from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from products.models import Product
from foro.models import Comentario
from .serializers import ComentarioSerializer

from .serializers import PostSerializer
from foro.models import Post
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated


class ComentarioListCreateAPIView(ListCreateAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Comentario.objects.filter(producto_id=product_id).order_by('-creado_en')

    def perform_create(self, serializer):
        if not self.request.user or not self.request.user.is_authenticated:
            raise PermissionDenied('Authentication required to create comentarios')
        product = get_object_or_404(Product, id=self.kwargs.get('product_id'))
        serializer.save(autor=self.request.user, producto=product)


class ComentarioDestroyAPIView(DestroyAPIView):
    queryset = Comentario.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_staff or user.is_superuser or instance.autor_id == user.id):
            raise PermissionDenied('No tenés permiso para borrar este comentario')
        super().perform_destroy(instance)


class MinePostsListAPIView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(autor=self.request.user).order_by('-creado_en')


class MineComentariosListAPIView(ListAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comentario.objects.filter(autor=self.request.user).order_by('-creado_en')


class PostDestroyAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_staff or user.is_superuser or instance.autor_id == user.id):
            raise PermissionDenied('No tenés permiso para borrar este post')
        super().perform_destroy(instance)
