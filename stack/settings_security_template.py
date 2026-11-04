"""
Plantilla de configuración de seguridad para Django (se copia como `backend/config/settings_security.py`
y se importa desde settings.py: `from .settings_security import *`).

Implementa BP-01 a BP-08 de greenfield/00_normativa_buenas_practicas_y_auditoria.md.
Todo valor sensible o dependiente del ambiente se lee de variables de entorno.
"""
import os
import secrets
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# Ejecución local (manage.py, pytest): carga <raíz>/.env. No pisa variables ya definidas, así que en
# Docker/CI mandan las del entorno.
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=False)
except ImportError:
    pass


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "si", "sí")


def env_list(name: str, default: str = "") -> list:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


# --- BP-01. Ambiente y secretos -------------------------------------------------------------
DEBUG = env_bool("DEBUG", False)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("SECRET_KEY es obligatoria cuando DEBUG=False.")
    # Solo desarrollo: clave efímera (invalida sesiones al reiniciar, lo cual es aceptable en local).
    SECRET_KEY = secrets.token_urlsafe(50)

# --- BP-02. Hosts permitidos (sin comodín) -------------------------------------------------
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
if "*" in ALLOWED_HOSTS and not DEBUG:
    raise ImproperlyConfigured("ALLOWED_HOSTS no puede contener '*' en producción.")

# Orígenes confiables para CSRF (necesario con HTTPS y frontend en otro origen).
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")

# --- BP-03. CORS restringido --------------------------------------------------------------
# CORS_ALLOWED_ORIGINS NO acepta comodines. Para subdominios use CORS_ALLOWED_ORIGIN_REGEXES,
# p. ej. r"^https://[a-z0-9-]+\.ejemplo\.com$".
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
CORS_ALLOWED_ORIGIN_REGEXES = env_list("CORS_ALLOWED_ORIGIN_REGEXES", "")
CORS_ALLOW_CREDENTIALS = True  # Necesario para enviar la cookie HttpOnly del refresh token.

# --- BP-04. Caché compartida y limitación de tasa ------------------------------------------
# Redis como caché: los contadores de throttling se comparten entre procesos/contenedores.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 2,
            "SOCKET_TIMEOUT": 2,
        },
    }
}

REST_FRAMEWORK = {
    # --- BP-05. Denegar por defecto: cada vista pública lo declara con AllowAny.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("THROTTLE_ANON", "30/minute"),
        "user": os.getenv("THROTTLE_USER", "120/minute"),
        # Usar en la vista de login: throttle_scope = "auth_login"
        "auth_login": os.getenv("THROTTLE_LOGIN", "5/minute"),
        "auth_recovery": os.getenv("THROTTLE_RECOVERY", "3/minute"),
    },
}

# Access token corto (vive en memoria del navegador); refresh rotado y en lista negra al usarse.
# Requiere "rest_framework_simplejwt.token_blacklist" en INSTALLED_APPS.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "15"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=int(os.getenv("JWT_REFRESH_HOURS", "12"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
# Cookie del refresh token (la escriben las vistas de login/refresh/logout del proyecto).
AUTH_REFRESH_COOKIE = {
    "name": "refresh_token",
    "path": "/api/v1/auth/",
    "httponly": True,
    "secure": not DEBUG,
    "samesite": "Lax",
}

# --- BP-06. Cabeceras HTTP y cookies ------------------------------------------------------
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
# SECURE_BROWSER_XSS_FILTER se eliminó: Django 4.0 lo retiró y los navegadores ya no usan X-XSS-Protection.

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG

# La SPA debe leer csrftoken para enviarlo en X-CSRFToken: por eso NO es HttpOnly. Esto no debilita
# la protección: el valor no sirve sin la cookie de sesión/refresh, que sí es HttpOnly.
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    # Detrás de Nginx/proxy que termina TLS: sin esto SECURE_SSL_REDIRECT entra en bucle.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    # includeSubDomains y preload afectan a TODOS los subdominios y son difíciles de revertir:
    # solo activarlos cuando todo el dominio sirva HTTPS.
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)

# --- BP-07 / BP-08. Rutas relativas y archivos subidos ------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
