# scraping/api/urls.py
"""
Rutas públicas de la API de Scraping / Comparador de precios.

Convenciones:
- check/   → Verifica que el servicio esté activo.
- search/  → Busca precios simulados o reales para una query dada.
- inspect/ → Endpoint opcional para testear/parsing de HTML de un sitio.
"""
from django.urls import path
from .views import ScrapePingView, PriceCompareView, InspectSiteView

app_name = "scraping_api"

urlpatterns = [
    # 🩺 Healthcheck / Ping
    path("check/", ScrapePingView.as_view(), name="check"),
    path("check", ScrapePingView.as_view(), name="check_noslash"),  # alias opcional

    # 💸 Comparación de precios (búsqueda principal)
    path("search/", PriceCompareView.as_view(), name="search"),
    path("search", PriceCompareView.as_view(), name="search_noslash"),  # alias opcional

    # 🔍 Inspección avanzada / debug de scraping
    path("inspect/", InspectSiteView.as_view(), name="inspect"),
    path("inspect", InspectSiteView.as_view(), name="inspect_noslash"),  # alias opcional
]
