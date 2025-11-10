from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["nombre", "precio", "stock", "descripcion", "imagen", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del producto"}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
