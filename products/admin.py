from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','precio','stock','activo','user','creado_en')
    list_filter = ('activo','creado_en')
    search_fields = ('nombre','descripcion','user__username')
