# products/views.py
from django.shortcuts import render
from django.views.decorators.http import require_GET
from math import inf
from urllib.parse import urlparse, urlencode
import logging

from scraping.utils import compare_prices  # motor del comparador

log = logging.getLogger(__name__)

# --- helpers de fallback/normalización (mismo criterio que la API) ---
def _google_search_url(query, source=None):
    q = (query or "").strip()
    if source:
        q = f"{q} {source}".strip()
    return f"https://www.google.com/search?{urlencode({'q': q})}"

def _needs_fallback(url: str) -> bool:
    if not url or url == "#" or url.startswith("about:"):
        return True
    try:
        netloc = urlparse(url).netloc.lower()
    except Exception:
        return True
    return (not netloc) or netloc.startswith("example.")

def _to_float(val, default=inf):
    try:
        if val is None:
            return default
        s = str(val).strip().replace(".", "").replace(",", ".")
        return float(s)
    except Exception:
        return default
# ---------------------------------------------------------------------


def home(request):
    """Portada simple."""
    return render(request, "home.html")


@require_GET
def compare_prices_view(request):
    """
    Vista del comparador: si hay ?q=..., consulta el motor y renderiza resultados.
    Aplica fallback de URL para que el botón "Ver" nunca apunte a example.*.
    """
    q = (request.GET.get("q") or "").strip()
    results = []
    msg = ""

    if q:
        try:
            raw = compare_prices(q)  # se espera: list[dict]
            if not isinstance(raw, list):
                raise TypeError(f"compare_prices() devolvió {type(raw).__name__}, se esperaba list")

            normed = []
            for i, r in enumerate(raw):
                if not isinstance(r, dict):
                    log.warning("Item %s no es dict: %r", i, r)
                    continue

                title = (r.get("title") or r.get("name") or "Producto").strip()
                source = (r.get("source") or r.get("store") or "N/D").strip()
                url = r.get("url") or "#"
                #  Fallback si la URL es inválida o de ejemplo
                if _needs_fallback(url):
                    url = _google_search_url(title, source)

                currency = (r.get("currency") or "").strip() or "ARS"
                price = _to_float(r.get("price"), default=inf)
                in_stock = bool(r.get("in_stock")) if "in_stock" in r else True

                normed.append({
                    "title": title,
                    "source": source,
                    "url": url,
                    "currency": currency,
                    "price": price,
                    "in_stock": in_stock,
                })

            results = sorted(normed, key=lambda x: x["price"])
            if not results:
                msg = f"No se encontraron resultados para “{q}”."
        except Exception as e:
            log.exception("Error en compare_prices_view")
            msg = f"Error al buscar “{q}”: {e}"

    context = {"query": q, "results": results, "msg": msg}
    return render(request, "products/compare.html", context)
