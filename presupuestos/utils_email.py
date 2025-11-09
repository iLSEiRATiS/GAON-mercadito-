# presupuestos/utils_email.py
import os
from django.core.mail import EmailMessage
from django.conf import settings


def enviar_presupuesto_por_mail(presupuesto, pdf_path: str):
    """
    Envía un email al cliente con el PDF de presupuesto adjunto.
    """
    if not presupuesto.email:
        return

    asunto = f"Presupuesto #{presupuesto.id} - GAON Mercadito"
    cuerpo = (
        f"Hola,\n\n"
        f"Te enviamos el presupuesto solicitado para: {presupuesto.producto}.\n\n"
        f"Mensaje que nos dejaste:\n{presupuesto.mensaje or '-'}\n\n"
        f"Adjuntamos el PDF con el detalle.\n\n"
        f"Saludos,\n"
        f"GAON Mercadito"
    )

    email = EmailMessage(
        subject=asunto,
        body=cuerpo,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[presupuesto.email],
    )

    # Adjuntar el PDF si existe
    if pdf_path and os.path.exists(pdf_path):
        filename = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            email.attach(filename, f.read(), "application/pdf")

    email.send(fail_silently=True)
