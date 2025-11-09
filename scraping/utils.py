from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus
import json
import random
import time


def fetch_url(url: str, timeout: int = 8, max_bytes: int = 8192):
    """
    Descarga texto de una URL (solo para ver conectividad en /inspect/).
    Limita el tamaño para evitar respuestas enormes.
    Retorna (ok, data | error_msg)
    """
    try:
        req = Request(url, headers={"User-Agent": "GAON-Scraper/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read(max_bytes)
            try:
                txt = raw.decode("utf-8", errors="replace")
            except Exception:
                txt = raw.decode(errors="replace")
            return True, txt
    except HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except URLError as e:
        return False, f"URL error: {getattr(e, 'reason', str(e))}"
    except Exception as e:
        return False, f"Error: {e}"


# --------- SIMULACIÓN DE FUENTES ---------
def _fake_source(name: str, q: str, base_price: float):
    """
    Simula una “fuente” de precios. Para demo.
    """
    # variación aleatoria leve
    rnd = random.uniform(-0.15, 0.15)
    price = round(max(1.0, base_price * (1 + rnd)), 2)
    return {
        "source": name,
        "title": f"{q.title()} - {name}",
        "price": price,
        "currency": "ARS",
        "url": f"https://example.{name}/search?q={quote_plus(q)}",
        "in_stock": random.choice([True, True, True, False]),
    }


def compare_prices(q: str):
    """
    Devuelve una lista de resultados combinando “fuentes”.
    Reemplazá esta función por scraping real cuando lo necesites.
    """
    # Semilla estable por consulta para que no cambie tanto entre requests
    random.seed(hash(q) & 0xffffffff)

    base = 10000.0 + (abs(hash(q)) % 5000)  # precio base pseudoestable
    results = [
        _fake_source("tiendaA", q, base),
        _fake_source("tiendaB", q, base * 0.98),
        _fake_source("tiendaC", q, base * 1.03),
    ]

    # Ordenar de menor a mayor precio
    results.sort(key=lambda x: x["price"])
    return results
