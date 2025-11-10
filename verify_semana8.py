# verify_semana8.py
import sys
import json
import requests

BASE = "http://127.0.0.1:8000"

def fail(msg):
    print("❌", msg)
    sys.exit(1)

def ok(msg):
    print("✅", msg)

def get(url, params=None):
    r = requests.get(url, params=params or {}, timeout=10)
    print(f"\n▶ {r.request.method} {r.url}")
    print("Status:", r.status_code)
    if "application/json" in r.headers.get("Content-Type",""):
        print("Body:", json.dumps(r.json(), ensure_ascii=False)[:400])
    else:
        print("Body:", r.text[:400])
    return r

def main():
    # 1) Health
    r = get(f"{BASE}/api/scraping/check/")
    if not r.ok:
        fail("/api/scraping/check/ no responde 200")
    data = r.json()
    if not (data.get("ok") and data.get("service") == "scraping"):
        fail("Healthcheck no devolvió estructura esperada")
    ok("Healthcheck OK")

    # 2) Búsqueda (lista directa)
    r = get(f"{BASE}/api/scraping/search/", params={"q": "yerba"})
    if not r.ok:
        fail("/api/scraping/search/?q=yerba no responde 200")
    data = r.json()
    if not isinstance(data, list):
        fail("search (sin wrap) debería devolver una LISTA")
    if data:
        must = {"title","source","price","currency","url"}
        if not must.issubset(set(data[0].keys())):
            fail(f"Faltan campos en item: {must - set(data[0].keys())}")
    ok("Search (lista) OK")

    # 3) Búsqueda envuelta (wrap=1)
    r = get(f"{BASE}/api/scraping/search/", params={"q": "yerba", "wrap": "1"})
    if not r.ok:
        fail("search (wrap=1) no responde 200")
    obj = r.json()
    if not (obj.get("ok") and isinstance(obj.get("results"), list)):
        fail("wrap=1 debería devolver {'ok': True, 'results': [...]}")
    ok("Search (wrap=1) OK")

    print("\n🎉 Verificación Semana 8 superada.\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        fail(str(e))
