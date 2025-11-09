# gaon/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include

# API docs
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Sitemap
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap

# Auth views (HTML)
from users.views import login_page, signup_page, social_bridge, session_from_token

# Web views extra
from products.views import home, compare_prices_view  # home NO se importa, usamos TemplateView

# --- Sitemaps registry ---
sitemaps = {
    "static": StaticViewSitemap,
}

# --- robots.txt ---
def robots_txt(_request):
    content = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    # Favicon
    path("favicon.ico", RedirectView.as_view(url="/static/gaon.ico"), name="favicon"),

    # Home (template)
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    # Admin
    path("admin/", admin.site.urls),
    
    #About
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),

    # ---------- API (Docs) ----------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # ---------- API (Endpoints) ----------
    path("api/users/", include("users.api.urls")),
    path("api/auth/", include("users.api.auth_urls")),
    path("api/auth/session/", session_from_token, name="session-from-token"),
    path("api/products/", include("products.api.urls")),
    path("api/cart/", include("cart.api.urls")),
    path("api/payments/", include("payments.api.urls")),
    path(
        "api/scraping/",
        include(("scraping.api.urls", "scraping_api"), namespace="scraping_api"),
    ),
    path("admin/", admin.site.urls),

    # ---------- Web (HTML) ----------
    path("products/", include("products.web_urls")),
    path("cart/", include("cart.web_urls")),
    path("payments/", include("payments.web_urls")),
    path("account/", include("users.web_urls")),
    path("categories/", include("products.categories_urls")),

    # Auth HTML
    path("login/", login_page, name="login-page"),
    path("signup/", signup_page, name="signup-page"),
    path("accounts/", include("allauth.urls")),
    path("social/bridge/", social_bridge, name="social-bridge"),

    # API del chatbot (Gemini)
    path("api/chat/", include("chat.urls")),

    # Comparador de precios (HTML)
    path("comparar/", compare_prices_view, name="compare-prices"),

    # ---------- SEO ----------
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

