from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, authentication
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema
from .auth_serializers import (
    SignupSerializer,
    LoginSerializer,
    TokenResponseSerializer,
    LogoutResponseSerializer
)
from .serializers import UserSerializer

class SignupView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=SignupSerializer,
        responses={201: TokenResponseSerializer, 400: dict}
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            data = TokenResponseSerializer({'token': token.key, 'user': UserSerializer(user).data}).data
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenLoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: TokenResponseSerializer, 400: dict}
    )
    def post(self, request):
        login_ser = LoginSerializer(data=request.data)
        if not login_ser.is_valid():
            return Response(login_ser.errors, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(
            username=login_ser.validated_data['username'],
            password=login_ser.validated_data['password']
        )
        if not user:
            return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        data = TokenResponseSerializer({'token': token.key, 'user': UserSerializer(user).data}).data
        return Response(data)

class TokenLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    @extend_schema(
        request=None,
        responses={200: LogoutResponseSerializer}
    )
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'Logout OK'})

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: UserSerializer}
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)
