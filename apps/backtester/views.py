from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from .models import BacktestConfig, BacktestResult
from apps.tracking.models import TrackingConfiguration
from apps.strategies.models import Strategy
import json
from .factory import create_backtester
from .forms import BacktestForm
from django_jsonform.widgets import JSONFormWidget
from apps.strategies import get_strategy_class
from django.http import JsonResponse

def convert_timestamps_in_trades(trades_list):
    """Convierte todos los Timestamps en la lista de trades a strings"""
    converted_trades = []
    for trade in trades_list:
        trade_copy = trade.copy()
        if "timestamp" in trade_copy and hasattr(trade_copy["timestamp"], "strftime"):
            trade_copy["timestamp"] = trade_copy["timestamp"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        converted_trades.append(trade_copy)
    return converted_trades


class BacktestListView(LoginRequiredMixin, View):
    def get(self, request):
        backtests = BacktestConfig.objects.all().order_by("-id")
        return render(
            request,
            "backtest/list.html",
            {"backtests": backtests, "page_title": "Backtests"},
        )


class BacktestCreateView(LoginRequiredMixin, View):
    def get(self, request):
        schema_parametros = {
            "type": "object",
            "title": "Parámetros de estrategia",
            "properties": {}
        }
        form = BacktestForm(request.POST or None, initial={"parametros": {}})
        form.fields['parametros'].widget = JSONFormWidget(schema=schema_parametros)

        return render(
            request,
            "backtest/create.html",
            {
                "form": form,
            },
        )

    def post(self, request):
        try:
            form = BacktestForm(request.POST)
           
            strategy_id = request.POST.get("strategy")
            backtester_type= request.POST.get("backtester_type")

            #strategy_instance = Strategy.objects.filter(id=strategy_id).first()
            #strategy_class = get_strategy_class(strategy_instance.strategy_type)
            
            #strategy = strategy_class()
         
            form_schema = get_property_schema(backtester_type, strategy_id)
            form.fields['parametros'].widget = JSONFormWidget(schema= form_schema)
            if  form.is_valid():
                
                tracking_config_id = form.cleaned_data["tracking_config"]    
                initial_balance = form.cleaned_data["initial_balance"]
                start_date = form.cleaned_data["start_date"]
                end_date = form.cleaned_data["end_date"]
                backtester_type = form.cleaned_data["backtester_type"]
                parameters = form.cleaned_data["parametros"]

                # Parse parameters from form
               

                with transaction.atomic():
                    backtest = BacktestConfig.objects.create(
                        strategy_id=strategy_id,
                        tracking_config_id=tracking_config_id,
                        initial_balance=initial_balance,
                        start_date=start_date,
                        end_date=end_date,
                        parameters=parameters,
                        backtester_type=backtester_type
                    )

                    # Ejecutar backtest sincrónicamente
                    #if  tester == 'SpotSimpleBacktester':
                    # backtester = SimpleBacktester(backtest)
                    #elif tester == 'SpotRiskBacktester':
                    #  backtester = SpotRiskBacktester(backtest)


                    backtester = create_backtester(backtest)
                    results = backtester.run()
                    

                    # Guardar resultados
                    BacktestResult.objects.create(
                        config=backtest,
                        final_balance=results["final_balance"],
                        total_return=results["total_return"],
                        total_trades=results["total_trades"],
                        trades_data=convert_timestamps_in_trades(results["trades_data"]),
                    )

                    backtest.status = "completed"
                    backtest.save()

                return redirect("backtest_detail", backtest_id=backtest.id)
            else:
                # ⚠️ IMPORTANTE: Retornar respuesta cuando el formulario NO es válido
                return render(
                    request,
                    "backtest/create.html",
                    {
                        "form": form,
                        "strategies": Strategy.objects.filter(is_active=True),
                        "tracking_configs": TrackingConfiguration.objects.all(),
                        "page_title": "Nuevo Backtest",
                    },
                )

        except Exception as e:
            return render(
                request,
                "backtest/create.html",
                {
                    "error": str(e),
                    "strategies": Strategy.objects.filter(is_active=True),
                    "tracking_configs": TrackingConfiguration.objects.all(),
                    "page_title": "Nuevo Backtest",
                },
            )
        



    

class BacktestDetailView(LoginRequiredMixin, View):
    def get(self, request, backtest_id):
        backtest = get_object_or_404(BacktestConfig, id=backtest_id)
        result = get_object_or_404(BacktestResult, config=backtest)

        # Preparar datos para la gráfica
        equity_data = self.prepare_equity_data(result.trades_data)

        return render(
            request,
            "backtest/detail.html",
            {
                "backtest": backtest,
                "result": result,
                "equity_data": json.dumps(equity_data),
                "page_title": f"Resultados: {backtest.strategy.name}",
            },
        )

    def prepare_equity_data(self, trades_data):
        """Prepara datos para la gráfica de equity curve"""
        equity_data = []
        balance = 0

        for trade in trades_data:
            if trade["action"] == "BUY":
                balance = trade["balance_after"]
            elif trade["action"] == "SELL":
                balance = trade["balance_after"]
                equity_data.append({"x": trade["timestamp"], "y": balance})

        return equity_data


class BacktestDeleteView(LoginRequiredMixin, View):
    def post(self, request, backtest_id):
        backtest = get_object_or_404(BacktestConfig, id=backtest_id)
        backtest.delete()
        return redirect("backtest_list")


def get_property_schema_view(request, backtest_type, strategy_id):  # Ahora recibe strategy_id como parámetro
 
    
    schema = get_property_schema(backtest_type, strategy_id)
    
    return JsonResponse(schema)


def get_property_schema( backtest_type, strategy_id):  # Ahora recibe strategy_id como parámetro

    # Debug: verificar qué devuelven las funciones
    strategy_schema = get_strategie_schema(strategy_id)
    backtester_schema = get_backtester_schema(backtest_type)
    
    
    schema = {
        "type": "object",
        "title": "Parametros",
        "properties": {
            "strategy": strategy_schema,
            "backtester": backtester_schema
        }
    }
    
    return schema

def get_strategie_schema(strategy_id):
    strategy_instance = Strategy.objects.filter(id=strategy_id).first()
    if not strategy_instance:
        raise ValueError('Strategy not found')
    
    strategy_class = get_strategy_class(strategy_instance.strategy_type)
    strategy = strategy_class()
    
    return strategy.get_parameters_schema()

def get_backtester_schema( backtest_type):  

    backtester = create_backtester({    
        "backtester_type": backtest_type})
    
    return backtester.get_parameters_schema()

    