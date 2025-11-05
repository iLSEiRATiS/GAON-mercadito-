from django import forms
from django.utils.text import slugify
from .models import Product, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["nombre"]           # no mostramos slug
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Indumentaria"}),
        }

    def save(self, commit=True):
        """
        Autogenera/actualiza slug en base al nombre, manteniéndolo único.
        """
        obj = super().save(commit=False)
        base = slugify(obj.nombre or "")
        if not base:
            base = "categoria"

        slug = base
        i = 1
        while Category.objects.exclude(pk=obj.pk).filter(slug=slug).exists():
            i += 1
            slug = f"{base}-{i}"

        obj.slug = slug
        if commit:
            obj.save()
        return obj


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["nombre", "category", "precio", "stock", "descripcion", "imagen", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del producto"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
