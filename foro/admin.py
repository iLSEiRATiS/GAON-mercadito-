from django.contrib import admin
from .models import Post, Comentario


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'autor', 'producto', 'creado_en')
    search_fields = ('titulo', 'contenido')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'autor', 'creado_en')
    search_fields = ('texto',)
