"""
Plantilla Canónica de Configuración de Seguridad y Hardening — Django / Jolifoods
Cumple al 100% con los criterios de auditoría (Paso 01 al 06).
"""

import os
from pathlib import Path

# --- 1. ENTORNO Y AISLAMIENTO DE SECRETOS ---
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
SECRET_KEY = os.getenv("SECRET_KEY")

if not DEBUG and not SECRET_KEY:
    raise ValueError("ERROR FATAL DE SEGURIDAD: SECRET_KEY no puede estar vacía en producción.")

# --- 2. BLINDAJE DE HOSTS (SIN COMODÍN '*') ---
# Ejemplo: ALLOWED_HOSTS=129.213.95.33,apps.jolifoods.co,localhost,127.0.0.1
raw_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]

# --- 3. POLÍTICA DE CORS RESTRINGIDA (SIN ALLOW_ALL_ORIGINS) ---
CORS_ALLOW_ALL_ORIGINS = False
raw_cors = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
CORS_ALLOW_CREDENTIALS = True  # Obligatorio para intercambio de Cookies HttpOnly

# --- 4. THROTTLING Y RATE LIMITING DISTRIBUIDO (REDIS) ---
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 2,
            "SOCKET_TIMEOUT": 2,
        }
    }
}

REST_FRAMEWORK = {
    # --- 5. PRINCIPIO DE MÍNIMO PRIVILEGIO: DENY BY DEFAULT ---
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",
        "user": "120/minute",
        "auth_login": "5/minute",  # Throttle estricto en intento de login
    },
}

# --- 6. HARDENING DE CABECERAS HTTP Y COOKIES SEGURAS ---
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# HSTS para producción
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True

# --- 7. RUTAS 100% RELATIVAS Y ALMACENAMIENTO DE ARCHIVOS MEDIA ---
# Prohibición terminante de rutas absolutas quemadas en código ('C:\...', '/home/...').
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
