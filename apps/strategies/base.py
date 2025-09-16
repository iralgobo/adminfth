from abc import ABC, abstractmethod
import pandas as pd


class BaseStrategy(ABC):
    def __init__(self, parameters=None):
        self.parameters = parameters or {}

    @abstractmethod
    def generate_signals(self, data):
        pass

    def prepare_data(self, candles_queryset):
        data = []
        for candle in candles_queryset:
            data.append(
                {
                    "index_time": candle.time,
                    "time": candle.time,
                    "open": float(candle.open),
                    "high": float(candle.high),
                    "low": float(candle.low),
                    "close": float(candle.close),
                    "volume": float(candle.quoteVol),
                }
            )
        return pd.DataFrame(data).set_index("index_time")
