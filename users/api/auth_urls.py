from django.urls import path
from .auth_views import SignupView, TokenLoginView, TokenLogoutView, MeView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='auth-signup'),
    path('token/login/', TokenLoginView.as_view(), name='auth-token-login'),
    path('token/logout/', TokenLogoutView.as_view(), name='auth-token-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
]
