import ccxt
from django.utils import timezone
from .models import Candle


class ExchangeDataService:
    def __init__(self, exchange_id="bitunix"):
        self.exchange = getattr(ccxt, exchange_id)(
            {
                "enableRateLimit": True,
            }
        )

    def fetch_ohlcv(self, symbol, timeframe, since=None, limit=100):
        try:
            return self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        except Exception as e:
            print(f"Error fetching OHLCV: {e}")
            return []

    def save_candles(self, tracking_config, ohlcv_data):
        candles = []
        for ohlcv in ohlcv_data:
            timestamp, open_, high, low, close, volume = ohlcv
            candle = Candle(
                tracking_configuration=tracking_config,
                open=open_,
                high=high,
                low=low,
                close=close,
                volume=volume,
                timestamp=timestamp,
                time=timezone.datetime.fromtimestamp(timestamp / 1000),
            )
            candles.append(candle)

        Candle.objects.bulk_create(candles, ignore_conflicts=True)
        return len(candles)
