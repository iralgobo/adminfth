from django.db import models


# Create your models here.
class TrackingConfiguration(models.Model):
    """
    Represents a tracking configuration for a given par and timeframe
    """

    TIMEFRAME_CHOICES = [
        ("5m", "5m"),
        ("15m", "15m"),
        ("30m", "30m"),
        ("1h", "1h"),
        ("2h", "2h"),
        ("4h", "4h"),
        ("6h", "6h"),
        ("8h", "8h"),
        ("1d", "1d"),
    ]

    par = models.CharField(max_length=10)
    timeframe = models.CharField(max_length=10, choices=TIMEFRAME_CHOICES)

    class Meta:
        unique_together = ("par", "timeframe")

    def __str__(self):
        return f"{self.par} - {self.timeframe}"


class Candle(models.Model):
    """
    Represents a candle with open, close, high, low prices and volumes
    """

    tracking_configuration = models.ForeignKey(
        TrackingConfiguration, on_delete=models.RESTRICT
    )

    open = models.DecimalField(max_digits=20, decimal_places=8)
    close = models.DecimalField(max_digits=20, decimal_places=8)
    high = models.DecimalField(max_digits=20, decimal_places=8)
    low = models.DecimalField(max_digits=20, decimal_places=8)
    quoteVol = models.DecimalField(max_digits=20, decimal_places=8)
    baseVol = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.BigIntegerField()
    time = models.DateTimeField()

    class Meta:
        unique_together = ("tracking_configuration", "timestamp")

    def __str__(self):
        return f"Open: {self.open}, Close: {self.close}, High: {self.high}, Low: {self.low}"
