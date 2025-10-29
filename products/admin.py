from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','slug')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','precio','stock','activo','category','user','creado_en')
    list_filter = ('activo','creado_en','category')
    search_fields = ('nombre','descripcion','user__username')
