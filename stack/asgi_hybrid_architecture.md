# Arquitectura híbrida ASGI: Django + FastAPI

Un solo proceso ASGI (Uvicorn) atiende dos aplicaciones:

- **Django:** autenticación (JWT con SimpleJWT, SSO), usuarios, roles y permisos, modelo de datos, migraciones y administración.
- **FastAPI:** endpoints de lectura intensiva (listados grandes, tableros, exportaciones), con validación y serialización de Pydantic v2.

> **Nota de versión (verificado con FastAPI 0.162):** cuando el endpoint declara su modelo o su tipo de retorno, FastAPI serializa directamente con Pydantic. Esa es la vía rápida recomendada. `ORJSONResponse`, que antes se usaba como clase de respuesta por defecto, quedó obsoleto y no se debe usar en código nuevo.

La decisión, sus alternativas y sus costos están en [ADR 0001](../memory/adrs/0001_arquitectura_hibrida_fastapi_django.md).

---

## 1. Cuándo usar cada capa

| Use Django (`/api/v1/...`) | Use FastAPI (`/fast/v1/...`) |
| :--- | :--- |
| Escrituras, formularios, CRUD con permisos por objeto | Lecturas de alto volumen o muy frecuentes (tableros, polling) |
| Todo lo de autenticación y sesión | Agregaciones y exportaciones |
| Admin y migraciones | Endpoints donde la latencia medida importa |

**Por qué no todo en FastAPI:** Django aporta autenticación, administración, migraciones y permisos ya probados. **Por qué no todo en Django:** con DRF, serializar miles de filas es notablemente más lento que con Pydantic v2. Si un proyecto no tiene lecturas pesadas, DEBERÍA usar solo Django: la capa FastAPI agrega complejidad.

---

## 2. Enrutamiento

Implementación: [`asgi_template.py`](./asgi_template.py) (se copia como `backend/config/asgi.py`).

| Ruta | Destino | Detalle |
| :--- | :--- | :--- |
| `/fast/...` | FastAPI | Se quita el prefijo: `/fast/v1/ventas` llega como `/v1/ventas`, con `root_path=/fast` para que `/fast/docs` funcione. |
| `/health/...` | FastAPI | Sin modificar; sondas de [`healthcheck.py`](./healthcheck.py). |
| Resto | Django | `/api/v1/...`, `/admin/`, etc. |

Reglas del enrutador:

- La coincidencia DEBE ser por prefijo exacto (`/fast` o `/fast/`). Buscar la subcadena `'/fast' in path` envía a FastAPI rutas como `/api/v1/breakfast/`.
- Ante un error de FastAPI NO DEBE reintentarse con Django: la respuesta pudo empezar a enviarse y un segundo inicio de respuesta rompe el protocolo ASGI.
- Para las peticiones de FastAPI que usan el ORM se llama a `close_old_connections()` antes y después. Django solo lo hace en sus propias peticiones; sin esto aparecen errores `connection already closed` cuando la conexión expira (`CONN_MAX_AGE`).

---

## 3. App FastAPI: seguridad igual que en Django

`backend/config/fastapi_app.py` (el generador `init_project.py` crea una versión mínima):

```python
import os

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from config.healthcheck import router as health_router

app = FastAPI(title="API de lectura", docs_url="/docs")

# Mismos orígenes que Django. Con allow_credentials=True NO se puede usar "*":
# el navegador lo rechaza y además abriría la API a cualquier sitio.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-CSRFToken"],
)

bearer = HTTPBearer(auto_error=False)


@sync_to_async
def _usuario_activo(user_id):
    return get_user_model().objects.filter(pk=user_id, is_active=True).first()


async def usuario_actual(cred: HTTPAuthorizationCredentials | None = Depends(bearer)):
    """Valida el mismo access token que emite Django (BP-05: privado por defecto)."""
    if cred is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado")
    try:
        token = AccessToken(cred.credentials)
    except TokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o vencido")
    usuario = await _usuario_activo(token["user_id"])
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario inactivo")
    return usuario


app.include_router(health_router)  # /health/live y /health/ready (públicas)


class Salud(BaseModel):
    status: str


@app.get("/v1/health", tags=["Salud"])
async def fast_health() -> Salud:  # el tipo de retorno activa la serialización directa de Pydantic
    return Salud(status="ok")


# Todo router de negocio se declara con la dependencia: no hay endpoints privados "olvidados".
privado = APIRouter(prefix="/v1", dependencies=[Depends(usuario_actual)])
# @privado.get("/ventas/resumen") ...
app.include_router(privado)
```

Los permisos finos (BP-19) se validan con la misma función que usa Django (por ejemplo `tiene_permiso(usuario, "ventas.ver")`), envuelta en `sync_to_async`.

---

## 4. Consultas al ORM desde FastAPI

El ORM de Django es síncrono. Dentro de `async def` DEBE llamarse con `sync_to_async`; si no, Django lanza `SynchronousOnlyOperation`.

**Opción A, objetos con relaciones precargadas:**

```python
@sync_to_async
def listar_usuarios(offset: int, limit: int):
    from apps.auth_core.models import Usuario
    return list(
        Usuario.objects.filter(is_active=True)
        .select_related("sede")
        .prefetch_related("roles")
        .order_by("-date_joined")[offset:offset + limit]
    )
```

**Opción B, proyección con `.values()`** para lecturas masivas: evita crear instancias de modelo y suele reducir bastante el tiempo y la memoria. Mídalo en su caso antes de asumir una cifra.

```python
@sync_to_async
def usuarios_para_exportar():
    from apps.auth_core.models import Usuario
    return list(Usuario.objects.values("id", "numero_documento", "first_name", "email", "is_active"))
```

Para cruzar colecciones en memoria se indexa una de ellas en un diccionario. Así el costo pasa de O(N×M) a O(N+M) (BP-11):

```python
def enriquecer(usuarios: list[dict], sedes: list[dict]) -> list[dict]:
    sede_por_id = {s["id"]: s["nombre"] for s in sedes}
    return [{**u, "sede_nombre": sede_por_id.get(u["sede_id"], "Sin sede")} for u in usuarios]
```
