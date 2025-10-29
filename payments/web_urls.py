from django.urls import path
from .web_views import mp_success, mp_failure, mp_pending

urlpatterns = [
    path('success/', mp_success, name='mp-success'),
    path('failure/', mp_failure, name='mp-failure'),
    path('pending/', mp_pending, name='mp-pending'),
]
