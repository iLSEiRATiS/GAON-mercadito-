from django.urls import path
from users.views import account_page, account_edit

urlpatterns = [
    path('', account_page, name='account'),
    path("edit/", account_edit, name="account-edit"),
]
