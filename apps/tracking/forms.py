from django import forms
from .models import TrackingConfiguration


class TrackingConfigurationForm(forms.ModelForm):
    class Meta:
        model = TrackingConfiguration
        fields = ("par", "timeframe")
        widgets = {
            "par": forms.TextInput(attrs={"class": "form-control"}),
            "timeframe": forms.Select(
                choices=TrackingConfiguration.TIMEFRAME_CHOICES,
                attrs={"class": "form-control"},
            ),
        }

    def clean_par(self):
        """
        Clean the par field by uppercasing it.
        """
        par = self.cleaned_data.get("par")
        return par.upper() if par else par
