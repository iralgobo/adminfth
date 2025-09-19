# backtester/futures_risk_backtester.py
from .futures_simple_backtester import FuturesSimpleBacktester
from .risk_management import FuturesRiskManager

class FuturesRiskBacktester(FuturesSimpleBacktester):
    def __init__(self, backtest_config):
        super().__init__(backtest_config)
        self.risk_manager = None
    
    def execute_simulation(self, signals):
        for _, signal in signals.iterrows():
            price = signal['close']
            
            # Verificar condiciones de riesgo si tenemos posición
            if self.position != 0 and self.risk_manager:
                exit_reason = self.risk_manager.check_exit_conditions(price, self.position)
                if exit_reason:
                    self.close_position(price, signal['time'], exit_reason)
                    continue
            
            # Lógica normal de estrategia
            if signal.get('position') == 1 and self.position <= 0:
                self.open_position_with_risk(price, signal['time'], 'LONG', signal)
            elif signal.get('position') == -1 and self.position >= 0:
                self.open_position_with_risk(price, signal['time'], 'SHORT', signal)
            elif signal.get('position') == 0 and self.position != 0:
                self.close_position(price, signal['time'], 'strategy_signal')
    
    def open_position_with_risk(self, price, timestamp, position_type, signal):
        """Abrir posición con gestión de riesgos"""
        if self.position != 0:
            self.close_position(price, timestamp, 'switch_position')
        
        # Configurar gestión de riesgos
        self.setup_risk_management(price, position_type)
        
        # Abrir posición
        position_size = (self.balance * self.leverage) / price
        
        if position_type == 'LONG':
            self.position = position_size
        else:
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
            'reason': 'strategy_signal',
            'stop_loss': self.risk_manager.stop_loss_price,
            'take_profit': self.risk_manager.take_profit_price
        })
    
    def setup_risk_management(self, entry_price, position_type):
        """Configurar risk manager para futuros"""
        stop_loss_pct = self.config.parameters.get('stop_loss_pct', 0.02)
        take_profit_pct = self.config.parameters.get('take_profit_pct', 0.04)
        trailing_stop = self.config.parameters.get('trailing_stop', False)
        
        self.risk_manager = FuturesRiskManager(
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            trailing_stop=trailing_stop,
            position_type=position_type
        )
        self.risk_manager.set_entry_conditions(entry_price)
    
    def close_position(self, price, timestamp, reason='strategy_signal'):
        """Cerrar posición con razón específica"""
        if self.position == 0:
            return
        
        # Calcular PnL
        if self.position > 0:  # Long
            pnl = (price - self.position_entry_price) * abs(self.position)
        else:  # Short
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
            'reason': reason
        })
        
        self.position = 0
        self.position_entry_price = 0
        self.risk_manager = None