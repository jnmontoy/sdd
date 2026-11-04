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

**Por qué `dependency_overrides`:** se prueba la validación sin depender de un token real. La autenticación tiene su propia prueba, la del 401.

---

## 4. Pruebas de frontend

- **Vitest + Testing Library:** hooks (`useAuth`, `useSmartPolling`), validaciones Zod y componentes con lógica (filtros, paginador, drawer). Se busca por rol y etiqueta accesible, no por clase CSS.
- **E2E (pytest-playwright):** login, carga de tabla, filtro, apertura y cierre del drawer, confirmación destructiva y sesión vencida. Sin esperas fijas. Ver la [guía práctica](../stack/e2e_testing_guide.md).

---

## 5. Puertas de calidad (CI)

| Puerta | Umbral | Comando | Si falla |
| :--- | :--- | :--- | :--- |
| Pruebas backend | 100 % aprobadas | `python -m pytest -m "not e2e" --cov=backend --cov-fail-under=80` | Se bloquea la integración |
| Cobertura | ≥ 80 % en lógica de negocio, servicios y endpoints | (la misma) | Se bloquea la integración |
| Pruebas frontend y tipos | 100 % aprobadas, sin errores de tipos | `npm run typecheck && npm test` | Se bloquea la integración |
| Lint | Sin errores | `ruff check backend pruebas` · `npm run lint` | Se bloquea la integración |
| Dependencias | Sin vulnerabilidades altas ni críticas | `pip-audit -r backend/requirements.txt` · `npm audit --audit-level=high` | Se bloquea el despliegue |
| Humo HTTP | 100 % aprobado | `python pruebas/validate_endpoints.py --base-url <ambiente>` | Se bloquea el despliegue |
| E2E de humo | 100 % aprobado en ambiente de pruebas | `python -m pytest pruebas/e2e -m e2e` | Se bloquea el paso a producción |

La cobertura es un indicador, no la meta: un 80 % con aserciones débiles protege menos que un 60 % con buenas pruebas de los casos de la sección 3. La revisión de código verifica que esos casos estén cubiertos.

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

## 7. Prototipos (BP-10)

Los prototipos de `mock/` no llevan pruebas automatizadas: son HTML estático sin servidor ni base de datos. Su validación es la revisión con el usuario de negocio y el contrato de datos (`datos_<pantalla>.md`) que el backend implementará después. Las pruebas de este protocolo empiezan cuando el prototipo aprobado se implementa en `frontend/` y `backend/`.
