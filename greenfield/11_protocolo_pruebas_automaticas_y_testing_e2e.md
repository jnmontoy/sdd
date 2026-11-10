# Protocolo de pruebas automáticas

Define **qué** se prueba, **dónde** vive cada prueba y qué **puertas de calidad** debe pasar un cambio antes de llegar a producción. Los ejemplos para copiar están en la [guía práctica](../stack/e2e_testing_guide.md).

Las pruebas reducen el riesgo, pero no garantizan que no haya errores. Cada puerta de este protocolo está asociada a un comando que la verifica, para que no dependa de que alguien la recuerde.

---

## 1. Proporción de pruebas

```text
            ▲  E2E / humo (pocas)          Flujos críticos en navegador real
           ╱ ╲
          ╱───╲  Integración (varias)      Endpoints con BD real: estados HTTP, permisos, N+1
         ╱─────╲
        ╱───────╲  Unitarias (muchas)      Lógica de negocio, validadores, utilidades, hooks
```

Muchas pruebas unitarias rápidas, varias de integración y pocas E2E. **Por qué:** las E2E son lentas y frágiles, y cuando fallan cuesta saber dónde está el problema. Lo que puede probarse más abajo en la pirámide se prueba ahí.

---

## 2. Dónde vive cada prueba (BP-17)

```text
<raíz-del-proyecto>/
├── pytest.ini                 # testpaths = pruebas · pythonpath = backend
├── pruebas/
│   ├── conftest.py            # fixtures compartidas (api_client, usuarios, roles)
│   ├── unitarias/             # sin BD ni red
│   ├── integracion/           # endpoints Django (APIClient) y FastAPI (TestClient) contra PostgreSQL
│   ├── e2e/                   # pytest-playwright, marca @pytest.mark.e2e
│   └── validate_endpoints.py  # humo HTTP contra la app levantada
├── backend/                   # solo código de producción
└── frontend/src/**/X.test.tsx # Vitest + Testing Library, junto al componente
```

`init_project.py` genera esta estructura con un `conftest.py` y una prueba de ejemplo.

---

## 3. Qué debe probar cada endpoint

Un endpoint se considera probado cuando su suite de integración cubre los casos que le aplican:

| # | Caso | Esperado | Aplica a |
| :--- | :--- | :--- | :--- |
| 1 | Petición válida | 200/201 y el contrato JSON (campos y tipos) | Todos |
| 2 | Sin autenticación | 401 | Privados (BP-05) |
| 3 | Usuario sin el permiso | 403 | Con permiso específico (BP-19) |
| 4 | Datos inválidos | 400 (DRF) o 422 (FastAPI) con detalle por campo | Los que reciben datos |
| 5 | Consultas a la BD | No más de un máximo fijo (`django_assert_max_num_queries`) | Listados (BP-11) |
| 6 | Límite de tasa | 429 con `Retry-After` | Login, recuperación y endpoints con límite propio (BP-04) |

El caso 6 no se repite en cada endpoint: el límite global es configuración compartida y basta probarlo una vez. Se prueba de forma individual en los endpoints que tienen un límite propio.

### 3.1. Ejemplo con Django (DRF)

```python
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def usuario(db):
    return get_user_model().objects.create_user(username="qa", password="Prueba-segura-123")


@pytest.mark.django_db
class TestListadoUsuarios:
    url = "/api/v1/usuarios/"

    def test_sin_sesion_responde_401(self, api_client):
        assert api_client.get(self.url).status_code == 401

    def test_sin_permiso_responde_403(self, api_client, usuario):
        api_client.force_authenticate(user=usuario)  # usuario sin el permiso usuarios.ver
        assert api_client.get(self.url).status_code == 403

    def test_listado_sin_n_mas_1(self, api_client, usuario_con_permiso, django_assert_max_num_queries):
        api_client.force_authenticate(user=usuario_con_permiso)
        with django_assert_max_num_queries(4):  # conteo + página + roles precargados + permisos
            respuesta = api_client.get(self.url)
        assert respuesta.status_code == 200
        assert {"count", "results"} <= respuesta.json().keys()
```

(`usuario_con_permiso` es una fixture del proyecto en `pruebas/conftest.py` que crea el rol con la clave `usuarios.ver`).

### 3.2. Ejemplo con FastAPI

```python
from fastapi.testclient import TestClient

from config.fastapi_app import app, usuario_actual

client = TestClient(app)


def test_salud():
    assert client.get("/v1/health").json() == {"status": "ok"}


def test_privado_sin_token_responde_401():
    assert client.get("/v1/ventas/resumen").status_code == 401


def test_validacion_responde_422():
    app.dependency_overrides[usuario_actual] = lambda: object()  # simula sesión válida
    try:
        respuesta = client.get("/v1/ventas/resumen", params={"desde": "no-es-fecha"})
        assert respuesta.status_code == 422
    finally:
        app.dependency_overrides.clear()
```

**Por qué `dependency_overrides`:** se prueba la validación sin depender de un token real. La autenticación tiene su propia prueba, la del 401. En una suite grande, la limpieza va en una fixture con `yield` (no en cada prueba), para que un fallo no deje la sesión simulada activa en las pruebas siguientes.

### 3.3. FastAPI asíncrono con el ORM de Django (arquitectura híbrida)
`TestClient` sirve para la mayoría de los casos. Cuando la prueba en sí es asíncrona (por ejemplo, para probar dos peticiones concurrentes o un WebSocket junto a otra llamada), se usa el cliente asíncrono de httpx sobre la app, sin red:

```python
import httpx
import pytest

from config.fastapi_app import app


@pytest.mark.django_db(transaction=True)
async def test_resumen_concurrente():
    transporte = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transporte, base_url="http://pruebas") as cliente:
        respuesta = await cliente.get("/v1/salud")
    assert respuesta.status_code == 200
```

- **`transaction=True` es obligatorio** si el endpoint usa el ORM con `sync_to_async`: el ORM corre en otro hilo y no ve los datos que la prueba creó dentro de la transacción normal de `django_db`. Sin esa marca la prueba falla de forma confusa (registros «que no existen») o pasa por casualidad.
- Las pruebas asíncronas necesitan `pytest-asyncio` (`asyncio_mode = auto` en `pytest.ini`) o `anyio`.

### 3.4. Aislamiento de sistemas externos (DEBE)
Ninguna prueba DEBE conectarse a sistemas reales: bases de otros equipos (réplicas de ERP, nómina), APIs de internet (mapas, festivos, geocodificación), correo ni notificaciones push. Esto vale aunque el `.env` del equipo tenga las credenciales.
- `pruebas/conftest.py` DEBE tener una fixture `autouse` que bloquee la red y las conexiones externas, con un mensaje que diga cómo simularlas:

```python
@pytest.fixture(autouse=True)
def sin_sistemas_externos(monkeypatch):
    def bloqueado(*_a, **_k):
        raise httpx.ConnectError("Red externa bloqueada en las pruebas: simula la respuesta con patch.")
    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", bloqueado)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", bloqueado)
    monkeypatch.setattr(psycopg, "connect", ...)  # bases externas
```

  El `TestClient` de FastAPI no usa esos transportes, así que sigue funcionando.
- Una prueba que necesite el sistema externo simula su respuesta con `unittest.mock.patch` sobre la función del proyecto que lo consulta, o con `respx` para respuestas HTTP.
- DEBE existir una prueba que confirme el bloqueo (que una petición real falla).

*Por qué:* una prueba que sale a internet es lenta, falla cuando el servicio externo se cae (sin que el código haya cambiado), gasta cuota de APIs pagas y, contra una base real, puede leer o escribir datos de producción.

### 3.5. Pruebas generadas desde el contrato (DEBERÍA)
**Schemathesis** lee el `openapi.json` y genera cientos de peticiones válidas e inválidas para cada endpoint. Falla si alguna responde `500`, si la respuesta no cumple el esquema declarado o si acepta datos que el contrato prohíbe. Encuentra lo que nadie pensó en probar a mano (textos enormes, fechas extremas, caracteres especiales).

```powershell
schemathesis run http://localhost:8000/openapi.json -H "Authorization: Bearer $env:SDD_TOKEN_PRUEBAS"
```

Se corre contra el ambiente de pruebas (nunca producción), con un usuario de pruebas y, por defecto, solo sobre métodos de lectura; las escrituras se incluyen en un ambiente desechable.

### 3.6. Pruebas por propiedades (DEBERÍA en validadores y cargas de archivos)
En vez de tres ejemplos escritos a mano, **Hypothesis** genera miles de entradas y comprueba una regla que siempre debe cumplirse. Sirve sobre todo para lo que procesa datos de usuarios: cargas de Excel, normalización de documentos, teléfonos y códigos, cálculos de fechas.

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_normalizar_documento_nunca_falla_y_es_idempotente(texto):
    una_vez = normalizar_documento(texto)
    assert normalizar_documento(una_vez) == una_vez
```

### 3.7. Tiempo y zona horaria
Las pruebas que dependen de la fecha DEBEN fijar el reloj (`time-machine`) en vez de usar la hora real, y cubrir los bordes del día en la zona del negocio (por ejemplo, 23:30 en `America/Bogota` ya es el día siguiente en UTC). **Por qué:** sin reloj fijo, la prueba pasa hoy y falla a medianoche, un fin de mes o un festivo.

### 3.8. Migraciones
- La puerta de calidad DEBE incluir `python manage.py makemigrations --check --dry-run`: falla si un cambio de modelos no trae su migración.
- Las migraciones de datos (las que usan `RunPython`) DEBERÍAN tener una prueba que las aplique sobre datos de ejemplo y verifique el resultado, y una función de reversa. Ver el [protocolo 08](./08_protocolo_migraciones_zero_downtime.md).

---

## 4. Pruebas de frontend

- **Vitest + Testing Library:** hooks (`useAuth`, `useSmartPolling`), validaciones Zod y componentes con lógica (filtros, paginador, drawer). Se busca por rol y etiqueta accesible, no por clase CSS.
- **E2E (pytest-playwright):** login, carga de tabla, filtro, apertura y cierre del drawer, confirmación destructiva y sesión vencida. Sin esperas fijas. Ver la [guía práctica](../stack/e2e_testing_guide.md).
- **Accesibilidad automática:** las E2E de las pantallas principales DEBERÍAN pasar `axe-core` (paquete `axe-playwright-python`) sin infracciones graves. Detecta etiquetas faltantes, contraste insuficiente y botones sin nombre; no reemplaza la prueba con teclado.
- **Respuestas simuladas en el frontend:** las pruebas de componentes que llaman a la API DEBERÍAN simularla con **MSW** (Mock Service Worker), no con funciones falsas dentro del componente: así se prueba también el cliente HTTP y el manejo de errores (401, 500, red caída).

### 4.1. Apps móviles (Expo / React Native)
- **Unitarias y de componentes:** `jest-expo` con React Native Testing Library, buscando por texto y `accessibilityLabel`. Empiezan por lo que más se rompe: hooks de sesión y sincronización, formateo de fechas y moneda, pantallas con estados de carga, vacío y error.
- **E2E en dispositivo o emulador:** **Maestro** (flujos en YAML, sin código nativo) para los flujos críticos: login, la tarea principal del usuario y el trabajo sin conexión si la app lo tiene. Se corren antes de publicar una versión.
- Se instalan con `npx expo install` para respetar las versiones del SDK.

---

## 5. Puertas de calidad (CI)

| Puerta | Umbral | Comando | Si falla |
| :--- | :--- | :--- | :--- |
| Pruebas backend | 100 % aprobadas, en paralelo y en orden aleatorio | `python -m pytest -m "not e2e" -n auto --cov=backend --cov-branch --cov-report=xml` | Se bloquea la integración |
| Cobertura de lo cambiado | ≥ 80 % de las líneas nuevas o modificadas | `diff-cover coverage.xml --compare-branch=origin/main --fail-under=80` | Se bloquea la integración |
| Cobertura global | No baja respecto a `main` (referencia ≥ 80 % en servicios y endpoints) | (el reporte de `--cov`) | Se revisa en la integración |
| Migraciones | Ningún cambio de modelos sin migración | `python manage.py makemigrations --check --dry-run` | Se bloquea la integración |
| Pruebas frontend y tipos | 100 % aprobadas, sin errores de tipos | `npm run typecheck && npm test` | Se bloquea la integración |
| Lint y seguridad estática | Sin errores, incluidas las reglas de seguridad | `ruff check backend pruebas` (con las reglas `S`, equivalentes a Bandit) · `npm run lint` | Se bloquea la integración |
| Tipos en Python | Sin errores nuevos | `mypy backend` con `django-stubs`, o `pyright` | Se revisa en la integración (DEBERÍA) |
| Contrato de la API | Sin `500` ni respuestas fuera del esquema; sin cambios incompatibles | `schemathesis run …` (3.5) · `oasdiff breaking` ([protocolo 09](./09_protocolo_gobernanza_apis_y_breaking_changes.md)) | Se bloquea el despliegue |
| Dependencias | Sin vulnerabilidades altas ni críticas | `pip-audit -r backend/requirements.txt` · `npm audit --audit-level=high` | Se bloquea el despliegue |
| Humo HTTP | 100 % aprobado | `python pruebas/validate_endpoints.py --base-url <ambiente>` | Se bloquea el despliegue |
| E2E de humo | 100 % aprobado en ambiente de pruebas | `python -m pytest pruebas/e2e -m e2e` | Se bloquea el paso a producción |

La cobertura es un indicador, no la meta: un 80 % con aserciones débiles protege menos que un 60 % con buenas pruebas de los casos de la sección 3. La revisión de código verifica que esos casos estén cubiertos.

**Por qué cobertura de lo cambiado y no solo la global:** en un proyecto que ya existe, exigir 80 % global de un día para otro es imposible, y un promedio alto puede esconder un módulo nuevo sin pruebas. Medir las líneas que cada cambio agrega o modifica sube la calidad cambio a cambio. `--cov-branch` cuenta también las ramas de cada `if`, no solo las líneas.

**Por qué en paralelo y en orden aleatorio:** `pytest-xdist` (`-n auto`) reparte las pruebas entre los núcleos y acorta la suite; `pytest-randomly` cambia el orden en cada corrida y descubre pruebas que solo pasan porque otra dejó datos o ajustes cambiados. Si una prueba falla solo en cierto orden, el error está en la prueba (estado compartido), no en el azar.

**Mutación (PUEDE, en módulos críticos):** `mutmut` cambia el código a propósito (un `>` por `>=`, un `True` por `False`) y verifica que alguna prueba lo note. Mide si las pruebas de verdad comprueban algo. Es lento: se corre de vez en cuando sobre permisos, cálculos de dinero o cargas masivas, no en cada cambio.

---

## 6. Validador de endpoints

[`stack/validate_endpoints.py`](../stack/validate_endpoints.py) (copiado a `pruebas/validate_endpoints.py`) prueba desde fuera, por HTTP, lo declarado en `backend/config/endpoints_registry.json`:

- el código HTTP esperado;
- deny-by-default: cada endpoint privado responde 401/403 sin token;
- las cabeceras de seguridad (`X-Frame-Options`, `X-Content-Type-Options`, y HSTS en HTTPS);
- la latencia contra `max_latency_ms`, con percentil 95 si se usa `--samples N`.

Por seguridad, omite los endpoints marcados `"mutates": true` salvo que se use `--incluir-mutaciones`. La contraseña de login se toma de `SDD_LOGIN_PASSWORD`, nunca de un argumento. Termina con código 0 si todo pasa y 1 si algo falla. Uso y opciones: [`stack/README.md`](../stack/README.md#4-validador-de-endpoints).

No reemplaza las pruebas de integración: no verifica permisos por rol, contratos JSON detallados ni consultas N+1.

---

## 7. Pruebas inestables

Una prueba que a veces pasa y a veces falla sin cambios en el código (*flaky*) NO DEBE «arreglarse» con reintentos automáticos ni con esperas fijas más largas: eso esconde el error. Se hace lo siguiente:
1. Se reproduce con `pytest --randomly-seed=<semilla>` (la semilla sale al inicio de la corrida que falló) o repitiendo la prueba (`pytest-repeat`, `--count 50`).
2. Las causas habituales son estado compartido entre pruebas, la hora real (3.7), la red (3.4), el orden de resultados sin `order_by` y esperas fijas en E2E.
3. Si no se puede corregir el mismo día, se marca con `@pytest.mark.skip(reason="inestable: <causa>, <fecha>")`, se registra en `memory/learnings/bug_lessons.md` y se corrige en el siguiente cambio. Una prueba marcada así no puede quedar más de una semana.

**Por qué:** cuando las pruebas fallan al azar, el equipo aprende a ignorarlas, y entonces tampoco ve cuando fallan por un error real.

---

## 8. Prototipos (BP-10)

Los prototipos de `mock/` no llevan pruebas automatizadas: son HTML estático sin servidor ni base de datos. Su validación es la revisión con el usuario de negocio y el contrato de datos (`datos_<pantalla>.md`) que el backend implementará después. Las pruebas de este protocolo empiezan cuando el prototipo aprobado se implementa en `frontend/` y `backend/`.
