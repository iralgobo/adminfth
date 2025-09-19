from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db import transaction
from .models import BacktestConfig, BacktestResult
from .engine import SimpleBacktester
from apps.tracking.models import TrackingConfiguration
from apps.strategies.models import Strategy
import json
from .spot_risk_backtester import SpotRiskBacktester
from .factory import create_backtester



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
        strategies = Strategy.objects.filter(is_active=True)
        tracking_configs = TrackingConfiguration.objects.all()
        testers = [
            {"id":'spot_simple', "name":"Simple Spot Backtester"},
            {"id":'spot_risk', "name":"Spot Risk Backtester"},
            {"id":'futures_simple', "name":"Futures Simple Backtester"},
            {"id":'futures_risk', "name":"Futures Risk Backtester"},
            ]

        return render(
            request,
            "backtest/create.html",
            {
                "strategies": strategies,
                "tracking_configs": tracking_configs,
                "page_title": "Nuevo Backtest",
                "testers":testers,
            },
        )

    def post(self, request):
        try:
            strategy_id = request.POST.get("strategy")
            tracking_config_id = request.POST.get("tracking_config")
            initial_balance = request.POST.get("initial_balance", 1000.0)
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            backtester_type=request.POST.get('backtester_type', 'spot_simple')

            # Parse parameters from form
            parameters = {
                "short_window": int(request.POST.get("param_short_window", 20)),
                "long_window": int(request.POST.get("param_long_window", 50)),
                "stop_loss_pct": float(request.POST.get("param_stop_loss", 0.02)),
                "take_profit_pct": float(request.POST.get("param_take_profit", 0.04)),
                "trailing_stop": bool(request.POST.get("param_trailing", False)),
            }

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
