# chatbot/api/views.py
import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-1.5-flash:generateContent"
)

class ChatGeminiView(APIView):
    """
    POST /api/chat/
    Body:
      {
        "messages": [
          {"role": "user", "content": "hola"},
          {"role": "assistant", "content": "¡hola!"},
          ...
        ]
      }
    Respuesta: { "reply": "texto del asistente" }
    """
    authentication_classes = []   # público para el TP (si querés, podés exigir auth)
    permission_classes = []

    def post(self, request):
        # 1) validar prompt
        messages = request.data.get("messages") or []
        last_user = ""
        for m in reversed(messages):
            if (m or {}).get("role") == "user":
                last_user = (m.get("content") or "").strip()
                break
        if not last_user:
            return Response({"detail": "Mensaje vacío"}, status=status.HTTP_400_BAD_REQUEST)

        # 2) obtener API key (seguro en servidor)
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            return Response({"detail": "Falta GEMINI_API_KEY en el servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3) armar historial mínimo (user → model → user ...). Para el TP alcanza con el último user
        #    Si querés enviar historial real, transformá 'messages' a la estructura 'contents' de Gemini.
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": last_user}]}
            ]
        }

        try:
            r = requests.post(
                f"{GEMINI_ENDPOINT}?key={api_key}",
                json=payload,
                timeout=25,
            )
        except requests.RequestException as e:
            return Response({"detail": f"Error de red al contactar Gemini: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        if not r.ok:
            # devolvemos información útil para debug
            return Response(
                {"detail": "Gemini devolvió error", "status": r.status_code, "body": r.text[:1000]},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = r.json()
        # extraer respuesta
        reply = ""
        try:
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            reply = ""
        if not reply:
            reply = "(No recibimos texto del modelo)"

        return Response({"reply": reply}, status=status.HTTP_200_OK)
