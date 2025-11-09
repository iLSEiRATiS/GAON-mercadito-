from django.contrib import admin
from .models import Mensaje

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "texto", "creado_en")
    list_filter = ("user", "creado_en")
    search_fields = ("texto", "user__username", "user__email")
    ordering = ("-creado_en",)
