from django.contrib import admin
from .models import Presupuesto

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ("id", "producto", "email", "creado_en")
    search_fields = ("producto", "email")
