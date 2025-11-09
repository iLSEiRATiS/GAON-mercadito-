# scraping/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import urlparse, urlencode
import logging
from math import inf

from scraping.utils import compare_prices, fetch_url

log = logging.getLogger(__name__)
VERSION = "1.2.0"

# =========================
# (A) HELPERS DE FALLBACK
# =========================
def _google_search_url(query, source=None):
    """
    Devuelve una URL de búsqueda en Google como fallback.
    Ej.: https://www.google.com/search?q=buzo+tiendaB
    """
    q = (query or "").strip()
    if source:
        q = f"{q} {source}".strip()
    return f"https://www.google.com/search?{urlencode({'q': q})}"

def _needs_fallback(url):
    """
    True si la URL está vacía, invalida o apunta a dominios de ejemplo.
    """
    if not url or url == "#" or url.startswith("about:"):
        return True
    try:
        netloc = urlparse(url).netloc.lower()
    except Exception:
        return True
    # dominios de prueba/ejemplo → forzamos fallback
    return (not netloc) or netloc.startswith("example.")
# =========================


def _to_float(val, default=inf):
    try:
        if val is None:
            return default
        # soporta "12.345,67" o "12345.67"
        s = str(val).strip().replace(".", "").replace(",", ".")
        return float(s)
    except Exception:
        return default


def _normalize_item(item):
    """
    Normaliza un item del comparador garantizando el esquema esperado por el front:
    {title, source, price(float), currency, url, in_stock(bool)}
    """
    if not isinstance(item, dict):
        return None

    title = (item.get("title") or item.get("name") or "Producto").strip()
    source = (item.get("source") or item.get("store") or "N/D").strip()
    url = item.get("url") or "#"
    currency = (item.get("currency") or "").strip() or "ARS"

    # (A) aplicar fallback si la URL no sirve (p.ej. example.tiendaB)
    if _needs_fallback(url):
        url = _google_search_url(title, source)

    price = _to_float(item.get("price"), default=inf)
    in_stock = bool(item.get("in_stock")) if "in_stock" in item else True

    return {
        "title": title,
        "source": source,
        "url": url,
        "currency": currency,
        "price": price,
        "in_stock": in_stock,
    }


class ScrapePingView(APIView):
    """
    GET /api/scraping/check/
    Healthcheck sencillo.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {"ok": True, "service": "scraping", "version": VERSION},
            status=status.HTTP_200_OK,
        )


class PriceCompareView(APIView):
    """
    GET /api/scraping/search/?q=... [&wrap=1]
    - Por defecto devuelve **lista directa** (compatibilidad con tus tests y front).
    - Si pasás `wrap=1`, devuelve un objeto con {ok, query, count, results}.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        if not q:
            return Response(
                {"detail": "Falta el parametro ?q"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        wrap = request.GET.get("wrap")
        try:
            raw = compare_prices(q)
            if not isinstance(raw, list):
                raise TypeError(f"compare_prices() devolvio {type(raw).__name__}, se esperaba list")

            normalized = []
            for it in raw:
                n = _normalize_item(it)
                if n:
                    normalized.append(n)

            # orden por precio asc
            normalized.sort(key=lambda x: x["price"])

        except Exception as e:
            log.exception("Error en PriceCompareView con q=%r", q)
            return Response(
                {"detail": f"Error en comparador: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ✅ Modo por defecto: lista directa
        if not wrap:
            return Response(normalized, status=status.HTTP_200_OK)

        # 🧰 Modo envuelto
        return Response(
            {"ok": True, "query": q, "count": len(normalized), "results": normalized},
            status=status.HTTP_200_OK,
        )


class InspectSiteView(APIView):
    """
    GET /api/scraping/inspect/?url=https://...
    Descarga un preview del HTML (solo DEV).
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        url = (request.GET.get("url") or "").strip()
        if not url:
            return Response(
                {"detail": "Falta el parametro ?url"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # pequeña validación de esquema
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return Response(
                    {"detail": "URL invalida: se requiere http o https"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception:
            return Response(
                {"detail": "URL invalida"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ok, info = fetch_url(url, max_bytes=4096)  # asegura tope de bytes
        except Exception as e:
            log.exception("fetch_url fallo para %s", url)
            return Response(
                {"ok": False, "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not ok:
            return Response(
                {"ok": False, "error": info},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        preview = info[:1000] + ("..." if len(info) > 1000 else "")
        return Response(
            {"ok": True, "url": url, "preview_len": len(info), "preview": preview},
            status=status.HTTP_200_OK,
        )
