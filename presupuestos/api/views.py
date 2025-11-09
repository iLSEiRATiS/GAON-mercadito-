# presupuestos/api/views.py
from rest_framework import generics, permissions
from presupuestos.models import Presupuesto
from .serializers import PresupuestoSerializer
from presupuestos.utils import enviar_a_telegram
from presupuestos.utils_pdf import generar_pdf
from presupuestos.utils_email import enviar_presupuesto_por_mail


class PresupuestoCreate(generics.CreateAPIView):
    """
    Crea un Presupuesto, genera un PDF en MEDIA_ROOT
    y envía una notificación por Telegram.
    """
    queryset = Presupuesto.objects.all()
    serializer_class = PresupuestoSerializer
    # Si querés que cualquier usuario (aunque no esté logueado) pueda pedir presupuesto:
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()

        # Generar el PDF
        pdf_path = generar_pdf(instance)

        # Mensaje para Telegram
        mensaje = (
            f"📩 Nuevo presupuesto recibido\n\n"
            f"ID: {instance.id}\n"
            f"Producto: {instance.producto}\n"
            f"Email: {instance.email}\n"
            f"Mensaje: {instance.mensaje}\n"
            f"📄 PDF generado en:\n{pdf_path}"
        )

        try:
            enviar_a_telegram(mensaje)
        except Exception:
            # No queremos que la API falle si Telegram se cae
            pass

        # Enviar mail al cliente con el PDF adjunto
        try:
            enviar_presupuesto_por_mail(instance, pdf_path)
        except Exception as e:
            # Podés loguear si querés, pero no romper la API
            print("Error enviando presupuesto por mail:", e)
            pass
