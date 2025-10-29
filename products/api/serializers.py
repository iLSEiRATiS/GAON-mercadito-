from rest_framework import serializers
from products.models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','nombre','slug']

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    imagen = serializers.ImageField(required=False, allow_null=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True)

    class Meta:
        model = Product
        fields = ['id','user','category','category_id','nombre','precio','descripcion','imagen','stock','activo','creado_en']
        read_only_fields = ['id','user','creado_en']
