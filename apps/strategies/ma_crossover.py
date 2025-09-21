from .base import BaseStrategy
from . import register_strategy
import json
import talib


import pandas as pd

# Configurar para mostrar todas las filas
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)  # También todas las columnas
pd.set_option("display.width", None)  # Sin truncamiento horizontal


@register_strategy("moving_average_crossover")
class MovingAverageCrossover(BaseStrategy):
    def get_parameters_schema(self):
        parameters = self._get_parameters_schema_template()
        parameters["properties"] = {
            "short_window": {"type": "integer", "default": 20},
            "long_window": {"type": "integer", "default": 50},
        }
        return parameters

    def generate_signals(self, data: pd.DataFrame):
        short = int(self.parameters.get("short_window", "20"))
        long = int(self.parameters.get("long_window", "50"))

        data["sma_short"] = talib.SMA(data["close"], timeperiod=short)
        data["sma_long"] = talib.SMA(data["close"], timeperiod=long)

        data["signal"] = 0
        data["signal"] = (data["sma_short"] > data["sma_long"]).astype(int)
        data["position"] = data["signal"].diff()
        #data["position"] = data["signal"].replace(to_replace=0, method="ffill").fillna(0)

        return data
