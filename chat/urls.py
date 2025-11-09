from django.urls import path
from .views import ChatListCreateView

app_name = "chat"

urlpatterns = [
    path("", ChatListCreateView.as_view(), name="chat-list-create"),
]
