from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.views import login_page, signup_page, social_bridge, session_from_token

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/gaon.ico'), name='favicon'),
    # 🔹 Página principal -> redirige al perfil o productos
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # API principal
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # API endpoints
    path('api/users/', include('users.api.urls')),
    path('api/auth/', include('users.api.auth_urls')),
    path('api/auth/session/', session_from_token, name='session-from-token'),
    path('api/products/', include('products.api.urls')),
    path('api/cart/', include('cart.api.urls')),
    path('api/payments/', include('payments.api.urls')),

    # Web routes
    path('products/', include('products.web_urls')),
    path('cart/', include('cart.web_urls')),
    path('payments/', include('payments.web_urls')),
    path('account/', include('users.web_urls')),
    path('categories/', include('products.categories_urls')),


    # Autenticación HTML
    path('login/', login_page, name='login-page'),
    path('signup/', signup_page, name='signup-page'),

    path('accounts/', include('allauth.urls')),  # ⬅️ allauth
    path("social/bridge/", social_bridge, name="social-bridge"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

