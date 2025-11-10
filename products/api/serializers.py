from rest_framework import serializers
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    imagen = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = ['id','user','nombre','precio','descripcion','imagen','stock','activo','creado_en']
        read_only_fields = ['id','user','creado_en']
