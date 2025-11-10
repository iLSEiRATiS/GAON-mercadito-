from django.urls import path
from .web_views import (
    foro_home,
    posts_list,
    post_create,
    post_detail,
    post_edit,
    post_delete,
    comentario_edit,
    comentario_delete,
)

app_name = 'foro'

urlpatterns = [
    path('', foro_home, name='home'),
    path('posts/', posts_list, name='posts'),
    path('create/', post_create, name='post-create'),
    path('post/<int:pk>/', post_detail, name='post-detail'),
    path('post/<int:pk>/edit/', post_edit, name='post-edit'),
    path('post/<int:pk>/delete/', post_delete, name='post-delete'),
    path('comentario/<int:pk>/edit/', comentario_edit, name='comentario-edit'),
    path('comentario/<int:pk>/delete/', comentario_delete, name='comentario-delete'),
]
