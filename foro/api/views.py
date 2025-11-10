from rest_framework import viewsets, generics, permissions
from rest_framework.exceptions import NotFound

from foro.models import Post, Comentario
from .serializers import PostSerializer, ComentarioSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "autor_id", None) == getattr(request.user, "id", None)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)


class ComentarioListCreate(generics.ListCreateAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return Comentario.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound("Post no encontrado")
        serializer.save(autor=self.request.user, post=post)


class ComentarioDestroy(generics.DestroyAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
