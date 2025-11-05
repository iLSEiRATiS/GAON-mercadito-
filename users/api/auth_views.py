from django.contrib.auth import authenticate, login, get_user_model
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.db import transaction
import json

User = get_user_model()

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
        u = request.user
        return Response({
            "id": u.id,
            "username": u.username or "",
            "email": u.email or "",
            "first_name": u.first_name or "",
            "last_name": u.last_name or "",
            "telefono": getattr(u, "telefono", "") or "",
            "is_staff": bool(u.is_staff),
            "is_superuser": bool(u.is_superuser),
            "rol": "admin" if u.is_superuser else ("staff" if u.is_staff else "cliente"),
        })
    
from rest_framework import serializers

class ProfileUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)  # si tu modelo lo tiene

class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ProfileUpdateSerializer, responses={200: UserSerializer})
    def patch(self, request):
        ser = ProfileUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)

        u = request.user
        data = ser.validated_data

        # Sólo actualizamos campos permitidos (email NO)
        if 'username' in data:
            u.username = data['username']
        if 'first_name' in data:
            u.first_name = data['first_name']
        if 'last_name' in data:
            u.last_name = data['last_name']
        if 'telefono' in data and hasattr(u, 'telefono'):
            setattr(u, 'telefono', data['telefono'])

        u.save()
        return Response(UserSerializer(u).data)
    
@csrf_exempt  # importante: evitamos CSRF porque no usamos cookie de sesión aún
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_session(request):
    try:
        # Fuerza el backend para evitar "no backend authenticated"
        login(request, request.user, backend='django.contrib.auth.backends.ModelBackend')
        # A esta altura SessionMiddleware debió crear la cookie
        return Response({'ok': True})
    except Exception as e:
        # Devolvé JSON legible si algo truena
        return Response({'ok': False, 'error': str(e)}, status=500)
    
@csrf_exempt
@transaction.atomic
def signup(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    username   = (body.get("username")   or "").strip()
    email      = (body.get("email")      or "").strip().lower()
    password   = body.get("password")    or ""
    password2  = body.get("password2")   or ""
    first_name = (body.get("first_name") or "").strip()
    last_name  = (body.get("last_name")  or "").strip()

    # Validaciones
    if not first_name or not last_name:
        return JsonResponse({"detail": "Nombre y apellido son obligatorios"}, status=400)
    if not username:
        return JsonResponse({"detail": "Usuario es obligatorio"}, status=400)
    if not email:
        return JsonResponse({"detail": "Email es obligatorio"}, status=400)
    if not password or not password2:
        return JsonResponse({"detail": "Debés ingresar y repetir la contraseña"}, status=400)
    if password != password2:
        return JsonResponse({"detail": "Las contraseñas no coinciden"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"detail": "Ese usuario ya existe"}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"detail": "Ese email ya está registrado"}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )

    token, _ = Token.objects.get_or_create(user=user)
    return JsonResponse(
        {"id": user.id, "username": user.username, "email": user.email, "token": token.key},
        status=201
    )