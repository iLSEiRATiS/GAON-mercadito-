from django.conf import settings
from django.contrib import auth
from django.utils import timezone


class AutoLogoutMiddleware:
    """Middleware que cierra la sesión del usuario tras un periodo de inactividad.

    Funcionamiento:
    - Si el usuario está autenticado, se guarda en session['last_activity'] la marca temporal (timestamp).
    - Si la diferencia entre ahora y last_activity supera el timeout (AUTO_LOGOUT_DELAY o SESSION_COOKIE_AGE),
      se procede a hacer logout(request) y se limpia la sesión.

    Configuración:
    - AUTO_LOGOUT_DELAY (segundos) en settings.py para customizar. Si no está, se usa SESSION_COOKIE_AGE.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, "AUTO_LOGOUT_DELAY", None) or getattr(settings, "SESSION_COOKIE_AGE", 1800)

    def __call__(self, request):
        try:
            if request.user.is_authenticated:
                now_ts = int(timezone.now().timestamp())
                last = request.session.get("last_activity")
                if last:
                    try:
                        last = int(last)
                    except Exception:
                        last = None
                # Si hay última actividad y superó el timeout, cerrar sesión
                if last and (now_ts - last) > int(self.timeout):
                    auth.logout(request)
                    # limpiar la sesión (opcional)
                    try:
                        request.session.flush()
                    except Exception:
                        for k in list(request.session.keys()):
                            try:
                                del request.session[k]
                            except Exception:
                                pass
                else:
                    # actualizar último timestamp
                    request.session["last_activity"] = now_ts
        except Exception:
            # no romper la app si algo falla en la middleware
            pass

        response = self.get_response(request)
        return response
