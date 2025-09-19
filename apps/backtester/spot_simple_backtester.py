# backtester/spot_simple_backtester.py
from .base_backtester import BaseBacktester


class SpotSimpleBacktester(BaseBacktester):
    def __init__(self, backtest_config):
        super().__init__(backtest_config)
        self.position = 0  # Cantidad de crypto holdeda

    def execute_simulation(self, signals):
        for _, signal in signals.iterrows():
            price = signal["close"]

            # Lógica básica de compra/venta
            if signal.get("position") == 1 and self.position == 0:
                self.execute_buy(price, signal["time"])
            elif signal.get("position") == -1 and self.position > 0:
                self.execute_sell(price, signal["time"])

    def execute_buy(self, price, timestamp):
        if self.balance > 0:
            quantity = self.balance / price
            self.position = quantity
            self.balance = 0

            self.record_trade(
                {
                    "action": "BUY",
                    "price": price,
                    "quantity": quantity,
                    "timestamp": timestamp,
                    "balance_after": self.balance,
                    "type": "spot",
                    "reason": "strategy_signal",
                }
            )

    def execute_sell(self, price, timestamp):
        if self.position > 0:
            self.balance = self.position * price
            self.record_trade(
                {
                    "action": "SELL",
                    "price": price,
                    "quantity": self.position,
                    "timestamp": timestamp,
                    "balance_after": self.balance,
                    "type": "spot",
                    "reason": "strategy_signal",
                }
            )
            self.position = 0

    def calculate_results(self):
        # Calcular equity final considerando posición abierta
        if self.position > 0 and self.trades:
            last_price = self.trades[-1]["price"]
            final_equity = self.balance + (self.position * last_price)
        else:
            final_equity = self.balance

        total_return = (
            (final_equity - self.initial_balance) / self.initial_balance
        ) * 100

        return {
            "final_balance": final_equity,
            "total_return": total_return,
            "total_trades": len(self.trades),
            "trades_data": self.trades,
            "open_position": self.position > 0,
        }
