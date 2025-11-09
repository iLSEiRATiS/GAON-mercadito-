import os
from django.conf import settings
from django.http import FileResponse, Http404
from .models import Presupuesto
from .utils_pdf import generar_pdf


def presupuesto_pdf_view(request, pk):
    """
    Devuelve el PDF del presupuesto.
    Si no existe el archivo, lo vuelve a generar.
    """
    try:
        presupuesto = Presupuesto.objects.get(pk=pk)
    except Presupuesto.DoesNotExist:
        raise Http404("Presupuesto no encontrado")

    filename = f"presupuesto_{presupuesto.id}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    # Si no existe el PDF en disco, lo generamos de nuevo
    if not os.path.exists(filepath):
        filepath = generar_pdf(presupuesto)

    return FileResponse(
        open(filepath, "rb"),
        as_attachment=True,
        filename=filename,
    )
