from django.urls import path
from .views import CreatePreferenceView, WebhookView

urlpatterns = [
    path('create/', CreatePreferenceView.as_view(), name='payments_create'),          # ← ruta pedida
    path('mp/preference/', CreatePreferenceView.as_view(), name='mp_create_preference'),
    path('mp/webhook/', WebhookView.as_view(), name='mp_webhook'),
]

