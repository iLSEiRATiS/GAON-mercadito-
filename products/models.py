from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        """
        Autogenera slug único en cada alta/edición si cambia el nombre.
        """
        base = slugify(self.nombre or "")
        if not base:
            base = "categoria"

        if not self.slug or slugify(self.nombre) != self.slug:
            slug = base
            i = 1
            while Category.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug

        super().save(*args, **kwargs)

# products/models.py

import os
from uuid import uuid4

def product_upload_to(instance, filename):
    """
    Compatible con la migración 0001 que hace:
    upload_to=products.models.product_upload_to

    Genera un nombre único en /media/products/<uuid>.<ext>
    """
    name, ext = os.path.splitext(filename)
    ext = (ext or "").lower() or ".jpg"
    return f"products/{uuid4().hex}{ext}"



class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to="products/", blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return self.nombre
