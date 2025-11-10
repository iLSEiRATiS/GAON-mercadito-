from rest_framework import serializers
from foro.models import Comentario
from foro.models import Post


class ComentarioSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'autor', 'texto', 'creado_en']
        read_only_fields = ['id', 'autor', 'creado_en']


class PostSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'titulo', 'contenido', 'producto', 'autor', 'creado_en']
        read_only_fields = ['id', 'autor', 'creado_en']
