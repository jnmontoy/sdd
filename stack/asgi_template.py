"""
Plantilla Canónica ASGI Híbrida: Django + FastAPI
Ecosistema Jolifoods
"""
import os
import logging
from django.core.asgi import get_asgi_application
from asgiref.sync import sync_to_async
from django.db import close_old_connections

# Configuración del entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_application = get_asgi_application()

# Importar dinámicamente aplicación FastAPI del proyecto si existe
import importlib
fastapi_application = None
for mod_name in ['config.fastapi_app', 'core.fastapi_app']:
    try:
        mod = importlib.import_module(mod_name)
        fastapi_application = getattr(mod, 'app', None)
        if fastapi_application:
            break
    except ImportError:
        pass

logger = logging.getLogger("asgi.hybrid")

async def application(scope, receive, send):
    path = scope.get('path', '')

    # Refrescar conexiones DB en cada petición HTTP
    if scope.get('type') == 'http':
        await sync_to_async(close_old_connections)()

    # Enrutamiento hacia FastAPI si la ruta contiene /fast
    if scope.get('type') == 'http' and '/fast' in path and fastapi_application is not None:
        try:
            parts = path.split('/fast', 1)
            sub_path = parts[1]

            if sub_path.endswith('/') and len(sub_path) > 1:
                sub_path = sub_path[:-1]

            if not sub_path.startswith('/'):
                sub_path = '/' + sub_path

            scope['path'] = sub_path
            scope['root_path'] = parts[0] + '/fast'

            await fastapi_application(scope, receive, send)
        except Exception as e:
            logger.error(f"Error ASGI en FastAPI: {str(e)}", exc_info=True)
            await django_application(scope, receive, send)
    else:
        # Enrutamiento hacia Django
        await django_application(scope, receive, send)
