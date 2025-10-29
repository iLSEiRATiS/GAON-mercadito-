from rest_framework import serializers
from users.models import CustomUser
from .serializers import UserSerializer

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username','email','password','first_name','last_name','telefono','rol']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserSerializer()

class LogoutResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
