from pathlib import Path
import environ
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# --- django-environ ---
env = environ.Env(
    DEBUG=(bool, False),
)
# Lee el archivo .env (si existe)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY", default="dev-secret-key-gaon")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

INSTALLED_APPS = [

    #Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    #Terceros
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'drf_spectacular_sidecar',

    #Propias
    'users',
    'products',
    'cart',
    'payments',
    "scraping",
    "chat",
    'presupuestos'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gaon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gaon.wsgi.application'
ASGI_APPLICATION = 'gaon.asgi.application'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',        # Django auth
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth
]

LOGIN_REDIRECT_URL = '/social/bridge/'      # adonde volver tras login OK
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True             # adonde volver tras logout
# allauth: inicia el flujo del proveedor al hacer GET (sin formulario intermedio)
SOCIALACCOUNT_LOGIN_ON_GET = True

# Permitir login con usuario o email
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_EMAIL_VERIFICATION = "none"
# Campos del formulario de alta (los que terminan con * son obligatorios)
ACCOUNT_SIGNUP_FIELDS = [
    "username*",
    "email*",
    "password1*",
    "password2*",
    "first_name*",
    "last_name*",
]
ACCOUNT_UNIQUE_EMAIL = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'GAON API',
    'DESCRIPTION': 'API de GAON con DRF y Swagger',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

LOGIN_URL = '/login/'


# MercadoPago
MP_ACCESS_TOKEN = env("MP_ACCESS_TOKEN", default="")
MP_PUBLIC_KEY = env("MP_PUBLIC_KEY", default="")

# URL base para back_urls/webhook (lo usamos en payments)
SITE_URL = env("SITE_URL", default="")
def ABSOLUTE_URI(request, path: str):
    if SITE_URL:
        return SITE_URL.rstrip("/") + path
    return request.build_absolute_uri(path)

# Static & Media
from pathlib import Path as _P
STATICFILES_DIRS = [BASE_DIR / 'static']

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
    },
    "github": {
        "SCOPE": ["user:email"],
    },
}

# Social login: autocompletar datos desde provider
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_ADAPTER = "users.adapters.MySocialAccountAdapter"

# --- CSRF/Session en desarrollo (HTTP) ---
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False      # opcional; en plantillas no importa, pero ayuda si usás JS
CSRF_COOKIE_SAMESITE = "Lax"

# Asegurá host de dev como confiable
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
GEMINI_MODEL = env("GEMINI_MODEL", default="gemini-1.5-flash-002")
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID", default="")

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@gaon-mercadito.local")
