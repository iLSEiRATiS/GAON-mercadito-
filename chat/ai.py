import os
from django.conf import settings

try:
    import google.generativeai as genai
    from google.api_core.exceptions import NotFound, PermissionDenied, FailedPrecondition
except Exception:
    genai = None
    class NotFound(Exception): ...
    class PermissionDenied(Exception): ...
    class FailedPrecondition(Exception): ...


# Preferencias (orden de intención). No asumimos que existan: las verificamos con list_models.
PREFERRED_NAMES = [
    "gemini-1.5-flash-002",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-002",
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.0-pro-latest",
    "gemini-1.0-pro",
]


class GeminiUnavailable(Exception):
    """El SDK no está disponible o falta una configuración válida."""


def _configure():
    if genai is None:
        raise GeminiUnavailable(
            "Falta paquete 'google-generativeai'. Instalá con: pip install google-generativeai"
        )
    api_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise GeminiUnavailable("Falta GEMINI_API_KEY (en settings/env).")
    genai.configure(api_key=api_key)


def _normalize_name(n: str) -> str:
    """Acepta 'gemini-1.5-flash-002' o 'models/gemini-1.5-flash-002' y devuelve ambos formatos."""
    n = (n or "").strip()
    if not n:
        return ""
    if n.startswith("models/"):
        return n  # ya viene completo
    return f"models/{n}"


def _list_available_model_names():
    """
    Devuelve dos sets:
      - full_names: {'models/gemini-...'} que soportan generateContent
      - short_names: {'gemini-...'} pareados 1:1 con full_names
    """
    try:
        models = list(genai.list_models())
    except Exception as e:
        raise GeminiUnavailable(f"No se pudo listar modelos: {e}")

    full_names = set()
    short_names = set()
    for m in models:
        try:
            methods = set(getattr(m, "supported_generation_methods", []))
            if "generateContent" not in methods:
                continue
            name = getattr(m, "name", "")  # suele venir como 'models/gemini-...'
            if not name:
                continue
            full_names.add(name)
            if name.startswith("models/"):
                short_names.add(name.split("models/", 1)[1])
        except Exception:
            continue
    return full_names, short_names


def _pick_model_name():
    """
    Selecciona el nombre de modelo final a usar (formato 'models/...').
    Estrategia:
      1) Si hay GEMINI_MODEL y existe (full o short), úsalo.
      2) Sino, probá preferencias PREFERRED_NAMES si existen.
      3) Sino, tomá el primer disponible de list_models().
    """
    full, short = _list_available_model_names()

    # 1) .env / settings
    desired = getattr(settings, "GEMINI_MODEL", "") or os.getenv("GEMINI_MODEL", "")
    desired = desired.strip()
    if desired:
        full_candidate = _normalize_name(desired)     # forza 'models/...'
        short_candidate = desired                     # deja 'gemini-...'
        if full_candidate in full:
            return full_candidate
        if short_candidate in short:
            return _normalize_name(short_candidate)

    # 2) preferencias
    for name in PREFERRED_NAMES:
        if _normalize_name(name) in full or name in short:
            return _normalize_name(name)

    # 3) primer disponible
    if full:
        # elegimos algo estable: si hay alguno que empiece con models/gemini-, mejor
        for n in sorted(full):
            if n.startswith("models/gemini-"):
                return n
        # sino el primero alfabético
        return sorted(full)[0]

    raise GeminiUnavailable("No hay modelos disponibles con generateContent para esta key.")


def generate_reply(user_text: str) -> str:
    """
    Genera una respuesta breve usando un modelo disponible (descubierto dinámicamente).
    """
    _configure()

    prompt = (user_text or "").strip()
    if not prompt:
        return "Decime qué necesitás y te ayudo 🙂"

    system_preamble = (
        "Sos el asistente de GAON Mercadito. Respondé en español (Argentina), breve y útil. "
        "Si no sabés algo, sé transparente."
    )

    model_name = _pick_model_name()  # ← 'models/gemini-...'
    # Si querés loguear qué modelo se usó:
    # import logging; logging.getLogger(__name__).info("[CHAT] usando modelo: %s", model_name)

    try:
        model = genai.GenerativeModel(model_name, system_instruction=system_preamble)
        resp = model.generate_content(prompt)
        text = (getattr(resp, "text", None) or "").strip()
        if text:
            return text
        return "Estoy pensando… ¿podés reformular o darme un poco más de contexto?"
    except (NotFound, PermissionDenied, FailedPrecondition) as e:
        # Errores típicos: modelo no habilitado para la key/región o feature gated.
        raise GeminiUnavailable(f"Modelo no disponible: {e}") from e
    except Exception as e:
        raise GeminiUnavailable(f"Falla generando contenido: {e}") from e
