from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PostViewSet,
    ComentarioListCreate,
    ComentarioDestroy,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="foro-posts")

urlpatterns = router.urls + [
    path("posts/<int:post_id>/comments/", ComentarioListCreate.as_view(), name="foro-comments-list-create"),
    path("comments/<int:pk>/", ComentarioDestroy.as_view(), name="foro-comment-destroy"),
]
