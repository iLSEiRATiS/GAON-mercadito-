# payments/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.utils import timezone
from products.models import Product
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import mercadopago
import json

def _session_cart_items(request):
    """
    Lee ítems del carrito desde la sesión.
    Soporta estructuras típicas:
      - dict {product_id: qty}
      - dict {'items': [{'product_id': id, 'qty': n}, ...]}
      - list [{'product_id': id, 'qty': n}, ...]
    Devuelve: [{'product': Product, 'qty': int}, ...]
    """
    cart = request.session.get("cart") or request.session.get("CART") or {}
    pairs = []

    if isinstance(cart, dict) and "items" not in cart:
        pairs = list(cart.items())
    elif isinstance(cart, dict) and isinstance(cart.get("items"), list):
        pairs = [(i.get("product_id"), i.get("qty")) for i in cart["items"]]
    elif isinstance(cart, list):
        pairs = [(i.get("product_id"), i.get("qty")) for i in cart]

    norm = []
    for pid, qty in pairs:
        try:
            pid = int(pid)
            qty = int(qty or 0)
        except Exception:
            continue
        if qty > 0:
            norm.append((pid, qty))

    if not norm:
        return []

    qs = Product.objects.filter(id__in=[pid for pid, _ in norm])
    pmap = {p.id: p for p in qs}

    items = []
    for pid, qty in norm:
        p = pmap.get(pid)
        if not p:
            continue
        items.append({"product": p, "qty": qty})
    return items


class CreatePreferenceView(APIView):
    """Crea una preferencia de MercadoPago con el contenido del carrito (desde body o sesión)."""
    def post(self, request):
        token = getattr(settings, "MP_ACCESS_TOKEN", "")
        if not token:
            return Response({"error": "MP_ACCESS_TOKEN no configurado."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- 1) Preferimos ítems enviados por el cliente (desde /api/cart/) ---
        client_items = request.data.get("items") or []
        items = []
        total_qty = 0

        if isinstance(client_items, list) and client_items:
            # Revalidamos con DB para precio/título (evita manipulación)
            try:
                ids = [int(x.get("product_id")) for x in client_items if x.get("product_id") is not None]
            except Exception:
                ids = []
            qs = Product.objects.filter(id__in=ids)
            pmap = {p.id: p for p in qs}

            for x in client_items:
                try:
                    pid = int(x.get("product_id"))
                    qty = int(x.get("qty") or 0)
                except Exception:
                    continue
                if qty <= 0 or pid not in pmap:
                    continue
                p = pmap[pid]
                title = getattr(p, "nombre", getattr(p, "name", "Producto"))
                price = getattr(p, "precio", getattr(p, "price", 0))
                unit_price = float(price)
                items.append({
                    "id": str(p.id),
                    "title": title,
                    "currency_id": "ARS",
                    "quantity": qty,
                    "unit_price": unit_price,
                })
                total_qty += qty

        # --- 2) Si no vinieron ítems, caemos al carrito en sesión (fallback) ---
        if not items:
            cart_items = _session_cart_items(request)  # función que ya te dejé
            for it in cart_items:
                p = it["product"]
                qty = int(it["qty"])
                title = getattr(p, "nombre", getattr(p, "name", "Producto"))
                price = getattr(p, "precio", getattr(p, "price", 0))
                unit_price = float(price)
                items.append({
                    "id": str(p.id),
                    "title": title,
                    "currency_id": "ARS",
                    "quantity": qty,
                    "unit_price": unit_price,
                })
                total_qty += qty

        if not items:
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # URLs absolutas
        def abs_uri(path: str):
            site_url = getattr(settings, "SITE_URL", "")
            if site_url:
                return site_url.rstrip("/") + path
            return request.build_absolute_uri(path)

        success_url = abs_uri("/payments/success/")
        failure_url = abs_uri("/payments/failure/")
        pending_url = abs_uri("/payments/pending/")
        #notification_url = abs_uri("/api/payments/mp/webhook/")

        ref = f"cart-{request.session.session_key or 'anon'}-{int(timezone.now().timestamp())}"

        sdk = mercadopago.SDK(token)
        print("MP back_urls:", success_url, failure_url, pending_url)

        pref_data = {
            "items": items,
            "back_urls": {
                "success": success_url,
                "failure": failure_url,
                "pending": pending_url,
            },
            #"notification_url": notification_url,
            # "auto_return": "approved",  # ⬅️ comentar/quitar en desarrollo
            "external_reference": ref,
        }


        pref = sdk.preference().create(pref_data)
        if pref.get("status") != 201:
            return Response({"error": "No se pudo crear la preferencia", "mp": pref},
                            status=status.HTTP_502_BAD_GATEWAY)

        init_point = pref["response"].get("init_point") or pref["response"].get("sandbox_init_point")
        return Response({"ok": True, "init_point": init_point, "external_reference": ref, "count": total_qty},
                        status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(APIView):
    """Webhook de MercadoPago (opcional)."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            data = {}
        return Response({"received": True}, status=status.HTTP_200_OK)

    def get(self, request):
        return Response({"alive": True}, status=status.HTTP_200_OK)
