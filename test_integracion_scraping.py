# test_integracion_scraping.py
import requests

BASE = "http://127.0.0.1:8000"

def check_endpoint(url):
    print(f"\n▶ {url}")
    try:
        r = requests.get(url, timeout=5)
        print(f"Status: {r.status_code}")
        if r.ok:
            print("Respuesta:")
            print(r.text[:500] + ("..." if len(r.text) > 500 else ""))
        else:
            print("Error:", r.text)
    except Exception as e:
        print("❌ No se pudo conectar:", e)

def main():
    print("=== Verificación GAON Scraping ===")
    # Healthcheck
    check_endpoint(f"{BASE}/api/scraping/check/")

    # Search JSON (lista)
    check_endpoint(f"{BASE}/api/scraping/search/?q=yerba")

    # Search JSON (modo envuelto)
    check_endpoint(f"{BASE}/api/scraping/search/?q=yerba&wrap=1")

    # Vista HTML
    check_endpoint(f"{BASE}/comparar/?q=yerba")

if __name__ == "__main__":
    main()
