from django.urls import path
from . import web_views

urlpatterns = [
    # públicas (tienda)
    path("", web_views.product_list, name="products-list"),
    path("<int:pk>/", web_views.product_detail, name="product-detail"),

    # compatibilidad: alta simple
    path("create/", web_views.product_create, name="product-create-simple"),

    # gestión de productos
    path("manage/", web_views.my_products, name="product-manage"),
    path("manage/mine/", web_views.product_manage_mine, name="products-mine"),
    path("manage/new/", web_views.product_create, name="product-create"),
    path("manage/<int:pk>/edit/", web_views.product_manage_edit, name="product-edit"),
    path("manage/<int:pk>/delete/", web_views.product_delete, name="product-delete"),
]

