from django.urls import path
from . import web_views

app_name = "foro"

urlpatterns = [
    path("", web_views.ForoListView.as_view(), name="list"),
    path("<int:pk>/", web_views.foro_detail, name="detail"),                # compatibilidad vieja
    path("<slug:slug>/", web_views.foro_detail, name="detail-slug"),       # URLs SEO nuevas
]
