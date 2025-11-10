from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
import logging

from .models import Mensaje
from .serializers import MensajeSerializer
from .ai import generate_reply, GeminiUnavailable
from rest_framework.views import APIView
from rest_framework import permissions

log = logging.getLogger(__name__)


class ChatListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/chat/   -> lista los mensajes del usuario autenticado (orden cronológico)
    POST /api/chat/   -> crea un mensaje del usuario y, si hay GEMINI_API_KEY, guarda la respuesta del bot
                         Respuesta: el mensaje del usuario (compatibilidad); el bot se verá al recargar/listar.
    """
    serializer_class = MensajeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Mensaje.objects.filter(user=self.request.user).order_by("creado_en")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # 1) Validar & crear mensaje del usuario
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # setea user desde serializer.create(context)

        user_msg = serializer.instance

        # 2) Intentar generar y guardar la respuesta del bot (si hay key)
        try:
            reply_text = generate_reply(user_msg.texto)
            # Guardar la respuesta del asistente marcada como is_bot=True
            Mensaje.objects.create(user=request.user, texto=reply_text, is_bot=True)
        except GeminiUnavailable as e:
            # No explotes la request: guarda el del usuario, logueá el aviso
            log.warning("[CHAT] Gemini no disponible: %s", e)
        except Exception as e:
            log.exception("[CHAT] Error generando respuesta de Gemini: %s", e)

        # 3) Devolver SOLO el mensaje creado del usuario (compatibilidad con tu front)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class WelcomeView(APIView):
    """Crea un mensaje de bienvenida generado por el asistente para el usuario.

    POST /api/chat/welcome/ -> crea Mensaje(is_bot=True) y lo devuelve.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        welcome_text = "¡Hola! Soy el asistente de GAON. ¿En qué puedo ayudarte hoy?"
        msg = Mensaje.objects.create(user=request.user, texto=welcome_text, is_bot=True)
        ser = MensajeSerializer(msg, context={"request": request})
        return Response(ser.data, status=status.HTTP_201_CREATED)
