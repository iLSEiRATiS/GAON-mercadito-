# users/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
import re

def _username_from_email(email: str) -> str:
    # base: parte antes del @; si está vacía, fallback genérico
    base = (email or "").split("@")[0] or "user"
    # limpiar a formato username
    base = re.sub(r"[^a-zA-Z0-9._-]+", "", slugify(base, allow_unicode=False))
    return base or "user"

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Al crear/actualizar usuarios desde Google/GitHub:
    - Copiamos first_name, last_name y email del provider (si vienen).
    - NO pisamos username existente. Si el username está vacío, lo generamos a partir del email.
    """
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        email = data.get("email") or user.email
        first = data.get("first_name") or getattr(user, "first_name", "")
        last  = data.get("last_name") or getattr(user, "last_name", "")

        # Si no vinieron first/last, desglosamos 'name'
        if not first and not last:
            full = data.get("name") or ""
            parts = full.split()
            if parts:
                first = parts[0]
                last = " ".join(parts[1:]) if len(parts) > 1 else ""

        if email:
            user.email = email

        # Si el username no existe (o viene vacío), generarlo del email
        if not getattr(user, "username", ""):
            if email:
                user.username = _username_from_email(email)

        user.first_name = first or user.first_name
        user.last_name  = last or user.last_name
        return user
