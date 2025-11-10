from django.db import models
from django.conf import settings
from products.models import Product


class Post(models.Model):
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.autor}"


class Comentario(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario #{self.id} en {self.producto} por {self.autor}"
