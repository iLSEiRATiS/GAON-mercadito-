import requests
from django.conf import settings


def enviar_a_telegram(texto: str):
    """
    Envía un mensaje de texto simple a tu chat/bot de Telegram.
    Usa TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID desde settings.
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        # Si no está configurado, no rompemos la API, simplemente salimos.
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": texto,
    }
    try:
        requests.post(url, data=data, timeout=10)
    except Exception:
        # Podés loguear el error si querés
        pass
