from django.urls import path
from . import web_views

urlpatterns = [
    # públicas (tienda)
    path("", web_views.product_list, name="product-list"),
    path("<int:pk>/", web_views.product_detail, name="product-detail"),

    # alta simple / crear producto (usa la misma vista para /create/ y /manage/new/)
    path("create/", web_views.ProductCreateView.as_view(), name="product-create-simple"),
    path("manage/new/", web_views.ProductCreateView.as_view(), name="product-create-simple"),

    # gestión de productos
    path("manage/", web_views.ProductManageListView.as_view(), name="product-manage"),
    path("manage/mine/", web_views.MyProductsListView.as_view(), name="products-mine"),
    path("manage/<int:pk>/edit/", web_views.ProductUpdateView.as_view(), name="product-edit"),
    path("manage/<int:pk>/delete/", web_views.ProductDeleteView.as_view(), name="product-delete"),
]

