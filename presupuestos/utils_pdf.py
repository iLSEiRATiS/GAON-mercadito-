from reportlab.pdfgen import canvas
from django.conf import settings
import os


def generar_pdf(presupuesto):
    """
    Genera un PDF simple con los datos del presupuesto
    y lo guarda en MEDIA_ROOT/presupuesto_<id>.pdf
    Devuelve la ruta absoluta al archivo.
    """
    # Asegurate de que MEDIA_ROOT exista
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    filename = f"presupuesto_{presupuesto.id}.pdf"
    ruta = os.path.join(settings.MEDIA_ROOT, filename)

    c = canvas.Canvas(ruta)
    c.setTitle(f"Presupuesto #{presupuesto.id}")

    y = 750
    c.drawString(100, y,      f"Presupuesto #{presupuesto.id}")
    y -= 30
    c.drawString(100, y,      f"Producto: {presupuesto.producto}")
    y -= 20
    c.drawString(100, y,      f"Email: {presupuesto.email}")
    y -= 20
    c.drawString(100, y,      "Mensaje:")
    y -= 20

    # Mensaje puede ser largo: lo cortamos en líneas
    from textwrap import wrap
    for linea in wrap(presupuesto.mensaje or "", width=80):
        c.drawString(100, y, linea)
        y -= 15

    c.showPage()
    c.save()

    return ruta
