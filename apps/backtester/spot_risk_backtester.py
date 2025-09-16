# backtester/spot_risk_backtester.py
from .spot_simple_backtester import SpotSimpleBacktester
from .risk_management import RiskManager
import pandas as pd


class SpotRiskBacktester(SpotSimpleBacktester):
    def __init__(self, backtest_config):
        super().__init__(backtest_config)
        self.risk_manager = None
        self.current_trade_info = None

    def execute_simulation(self, signals: pd.DataFrame):
        for _, signal in signals.iterrows():
            price = signal["close"]

            # Verificar condiciones de riesgo si tenemos posición
            if self.position > 0 and self.risk_manager:
                exit_reason = self.risk_manager.check_exit_conditions(price)
                if exit_reason:
                    self.execute_sell(price, signal["time"], exit_reason)
                    continue

            # Lógica normal de estrategia
            if signal.get("position") == 1 and self.position == 0:
                time = signal["time"]
                self.execute_buy_with_risk(price, time, signal)
            elif signal.get("position") == -1 and self.position > 0:
                time = signal["time"]
                self.execute_sell(price, time, "strategy_signal")

    def execute_buy_with_risk(self, price, timestamp, signal):
        """Ejecutar compra con configuración de riesgo"""
        if self.balance > 0:
            quantity = self.balance / price
            self.position = quantity
            self.balance = 0

            # Configurar gestión de riesgos
            self.setup_risk_management(price)

            self.record_trade(
                {
                    "action": "BUY",
                    "price": price,
                    "quantity": quantity,
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "balance_after": self.balance,
                    "type": "spot",
                    "reason": "strategy_signal",
                    "stop_loss": self.risk_manager.stop_loss_price,
                    "take_profit": self.risk_manager.take_profit_price,
                }
            )

    def setup_risk_management(self, entry_price):
        """Configurar parámetros de riesgo"""
        stop_loss_pct = self.config.parameters.get("stop_loss_pct", 0.02)
        take_profit_pct = self.config.parameters.get("take_profit_pct", 0.04)
        trailing_stop = self.config.parameters.get("trailing_stop", False)

        self.risk_manager = RiskManager(
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            trailing_stop=trailing_stop,
        )
        self.risk_manager.set_entry_conditions(entry_price)

        self.current_trade_info = {
            "entry_price": entry_price,
            "stop_loss": self.risk_manager.stop_loss_price,
            "take_profit": self.risk_manager.take_profit_price,
        }

    def execute_sell(self, price, timestamp, reason="strategy_signal"):
        """Ejecutar venta con razón específica"""
        if self.position > 0:
            # Calcular PnL
            entry_price = (
                self.current_trade_info["entry_price"]
                if self.current_trade_info
                else price
            )
            pnl_pct = ((price - entry_price) / entry_price) * 100

            self.balance = self.position * price

            self.record_trade(
                {
                    "action": "SELL",
                    "price": price,
                    "quantity": self.position,
                    "timestamp": timestamp,
                    "balance_after": self.balance,
                    "type": "spot",
                    "reason": reason,
                    "pnl_pct": pnl_pct,
                    "entry_price": entry_price,
                }
            )

            self.position = 0
            self.risk_manager = None
            self.current_trade_info = None
