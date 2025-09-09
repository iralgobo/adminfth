
from apps.strategies import get_strategy_class
from apps.tracking.models import Candle

class SimpleBacktester:
    def __init__(self, backtest_config):
        self.config = backtest_config
        self.initial_balance = float(backtest_config.initial_balance)
        self.balance = self.initial_balance
        self.position = 0
        self.trades = []
    
    def run(self):
       
        # Obtener datos
        candles = self.get_historical_data()
        if not candles:
            raise ValueError("No data for backtest period")        
        
        # Preparar estrategia
        strategy_class = get_strategy_class(self.config.strategy.strategy_type)
        strategy = strategy_class(self.config.parameters)
        
        # Generar señales
        data = strategy.prepare_data(candles)
        data_with_signals = strategy.generate_signals(data)
        # Ejecutar simulación
        self.execute_simulation(data_with_signals)
        
        # Calcular resultados
        return self.calculate_results()
    
    def get_historical_data(self):
        return Candle.objects.filter(
            tracking_configuration=self.config.tracking_config,
            time__range=(self.config.start_date, self.config.end_date)
        ).order_by('time')
    
    def execute_simulation(self, data):
       
        for index, row in data.iterrows():
            price = row['close']
            
            if 'position' in row and row['position'] == 1 and self.position == 0:
                # Buy signal
                self.execute_buy(price, index)
            elif 'position' in row and row['position'] == -1 and self.position > 0:
                # Sell signal
                self.execute_sell(price, index)
    
    def execute_buy(self, price, timestamp):
        if self.balance > 0:
            quantity = self.balance / price
            self.position = quantity
            self.balance = 0
            self.record_trade('BUY', price, quantity, timestamp)
    
    def execute_sell(self, price, timestamp):
        if self.position > 0:
            self.balance = self.position * price
            self.record_trade('SELL', price, self.position, timestamp)
            self.position = 0
    
    def record_trade(self, action, price, quantity, timestamp):
        trade = {
            'action': action,
            'price': price,
            'quantity': quantity,
            'timestamp': timestamp.isoformat(),
            'balance_after': self.balance
        }
        self.trades.append(trade)
    
    def calculate_results(self):
        final_equity = self.balance + (self.position * self.trades[-1]['price']) if self.trades else self.initial_balance
        total_return = ((final_equity - self.initial_balance) / self.initial_balance) * 100
        
        return {
            'final_balance': final_equity,
            'total_return': total_return,
            'total_trades': len(self.trades),
            'trades_data': self.trades
        }