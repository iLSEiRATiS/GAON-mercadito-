# products/views.py
from django.shortcuts import render
from django.views.decorators.http import require_GET

def home(request):
    """
    Vista mínima para la portada. Sólo renderiza templates/home.html.
    """
    return render(request, "home.html")

@require_GET
def compare_prices(request):
    """
    Vista mínima para la página de comparación de precios.
    Por ahora no consulta DB ni hace scraping: sólo muestra el formulario y
    un mensaje si hay query. La lógica real la implementamos luego según el .doc.
    """
    q = (request.GET.get("q") or "").strip()
    context = {
        "query": q,
        "results": [],   # placeholder (luego lo llenamos)
        "msg": "Comparador conectado. Falta implementar la búsqueda real." if q else "",
    }
    return render(request, "products/compare.html", context)
