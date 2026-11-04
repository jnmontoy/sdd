"""
Plantilla ASGI híbrida: Django + FastAPI (se copia como `backend/config/asgi.py`).

Enrutamiento por prefijo exacto de ruta:
  /fast/...    -> FastAPI, quitando el prefijo (/fast/v1/health llega a FastAPI como /v1/health,
                  con root_path="/fast" para que la documentación OpenAPI genere URLs correctas).
  /health/...  -> FastAPI sin modificar la ruta (sondas de salud, ver stack/healthcheck.py).
  resto        -> Django.

La app FastAPI se busca en `config.fastapi_app:app` o `core.fastapi_app:app` y DEBE definir
`GET /v1/health` (salud propia de la capa) e incluir `healthcheck.router`.

Decisiones:
  - Se compara por prefijo exacto ("/fast/" o "/fast"), no por subcadena: con `'/fast' in path`,
    rutas como `/api/v1/breakfast/` terminaban en FastAPI.
  - Si FastAPI lanza una excepción no se reintenta con Django: la respuesta puede haberse empezado
    a enviar y un segundo `http.response.start` rompe el protocolo ASGI. Se registra y se propaga.
  - Si no hay app FastAPI, esas rutas caen en Django (que responderá 404) y se avisa en el log.
"""
import importlib
import logging
import os

from asgiref.sync import sync_to_async
from django.core.asgi import get_asgi_application
from django.db import close_old_connections

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django_application = get_asgi_application()  # Debe ir antes de importar código que use modelos.

logger = logging.getLogger("asgi.hybrid")

FAST_PREFIX = "/fast"
PASSTHROUGH_PREFIXES = ("/health/",)


def _load_fastapi_app():
    for module_name in ("config.fastapi_app", "core.fastapi_app"):
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            # Falta el módulo buscado o su paquete padre: probar el siguiente candidato.
            # Si lo que falta es otra dependencia interna, no ocultar el error.
            if exc.name is None or not (module_name == exc.name or module_name.startswith(exc.name + ".")):
                raise
            continue
        app = getattr(module, "app", None)
        if app is not None:
            return app
    logger.warning("No se encontró app FastAPI; /fast y /health serán atendidas por Django.")
    return None


fastapi_application = _load_fastapi_app()


def resolve_fastapi_scope(path: str):
    """Devuelve (sub_path, root_path) si la ruta va a FastAPI, o None si va a Django."""
    if path == FAST_PREFIX or path.startswith(FAST_PREFIX + "/"):
        sub_path = path[len(FAST_PREFIX):] or "/"
        if len(sub_path) > 1 and sub_path.endswith("/"):
            sub_path = sub_path[:-1]
        return sub_path, FAST_PREFIX
    if path.startswith(PASSTHROUGH_PREFIXES) or path == "/health":
        return path, ""
    return None


async def application(scope, receive, send):
    if scope["type"] == "http" and fastapi_application is not None:
        resolved = resolve_fastapi_scope(scope.get("path", ""))
        if resolved is not None:
            sub_path, root_path = resolved
            fast_scope = dict(scope, path=sub_path, root_path=scope.get("root_path", "") + root_path)
            # Django solo limpia conexiones en sus propias peticiones; las de FastAPI que usan el
            # ORM (vía sync_to_async) necesitan hacerlo explícitamente, antes y después.
            await sync_to_async(close_old_connections)()
            try:
                await fastapi_application(fast_scope, receive, send)
            except Exception:
                logger.exception("Error no controlado en FastAPI para %s", scope.get("path"))
                raise
            finally:
                await sync_to_async(close_old_connections)()
            return
    # Django gestiona por sí mismo el cierre de conexiones viejas en cada petición.
    await django_application(scope, receive, send)
