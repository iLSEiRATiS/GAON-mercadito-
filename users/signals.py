# users/signals.py
from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from .forms import resolve_user_email

@receiver(user_logged_in)
def fill_user_email_on_login(sender, request, user, **kwargs):
    try:
        if not user.email:
            em = resolve_user_email(user)
            if em:
                user.email = em
                user.save(update_fields=["email"])
    except Exception:
        pass
