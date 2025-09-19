from .base_backtester import BaseBacktester

class FuturesSimpleBacktester(BaseBacktester):
    def __init__(self, backtest_config):
        super().__init__(backtest_config)
        self.leverage = self.config.parameters.get('leverage', 1)
        self.position = 0  # + para long, - para short
        self.position_entry_price = 0
    
    def execute_simulation(self, signals):
        for _, signal in signals.iterrows():
            price = signal['close']
            
            # Lógica de trading de futuros
            if signal.get('position') == 1:
                # Señal de compra (long)
                if self.position <= 0:  # Cerrar short si existe o abrir long
                    self.execute_order(price, signal['time'], 'LONG')
            elif signal.get('position') == -1:
                # Señal de venta (short)
                if self.position >= 0:  # Cerrar long si existe o abrir short
                    self.execute_order(price, signal['time'], 'SHORT')
            elif signal.get('position') == 0:
                # Señal de cierre
                if self.position != 0:
                    self.execute_order(price, signal['time'], 'CLOSE')
    
    def execute_order(self, price, timestamp, order_type):
        """Ejecutar orden en futuros"""
        if order_type == 'CLOSE':
            self.close_position(price, timestamp)
        else:
            self.open_position(price, timestamp, order_type)
    
    def open_position(self, price, timestamp, position_type):
        """Abrir posición long o short"""
        # Cerrar posición existente si hay una
        if self.position != 0:
            self.close_position(price, timestamp)
        
        # Calcular tamaño de la posición con leverage
        position_size = (self.balance * self.leverage) / price
        
        if position_type == 'LONG':
            self.position = position_size
        else:  # SHORT
            self.position = -position_size
        
        self.position_entry_price = price
        
        self.record_trade({
            'action': 'OPEN',
            'price': price,
            'quantity': abs(self.position),
            'timestamp': timestamp,
            'type': 'futures',
            'position_type': position_type.lower(),
            'leverage': self.leverage,
            'reason': 'strategy_signal'
        })
    
    def close_position(self, price, timestamp):
        """Cerrar posición existente"""
        if self.position == 0:
            return
        
        # Calcular PnL
        if self.position > 0:  # Long position
            pnl = (price - self.position_entry_price) * abs(self.position)
        else:  # Short position
            pnl = (self.position_entry_price - price) * abs(self.position)
        
        self.balance += pnl
        pnl_pct = (pnl / (abs(self.position) * self.position_entry_price / self.leverage)) * 100
        
        position_type = 'long' if self.position > 0 else 'short'
        
        self.record_trade({
            'action': 'CLOSE',
            'price': price,
            'quantity': abs(self.position),
            'timestamp': timestamp,
            'balance_after': self.balance,
            'type': 'futures',
            'position_type': position_type,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'entry_price': self.position_entry_price,
            'reason': 'strategy_signal'
        })
        
        self.position = 0
        self.position_entry_price = 0
    
    def calculate_results(self):
        # Para futuros, el balance ya incluye todas las PnL realizadas
        return self.calculate_basic_metrics()