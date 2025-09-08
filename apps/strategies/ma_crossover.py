from .base import BaseStrategy
from . import register_strategy
import json
import talib

        
import pandas as pd   
# Configurar para mostrar todas las filas
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)  # También todas las columnas    
pd.set_option('display.width', None)  # Sin truncamiento horizontal 

@register_strategy('moving_average_crossover')
class MovingAverageCrossover(BaseStrategy):
    def generate_signals(self, data):
        
       
        
        short = self.parameters.get('short_window', 20)
        long = self.parameters.get('long_window', 50)
        
        data['sma_short'] = data['close'].rolling(window=short).mean()
        data['sma_long'] = data['close'].rolling(window=long).mean()
        
        data['signal'] = 0
        data['signal'] = (data['sma_short'] > data['sma_long']).astype(int)
        data['position'] = data['signal'].diff()        

        return data