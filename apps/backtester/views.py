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

class BacktestListView(LoginRequiredMixin, View):
    def get(self, request):
        backtests = BacktestConfig.objects.all().order_by('-created_at')
        return render(request, 'backtest/list.html', {
            'backtests': backtests,
            'page_title': 'Backtests'
        })

class BacktestCreateView(LoginRequiredMixin, View):
    def get(self, request):
        strategies = Strategy.objects.filter(is_active=True)
        tracking_configs = TrackingConfiguration.objects.all()
        
        return render(request, 'backtest/create.html', {
            'strategies': strategies,
            'tracking_configs': tracking_configs,
            'page_title': 'Nuevo Backtest'
        })
    
    def post(self, request):
        try:
            strategy_id = request.POST.get('strategy')
            tracking_config_id = request.POST.get('tracking_config')
            initial_balance = request.POST.get('initial_balance', 1000.0)
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            # Parse parameters from form
            parameters = {}
            for key in request.POST:
                if key.startswith('param_'):
                    param_name = key.replace('param_', '')
                    parameters[param_name] = request.POST[key]
            
            with transaction.atomic():
                backtest = BacktestConfig.objects.create(
                    strategy_id=strategy_id,
                    tracking_config_id=tracking_config_id,
                    initial_balance=initial_balance,
                    start_date=start_date,
                    end_date=end_date,
                    parameters=parameters
                )
                
                # Ejecutar backtest sincrónicamente
                backtester = SimpleBacktester(backtest)
                results = backtester.run()
                
                # Guardar resultados
                BacktestResult.objects.create(
                    config=backtest,
                    final_balance=results['final_balance'],
                    total_return=results['total_return'],
                    total_trades=results['total_trades'],
                    trades_data=results['trades_data']
                )
                
                backtest.status = 'completed'
                backtest.save()
            
            return redirect('backtest_detail', backtest_id=backtest.id)
            
        except Exception as e:
            return render(request, 'backtest/create.html', {
                'error': str(e),
                'strategies': Strategy.objects.filter(is_active=True),
                'tracking_configs': TrackingConfiguration.objects.all(),
                'page_title': 'Nuevo Backtest'
            })

class BacktestDetailView(LoginRequiredMixin, View):
    def get(self, request, backtest_id):
        backtest = get_object_or_404(BacktestConfig, id=backtest_id)
        result = get_object_or_404(BacktestResult, config=backtest)
        
        # Preparar datos para la gráfica
        equity_data = self.prepare_equity_data(result.trades_data)
        
        return render(request, 'backtest/detail.html', {
            'backtest': backtest,
            'result': result,
            'equity_data': json.dumps(equity_data),
            'page_title': f'Resultados: {backtest.strategy.name}'
        })
    
    def prepare_equity_data(self, trades_data):
        """Prepara datos para la gráfica de equity curve"""
        equity_data = []
        balance = 0
        
        for trade in trades_data:
            if trade['action'] == 'BUY':
                balance = trade['balance_after']
            elif trade['action'] == 'SELL':
                balance = trade['balance_after']
                equity_data.append({
                    'x': trade['timestamp'],
                    'y': balance
                })
        
        return equity_data

class BacktestDeleteView(LoginRequiredMixin, View):
    def post(self, request, backtest_id):
        backtest = get_object_or_404(BacktestConfig, id=backtest_id)
        backtest.delete()
        return redirect('backtest_list')
