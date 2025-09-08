from django.db import models

# Create your models here.
from config.models import TimeStampedModel
from apps.tracking.models import TrackingConfiguration
from apps.strategies.models import Strategy

class BacktestConfig(TimeStampedModel):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    tracking_config = models.ForeignKey(TrackingConfiguration, on_delete=models.CASCADE)
    initial_balance = models.DecimalField(max_digits=20, decimal_places=8, default=1000.0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    parameters = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])

class BacktestResult(TimeStampedModel):
    config = models.OneToOneField(BacktestConfig, on_delete=models.CASCADE)
    final_balance = models.DecimalField(max_digits=20, decimal_places=8)
    total_return = models.DecimalField(max_digits=10, decimal_places=2)
    total_trades = models.IntegerField()
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    trades_data = models.JSONField(default=list)