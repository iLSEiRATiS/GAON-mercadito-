import hashlib
from datetime import datetime
from urllib.parse import quote_plus

def _stable_price(seed: str, base: int, spread: int) -> int:
    """
    Genera un precio entero estable (pseudo) en base a la query.
    base: precio base
    spread: amplitud de variación
    """
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    n = int(h[:8], 16)  # 32 bits
    return base + (n % spread)

def competitors_for_query(q: str):
    """
    Modo DEMO: genera datos determinísticos para la query q.
    Estructura pensada para integrarse fácil con tu UI.
    """
    q = (q or "").strip()
    if not q:
        return []

    slug_q = quote_plus(q.lower())

    vendors = [
        ("MercadoGO", f"https://buscar.example/mercadogo?q={slug_q}", 18999, 6000),
        ("TiendaGAON", f"https://buscar.example/gaon?q={slug_q}",     17999, 7000),
        ("ShopExpress", f"https://buscar.example/express?q={slug_q}",  16999, 8000),
    ]

    out = []
    for name, url, base, spread in vendors:
        price = _stable_price(f"{name}:{q}", base, spread)
        out.append({
            "vendor": name,
            "url": url,
            "title": f"{q.title()} - {name}",
            "price": price,
            "currency": "ARS",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "shipping": "Envío estándar",
            "stock": "En stock",
        })
    # Ordena por precio ascendente
    out.sort(key=lambda x: x["price"])
    return out
