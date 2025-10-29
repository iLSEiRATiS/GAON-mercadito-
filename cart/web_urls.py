from django.urls import path
from .web_views import cart_view

urlpatterns = [
    path('', cart_view, name='cart-view'),
]
