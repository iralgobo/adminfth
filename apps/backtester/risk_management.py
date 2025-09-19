# backtester/risk_management.py
class RiskManager:
    def __init__(self, stop_loss_pct=0.02, take_profit_pct=0.04, trailing_stop=False):
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trailing_stop = trailing_stop
        self.entry_price = 0
        self.stop_loss_price = 0
        self.take_profit_price = 0
        self.trailing_peak = 0

    def set_entry_conditions(self, entry_price):
        """Configurar precios de stop loss y take profit al entrar en una posición"""
        self.entry_price = entry_price
        self.stop_loss_price = entry_price * (1 - self.stop_loss_pct)
        self.take_profit_price = entry_price * (1 + self.take_profit_pct)
        self.trailing_peak = entry_price

    def check_exit_conditions(self, current_price):
        """Verificar si se cumplen las condiciones de salida"""
        # Check stop loss
        if current_price <= self.stop_loss_price:
            return "stop_loss"

        # Check take profit
        if current_price >= self.take_profit_price:
            return "take_profit"

        # Trailing stop logic
        if self.trailing_stop:
            if current_price > self.trailing_peak:
                self.trailing_peak = current_price
                # Update trailing stop
                self.stop_loss_price = self.trailing_peak * (1 - self.stop_loss_pct)

            if current_price <= self.stop_loss_price:
                return "trailing_stop"

        return None

    def update_trailing_stop(self, current_price):
        """Actualizar trailing stop si está habilitado"""
        if self.trailing_stop and current_price > self.trailing_peak:
            self.trailing_peak = current_price
            self.stop_loss_price = self.trailing_peak * (1 - self.stop_loss_pct)

class FuturesRiskManager:
    def __init__(self, stop_loss_pct=0.02, take_profit_pct=0.04, 
                 trailing_stop=False, position_type='LONG'):
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trailing_stop = trailing_stop
        self.position_type = position_type
        self.entry_price = 0
        self.stop_loss_price = 0
        self.take_profit_price = 0
        self.trailing_peak = 0 if position_type == 'LONG' else float('inf')
    
    def set_entry_conditions(self, entry_price):
        self.entry_price = entry_price
        
        if self.position_type == 'LONG':
            self.stop_loss_price = entry_price * (1 - self.stop_loss_pct)
            self.take_profit_price = entry_price * (1 + self.take_profit_pct)
            self.trailing_peak = entry_price
        else:  # SHORT
            self.stop_loss_price = entry_price * (1 + self.stop_loss_pct)
            self.take_profit_price = entry_price * (1 - self.take_profit_pct)
            self.trailing_peak = entry_price
    
    def check_exit_conditions(self, current_price, current_position):
        """Verificar condiciones de salida para futuros"""
        if self.position_type == 'LONG':
            # Check stop loss (precio baja demasiado)
            if current_price <= self.stop_loss_price:
                return 'stop_loss'
            
            # Check take profit (precio sube suficiente)
            if current_price >= self.take_profit_price:
                return 'take_profit'
            
            # Trailing stop para long
            if self.trailing_stop:
                if current_price > self.trailing_peak:
                    self.trailing_peak = current_price
                    self.stop_loss_price = self.trailing_peak * (1 - self.stop_loss_pct)
                
                if current_price <= self.stop_loss_price:
                    return 'trailing_stop'
        
        else:  # SHORT
            # Check stop loss (precio sube demasiado)
            if current_price >= self.stop_loss_price:
                return 'stop_loss'
            
            # Check take profit (precio baja suficiente)
            if current_price <= self.take_profit_price:
                return 'take_profit'
            
            # Trailing stop para short
            if self.trailing_stop:
                if current_price < self.trailing_peak:
                    self.trailing_peak = current_price
                    self.stop_loss_price = self.trailing_peak * (1 + self.stop_loss_pct)
                
                if current_price >= self.stop_loss_price:
                    return 'trailing_stop'
        
        return None