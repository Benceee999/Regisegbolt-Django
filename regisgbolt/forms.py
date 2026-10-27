from django import forms
from .models import Velemeny


class VelemenyForm(forms.ModelForm):
    class Meta:
        model = Velemeny
        fields = ["nev", "email", "uzenet"]
        labels = {
            "nev": "Név",
            "email": "E-mail cím (nem kötelező)",
            "uzenet": "Véleményed",
        }
        widgets = {
            "nev": forms.TextInput(attrs={"class": "form-control", "placeholder": "Neved"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "E-mail címed (opcionális)"}),
            "uzenet": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Írd le a véleményed..."}),
        }
