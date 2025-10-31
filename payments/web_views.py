# payments/web_views.py
from django.shortcuts import render

def _clear_cart_session(request):
    """
    Limpia el carrito guardado en sesión sin depender de modelos.
    Soporta estructuras típicas: dict {id: qty}, list de items o dict con 'items'.
    """
    if "cart" in request.session:
        request.session["cart"] = {}
        request.session.modified = True
        return
    if "CART" in request.session:
        request.session["CART"] = {}
        request.session.modified = True
        return
    # fallback: por si lo guardaron como lista
    request.session["cart"] = {}
    request.session.modified = True

def payment_success(request):
    _clear_cart_session(request)  # limpiar carrito en éxito (opcional)
    ctx = {
        "payment_id": request.GET.get("payment_id"),
        "status": request.GET.get("status"),
        "merchant_order_id": request.GET.get("merchant_order_id"),
        "external_reference": request.GET.get("external_reference"),
        "preference_id": request.GET.get("preference_id"),
    }
    return render(request, "payments/success.html", ctx)

def payment_failure(request):
    ctx = {
        "payment_id": request.GET.get("payment_id"),
        "status": request.GET.get("status"),
        "merchant_order_id": request.GET.get("merchant_order_id"),
        "external_reference": request.GET.get("external_reference"),
        "preference_id": request.GET.get("preference_id"),
    }
    return render(request, "payments/failure.html", ctx)

def payment_pending(request):
    ctx = {
        "payment_id": request.GET.get("payment_id"),
        "status": request.GET.get("status"),
        "merchant_order_id": request.GET.get("merchant_order_id"),
        "external_reference": request.GET.get("external_reference"),
        "preference_id": request.GET.get("preference_id"),
    }
    return render(request, "payments/pending.html", ctx)