# presupuestos/urls.py
from django.urls import path
from .web_views import presupuesto_pdf_view

urlpatterns = [
    path("<int:pk>/pdf/", presupuesto_pdf_view, name="presupuesto-pdf"),
]
