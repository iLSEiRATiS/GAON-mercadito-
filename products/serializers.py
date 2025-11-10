from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "user",
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
