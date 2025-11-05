from rest_framework import serializers
from .models import Product, Category

class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "nombre", "slug"]

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    category = CategoryMiniSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True, allow_null=True, required=False
    )
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "user", "category", "category_id",
            "nombre", "precio", "descripcion",
            "imagen", "imagen_url", "stock", "activo",
            "creado_en",
        ]
        read_only_fields = ["id", "user", "creado_en"]

    def get_imagen_url(self, obj):
        req = self.context.get("request")
        if obj.imagen and hasattr(obj.imagen, "url"):
            return req.build_absolute_uri(obj.imagen.url) if req else obj.imagen.url
        return None

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
