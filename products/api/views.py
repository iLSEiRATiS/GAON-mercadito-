from django.db import models
from rest_framework import viewsets, permissions
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from products.models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == getattr(request.user, 'id', None)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.order_by('nombre')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    parameters=[
        OpenApiParameter(name='q', description='Buscar en nombre/descripcion', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='min_price', description='Precio mínimo', required=False, type=OpenApiTypes.NUMBER),
        OpenApiParameter(name='max_price', description='Precio máximo', required=False, type=OpenApiTypes.NUMBER),
        OpenApiParameter(name='category', description='Slug de categoría', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='in_stock', description='true/false', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='order', description='price_asc | price_desc | name | newest | oldest', required=False, type=OpenApiTypes.STR),
    ]
)
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        request: Request = self.request
        qs = Product.objects.filter(activo=True)

        q = request.query_params.get('q') or ''
        if q:
            qs = qs.filter(models.Q(nombre__icontains=q) | models.Q(descripcion__icontains=q))

        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            qs = qs.filter(precio__gte=min_price)
        if max_price:
            qs = qs.filter(precio__lte=max_price)

        cat = request.query_params.get('category') or ''
        if cat:
            qs = qs.filter(category__slug=cat)

        in_stock = (request.query_params.get('in_stock') or '').lower()
        if in_stock == 'true':
            qs = qs.filter(stock__gt=0)
        elif in_stock == 'false':
            qs = qs.filter(stock__lte=0)

        order = (request.query_params.get('order') or '').lower()
        if order == 'price_asc':
            qs = qs.order_by('precio', '-creado_en')
        elif order == 'price_desc':
            qs = qs.order_by('-precio', '-creado_en')
        elif order == 'name':
            qs = qs.order_by('nombre', '-creado_en')
        elif order == 'oldest':
            qs = qs.order_by('creado_en')
        else:
            qs = qs.order_by('-creado_en')

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
