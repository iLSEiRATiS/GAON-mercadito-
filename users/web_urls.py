from django.urls import path
from users.views import account_page

urlpatterns = [
    path('', account_page, name='account'),
]
