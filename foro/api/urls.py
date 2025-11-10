from django.urls import path
from .views import (
    ComentarioListCreateAPIView,
    ComentarioDestroyAPIView,
    MinePostsListAPIView,
    PostDestroyAPIView,
)

from .views import MineComentariosListAPIView

app_name = 'foro_api'

urlpatterns = [
    # List/Create comentarios para un producto
    path('producto/<int:product_id>/comentarios/', ComentarioListCreateAPIView.as_view(), name='comentarios-producto'),

    # Borrar comentario (por id)
    path('comentarios/<int:pk>/', ComentarioDestroyAPIView.as_view(), name='comentario-destroy'),
    # Mis publicaciones
    path('mine/posts/', MinePostsListAPIView.as_view(), name='mine-posts'),
    path('mine/comentarios/', MineComentariosListAPIView.as_view(), name='mine-comentarios'),
    # Borrar post (API)
    path('posts/<int:pk>/', PostDestroyAPIView.as_view(), name='post-destroy'),
]
