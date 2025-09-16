# backtester/base_backtester.py
from abc import ABC, abstractmethod
from apps.strategies import get_strategy_class
from apps.tracking.models import Candle


class BaseBacktester(ABC):
    def __init__(self, backtest_config):
        self.config = backtest_config
        self.initial_balance = float(backtest_config.initial_balance)
        self.balance = self.initial_balance
        self.trades = []
        self.equity_curve = []

    def run(self):
        """Método principal para ejecutar el backtest"""
        candles = self.get_historical_data()
        if not candles:
            raise ValueError("No data for backtest period")

        strategy_class = get_strategy_class(self.config.strategy.strategy_type)
        strategy = strategy_class(self.config.parameters)

        data = strategy.prepare_data(candles)
        signals = strategy.generate_signals(data)

        self.execute_simulation(signals)
        return self.calculate_results()

    def get_historical_data(self):
        return Candle.objects.filter(
            tracking_configuration=self.config.tracking_config,
            time__range=(self.config.start_date, self.config.end_date),
        ).order_by("time")

    @abstractmethod
    def execute_simulation(self, signals):
        """Ejecutar simulación - debe ser implementado por subclases"""
        pass

    @abstractmethod
    def calculate_results(self):
        """Calcular resultados - debe ser implementado por subclases"""
        pass

    def record_trade(self, trade_info):
        """Registrar trade de forma estandarizada"""
        self.trades.append(trade_info)

    def calculate_basic_metrics(self):
        """Métricas básicas comunes a todos los backtesters"""
        final_equity = self.balance
        total_return = (
            (final_equity - self.initial_balance) / self.initial_balance
        ) * 100

        return {
            "final_balance": final_equity,
            "total_return": total_return,
            "total_trades": len(self.trades),
            "trades_data": self.trades,
        }
