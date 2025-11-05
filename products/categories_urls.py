from django.urls import path
from products import web_views  # reutilizamos las vistas

urlpatterns = [
    path("manage/", web_views.category_list, name="category-manage"),
    path("manage/new/", web_views.category_create, name="category-create"),
    path("manage/<int:pk>/edit/", web_views.category_update, name="category-edit"),
    path("manage/<int:pk>/delete/", web_views.category_delete, name="category-delete"),
]
