"""Middleware temporal para debug de CSRF.

Registra en la consola el valor de la cookie `csrftoken`, la cabecera Cookie y
el valor de `csrfmiddlewaretoken` recibido en POST, antes de que Django ejecute
la verificación CSRF (esto permite diagnosticar mismatch aunque CsrfViewMiddleware
bloquee la vista posteriormente).

IMPORTANTE: Esto es solo para depuración local. Eliminá este archivo y la
entrada en `MIDDLEWARE` cuando termines.
"""
from typing import Callable

class DebugCSRFMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        # Solo loguear en métodos POST para no ensuciar la consola con GETs
        try:
            if request.method == 'POST':
                print("[DBG-MW CSRF] Path:", request.path)
                print("[DBG-MW CSRF] request.COOKIES.get('csrftoken'):", request.COOKIES.get('csrftoken'))
                print("[DBG-MW CSRF] request.META.get('HTTP_COOKIE'):", request.META.get('HTTP_COOKIE'))
                # request.POST accede al body parseado; en multipart/form-data leerá campos
                try:
                    print("[DBG-MW CSRF] request.POST.get('csrfmiddlewaretoken'):", request.POST.get('csrfmiddlewaretoken'))
                except Exception:
                    print("[DBG-MW CSRF] request.POST no está disponible o falló al parsear")
        except Exception:
            import traceback; traceback.print_exc()

        return self.get_response(request)
