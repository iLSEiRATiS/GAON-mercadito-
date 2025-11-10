from django.contrib import admin
from .models import Post, Comentario, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")
    prepopulated_fields = {"slug": ("nombre",)}
    search_fields = ("nombre",)  # ← requerido para autocomplete_fields en PostAdmin


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "categoria", "is_pinned", "is_active", "creado_en")
    list_filter = ("is_active", "is_pinned", "categoria")
    search_fields = ("titulo", "contenido", "autor__username")
    prepopulated_fields = {"slug": ("titulo",)}
    autocomplete_fields = ("categoria",)  # usa CategoryAdmin.search_fields
    ordering = ("-is_pinned", "-creado_en")


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("post", "autor", "creado_en")
    search_fields = ("texto", "autor__username", "post__titulo")
