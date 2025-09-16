from django.db import models
from config.models import TimeStampedModel
from apps.strategies import get_available_strategies


class Strategy(TimeStampedModel):
    STRATEGY_CHOICES = [
        ("moving_average_crossover", "Moving Average Crossover"),
        # Añadir más estrategias aquí según se vayan registrando
    ]

    name = models.CharField(max_length=100)
    strategy_type = models.CharField(max_length=50, choices=STRATEGY_CHOICES)
    parameters = models.JSONField(default=dict)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_strategy_type_display()})"

    def save(self, *args, **kwargs):
        # Actualizar las choices disponibles dinámicamente

        self._meta.get_field("strategy_type").choices = [
            (strategy, strategy.replace("_", " ").title())
            for strategy in get_available_strategies()
        ]
        super().save(*args, **kwargs)
