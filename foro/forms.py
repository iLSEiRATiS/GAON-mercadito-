from django import forms
from .models import Comentario

class ComentarioForm(forms.ModelForm):
    # campo honeypot invisible para bots
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"style": "display:none"}))

    class Meta:
        model = Comentario
        fields = ["texto"]
        widgets = {
            "texto": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Escribí tu comentario..."
            })
        }

    def clean(self):
        data = super().clean()
        if data.get("website"):  # si lo llenan, es bot
            raise forms.ValidationError("Detección anti-spam.")
        return data
