from django.db import models
from django.conf import settings

class Mensaje(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensajes",
    )
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)

    class Meta:
        ordering = ["creado_en"]  # listado cronológico ascendente
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"

    def __str__(self):
        return f"[{self.creado_en:%Y-%m-%d %H:%M}] {self.user}: {self.texto[:40]}"
