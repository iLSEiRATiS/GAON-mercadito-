from django.urls import path
from .views import ChatListCreateView, WelcomeView

app_name = "chat"

urlpatterns = [
    path("", ChatListCreateView.as_view(), name="chat-list-create"),
    path("welcome/", WelcomeView.as_view(), name="chat-welcome"),
]
