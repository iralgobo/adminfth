# forms.py
from django import forms
from django_jsonform.forms.fields import JSONFormField


from apps.tracking.models import TrackingConfiguration
from apps.strategies.models import Strategy


class BacktestForm(forms.Form):
    strategy = forms.ModelChoiceField(
        label="Estrategia",
        required=True,
        empty_label="Seleccione una estrategia",
        queryset=Strategy.objects.all(),
        to_field_name='id'
    )
    backtester_type = forms.ChoiceField(label="Tester", required=True, choices=[
        ("spot_simple", "Simple Spot Backtester"),
        ("spot_risk", "Spot Risk Backtester"),
        ("futures_simple", "Futures Simple Backtester"),
        ("futures_risk", "Futures Risk Backtester"),
    ])
    tracking_config = forms.ChoiceField(
        label="Par y Timeframe", 
        required=True, 
        choices=[(obj.id, str(obj)) for obj in TrackingConfiguration.objects.all()]
    )

    initial_balance = forms.DecimalField(label="Balance Inicial (USDT)",
                                         required=True, initial=1000, decimal_places=2)

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    parametros = JSONFormField(
        label="Parametros",
        required=False,
       
    )
