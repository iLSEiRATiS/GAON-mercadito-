from django.urls import path
from .web_views import payment_success, payment_failure, payment_pending

urlpatterns = [
    path('success/', payment_success, name='payment_success'),
    path('failure/', payment_failure, name='payment_failure'),
    path('pending/', payment_pending, name='payment_pending'),
]
