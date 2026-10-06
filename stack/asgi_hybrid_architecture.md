# Especificación de Arquitectura Híbrida ASGI: Django + FastAPI
## Ecosistema Jolifoods — Alto Rendimiento y Cero Problemas N+1

Esta especificación detalla el estándar arquitectónico que desacopla responsabilidades:
- **FastAPI (Capa de Entrega de Datos en JSON)**: Diseñado para ser **siempre ultra rápido** en la entrega de datos, utilizando `ORJSONResponse` para serialización nativa en C, validación declarativa Pydantic v2 y respuestas asíncronas de bajísima latencia sin sobrecarga de middleware.
- **Django (Capa Exclusiva de Seguridad y Gobierno)**: Actúa como el bastión de **seguridad**, centralizando la autenticación (JWT / SimpleJWT / Azure AD SSO), control de acceso basado en roles y permisos (RBAC), modelo unificado de usuarios, migraciones y panel de administración.

---

### 1. Principios de la Arquitectura Híbrida
1. **Separación de Responsabilidades**:
   - **FastAPI**: Capa exclusiva de entrega y serialización de datos JSON a máxima velocidad (`default_response_class=ORJSONResponse`).
   - **Django**: Capa exclusiva de seguridad, autenticación, control de accesos RBAC y gobierno del modelo de datos.
2. **Dependencias Esenciales del Stack ASGI de Alto Rendimiento**:
   - `fastapi>=0.115.0`
   - `uvicorn[standard]>=0.30.0`
   - `pydantic>=2.8.0`
   - `orjson>=3.10.0`
3. **Un solo puerto, un solo servidor ASGI**: El contenedor backend ejecuta `uvicorn config.asgi:application --host 0.0.0.0 --port 8000`. No se requieren proxies intermedios ni dos puertos diferentes.
4. **Enrutamiento por Prefijo de Ruta `/fast`**:
   - Peticiones que contengan `/fast` son dirigidas a la aplicación **FastAPI** (`core.fastapi_app`).
   - Todas las demás peticiones (`/admin/`, `/api/auth/`, vistas de seguridad Django) son procesadas por la aplicación **Django ASGI** (`get_asgi_application()`).
5. **Manejo de Conexiones de Base de Datos**: Para evitar fugas de conexiones o `InterfaceError: connection already closed`, se ejecuta `close_old_connections()` de forma asíncrona al inicio de cada petición HTTP.
6. **Cero N+1 y Ultra Velocidad en FastAPI**: Los endpoints FastAPI utilizan `select_related()` y `prefetch_related()` en Django ORM con `sync_to_async`, o proyecciones raw `.values()` serializadas directamente con `orjson`.

---

### 2. Implementación Canónica: `asgi.py`

```python
"""
Configuración ASGI Híbrida Universal para Proyectos Jolifoods.
Combina Django ASGI con FastAPI bajo un único proceso.
"""
import os
import logging
from django.core.asgi import get_asgi_application
from asgiref.sync import sync_to_async
from django.db import close_old_connections

# 1. Configurar entorno Django antes de importar componentes
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_application = get_asgi_application()

# 2. Importar aplicación FastAPI del proyecto
try:
    from config.fastapi_app import app as fastapi_application
except ImportError:
    from core.fastapi_app import app as fastapi_application

logger = logging.getLogger("asgi.hybrid")

async def application(scope, receive, send):
    path = scope.get('path', '')

    # Refrescar y limpiar conexiones inactivas a la DB
    if scope.get('type') == 'http':
        await sync_to_async(close_old_connections)()

    # Enrutamiento hacia la capa ultra-rápida FastAPI
    if scope.get('type') == 'http' and '/fast' in path:
        try:
            parts = path.split('/fast', 1)
            sub_path = parts[1]

            # Normalizar URL: quitar trailing slash para evitar 307 redirects innecesarios
            if sub_path.endswith('/') and len(sub_path) > 1:
                sub_path = sub_path[:-1]

            if not sub_path.startswith('/'):
                sub_path = '/' + sub_path

            scope['path'] = sub_path
            # Preservar el prefijo raíz para OpenAPI docs (/fast/docs)
            scope['root_path'] = parts[0] + '/fast'

            await fastapi_application(scope, receive, send)
        except Exception as e:
            logger.error(f"Error ASGI en FastAPI ({path}): {str(e)}", exc_info=True)
            # En caso de excepción no controlada, intentar resolver vía Django
            await django_application(scope, receive, send)
    else:
        # Enrutamiento hacia Django Core (Seguridad y Admin)
        await django_application(scope, receive, send)
```

---

### 3. Implementación Canónica: `fastapi_app.py`

```python
"""
Aplicación FastAPI Integrada para Consultas Masivas y Entrega Ultra Rápida de Datos JSON.
Utiliza ORJSONResponse para serialización nativa en C a microsegundos.
"""
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from asgiref.sync import sync_to_async

app = FastAPI(
    title="Jolifoods Fast API Layer",
    description="Capa ultra rápida de entrega de datos JSON optimizada con orjson y cero N+1",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse  # Serialización ultra rápida en C por defecto
)

# Configuración CORS permisiva interna
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Esquema Pydantic para respuesta de salud
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    service: str

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(),
        "service": "Jolifoods Fast Layer (orjson ultra-fast engine)"
    }
```

---

### 4. Directrices de Prevención Anti-N+1 en Consultas FastAPI

Al consultar modelos Django dentro de endpoints FastAPI, se debe seguir estrictamente una de las dos estrategias:

#### Estrategia A: `select_related` y `prefetch_related` con `sync_to_async`
```python
@sync_to_async
def get_usuarios_optimizados(skip: int, limit: int):
    from apps.usuarios.models import Usuario
    # select_related resuelve la FK 'rol' en el mismo JOIN SQL
    return list(
        Usuario.objects.select_related('rol')
        .filter(activo=True)
        .order_by('-fecha_creacion')[skip:skip+limit]
    )
```

#### Estrategia B: Proyección Directa con `.values()` (Máxima Velocidad)
Para lecturas masivas y exportaciones, `.values()` salta la instanciación de objetos del modelo Django, reduciendo el consumo de memoria en más del 70%:
```python
@sync_to_async
def get_usuarios_values():
    from apps.usuarios.models import Usuario
    return list(
        Usuario.objects.values(
            'id', 'cedula', 'nombre', 'email', 'activo', 'rol__nombre'
        )
    )
```

---

### 5. Prohibición de Ciclos `for` Anidados (Algoritmos O(1) para Respuestas en Microsegundos)

Para que FastAPI cumpla su estándar de ser la capa de entrega de datos en JSON **ultra rápida**, los endpoints y servicios tienen prohibido anidar bucles `for` ($O(N^2)$ o $O(N \times M)$) para cruzar o transformar colecciones.

1. **Regla de Oro**: Ninguna transformación de datos en memoria debe realizar búsquedas secuenciales dentro de bucles.
2. **Uso Mandatorio de Diccionarios Hash ($O(1)$)**: Si se deben relacionar o cruzar dos listas de datos (ej. clientes con pedidos, o usuarios con roles), la colección secundaria debe pre-indexarse en un `dict` o `defaultdict(list)` por clave foránea. Esto garantiza complejidad lineal **$O(N + M)$** en lugar de cuadrática $O(N \times M)$.
3. **Prohibición de Queries en Bucles**: Jamás ejecutar llamadas `get()`, `filter()` o consultas a base de datos dentro de un bucle `for`. Se deben precargar todas las entidades necesarias en lote con `filter(id__in=ids)` e indexarlas en memoria antes de la serialización JSON.

#### Ejemplo Canónico de Procesamiento en FastAPI:
```python
from collections import defaultdict
from typing import List, Dict, Any

def enriquecer_datos_ultra_rapido(usuarios: List[Dict[str, Any]], roles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # 1. Pre-indexar roles en Hash Map O(1) tiempo constante
    roles_map = {r["id"]: r["nombre"] for r in roles}

    # 2. Enriquecer usuarios en un solo paso lineal O(N) sin anidar for
    return [
        {
            **u,
            "rol_nombre": roles_map.get(u["rol_id"], "Sin Rol")
        }
        for u in usuarios
    ]
```
