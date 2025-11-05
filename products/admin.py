from django.contrib import admin
from .models import Product, Category
from django.utils.text import slugify

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('slug',)               # 👈 ocultar slug en admin
    list_display = ('nombre',)
    search_fields = ('nombre',)

    def save_model(self, request, obj, form, change):
        base = slugify(obj.nombre) or "categoria"
        slug = base
        i = 2
        qs = Category.objects.exclude(pk=obj.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base}-{i}"
            i += 1
        obj.slug = slug
        super().save_model(request, obj, form, change)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','precio','stock','activo','category','user','creado_en')
    list_filter = ('activo','creado_en','category')
    search_fields = ('nombre','descripcion','user__username')
