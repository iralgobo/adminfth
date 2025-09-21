from .base import BaseStrategy
from . import register_strategy
import talib


import pandas as pd


import talib
import pandas as pd
from apps.strategies.base import BaseStrategy


@register_strategy("moving_average_crossover_rsi")
class MovingAverageCrossoverRSI(BaseStrategy):
    def get_parameters_schema(self):
        parameters = self._get_parameters_schema_template()
        parameters["properties"] = {
            "short_window": {"type": "integer", "default": 20},
            "long_window": {"type": "integer", "default": 50},
            "rsi_period": {"type": "integer", "default": 14},
            "rsi_overbought": {"type": "integer", "default": 70},
            "rsi_oversold": {"type": "integer", "default": 30},
        }
        return parameters

    def generate_signals(self, data: pd.DataFrame):
        short = int(self.parameters.get("short_window", 20))
        long = int(self.parameters.get("long_window", 50))
        rsi_period = int(self.parameters.get("rsi_period", 14))
        rsi_overbought = int(self.parameters.get("rsi_overbought", 70))
        rsi_oversold = int(self.parameters.get("rsi_oversold", 30))

        # Moving averages
        data["sma_short"] = talib.SMA(data["close"], timeperiod=short)
        data["sma_long"] = talib.SMA(data["close"], timeperiod=long)

        # RSI
        data["rsi"] = talib.RSI(data["close"], timeperiod=rsi_period)

        # Señales
        data["signal"] = 0

        # Buy: cruce alcista + RSI por debajo de oversold
        buy_condition = (data["sma_short"] > data["sma_long"]) & (data["rsi"] < rsi_oversold)

        # Sell: cruce bajista + RSI por encima de overbought
        sell_condition = (data["sma_short"] < data["sma_long"]) & (data["rsi"] > rsi_overbought)

        data.loc[buy_condition, "signal"] = 1
        data.loc[sell_condition, "signal"] = -1

        # posición acumulada (para evitar operaciones duplicadas)
        #data["position"] = data["signal"].replace(to_replace=0, method="ffill").fillna(0)
        data["position"] = data["signal"].diff()
        return data
