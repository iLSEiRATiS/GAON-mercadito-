# chatbot/api/urls.py
from django.urls import path
from .views import ChatGeminiView

app_name = "chatbot_api"

urlpatterns = [
    path("", ChatGeminiView.as_view(), name="chat"),
]
