from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import urlencode

from scraping.utils import compare_prices, fetch_url


class ScrapePingView(APIView):
    """
    🔹 Healthcheck del microservicio de scraping.
    Permite confirmar que la API esté operativa.

    **GET** `/api/scraping/check/`
    Devuelve:
    ```json
    {
      "ok": true,
      "service": "scraping",
      "version": "1.1.0"
    }
    ```
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({
            "ok": True,
            "service": "scraping",
            "version": "1.1.0",
        }, status=status.HTTP_200_OK)


class PriceCompareView(APIView):
    """
    🔹 Compara precios simulados o reales según query dada.
    
    **GET** `/api/scraping/search/?q=palabra`
    
    Parámetros:
    - `q`: término de búsqueda (requerido)

    Ejemplo de respuesta:
    ```json
    {
      "query": "remera oversize",
      "count": 3,
      "results": [
        {"vendor": "MercadoGO", "price": 18999, "url": "..."},
        {"vendor": "GAON Store", "price": 17500, "url": "..."}
      ]
    }
    ```
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        if not q:
            return Response(
                {"detail": "Falta el parámetro ?q"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = compare_prices(q)
        except Exception as e:
            return Response(
                {"detail": f"Error al procesar búsqueda: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "ok": True,
            "query": q,
            "count": len(data),
            "results": data,
        }, status=status.HTTP_200_OK)


class InspectSiteView(APIView):
    """
    🔍 Inspecciona un sitio remoto (solo para debug en desarrollo).

    **GET** `/api/scraping/inspect/?url=https://...`

    Descarga los primeros bytes del HTML y devuelve un preview seguro.

    ⚠️ **Advertencia:** No usar en producción.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        url = (request.GET.get("url") or "").strip()
        if not url:
            return Response(
                {"detail": "Falta el parámetro ?url"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ok, info = fetch_url(url, max_bytes=4096)
        if not ok:
            return Response(
                {"ok": False, "error": info},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # Truncamos el preview si excede tamaño
        preview = info[:1000] + ("..." if len(info) > 1000 else "")

        return Response({
            "ok": True,
            "url": url,
            "preview_len": len(info),
            "preview": preview,
        }, status=status.HTTP_200_OK)
