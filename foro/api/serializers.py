from rest_framework import serializers
from foro.models import Post, Comentario


class ComentarioSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comentario
        fields = ["id", "post", "autor", "texto", "creado_en"]
        read_only_fields = ["autor", "creado_en", "post"]


class PostSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)
    comentarios_count = serializers.IntegerField(source="comentarios.count", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "titulo",
            "contenido",
            "autor",
            "creado_en",
            "actualizado_en",
            "comentarios_count",
        ]
        read_only_fields = ["autor", "creado_en", "actualizado_en", "comentarios_count"]
