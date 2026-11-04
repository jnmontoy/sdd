# Guía práctica de pruebas de humo y E2E

Complementa al [protocolo 11](../greenfield/11_protocolo_pruebas_automaticas_y_testing_e2e.md), que define **qué** se prueba y las puertas de calidad. Aquí está el **cómo**, con ejemplos que se pueden copiar.

> **Origen:** reúne lo que funcionó en las pruebas de los proyectos internos (flujos de login, tablas con filtros, drawer y sesión vencida). Aquí se describe de forma genérica.

---

## 1. Qué cubre una prueba de humo

Una prueba de humo comprueba, en pocos segundos, que lo crítico no está roto. No reemplaza las pruebas unitarias ni de integración. Cubre:

1. **Acceso:** login correcto y redirección según permisos.
2. **Datos:** la tabla principal carga sin errores 500 y pagina.
3. **Interacción:** filtros, apertura y cierre del drawer, confirmación de acciones destructivas.
4. **Sesión:** un 401 termina en el modal de sesión vencida, sin pantalla en blanco ni bucles.

---

## 2. Dónde vive cada prueba

| Tipo | Ubicación | Herramienta | Por qué |
| :--- | :--- | :--- | :--- |
| Unitarias e integración del backend | `pruebas/unitarias/`, `pruebas/integracion/` | Pytest + pytest-django | Separa el código de producción del de pruebas (BP-17). |
| Componentes y hooks de React | Junto al componente: `frontend/src/**/X.test.tsx` | Vitest + Testing Library | Es la convención del ecosistema Vite; el import relativo evita rutas frágiles. |
| E2E y humo en navegador | `pruebas/e2e/` | pytest-playwright (Python) | Un solo ejecutor (`pytest`) para todo lo que corre en CI desde la raíz. |
| Humo HTTP externo | `pruebas/validate_endpoints.py` | Script sin dependencias | Prueba contra el servidor levantado lo declarado en `endpoints_registry.json`. |

---

## 3. Selectores estables (`data-testid`)

Las pruebas DEBERÍAN seleccionar por rol accesible (`get_by_role`, `get_by_label`) y, si no alcanza, por `data-testid`. NO DEBERÍAN depender de clases CSS, porque cambian por razones visuales.

**Por qué:** una prueba que se rompe al cambiar un estilo genera falsas alarmas y termina ignorándose.

| Elemento | `data-testid` |
| :--- | :--- |
| Campo usuario | `input-username` |
| Campo contraseña | `input-password` |
| Botón ingresar | `btn-login-submit` |
| Buscador de tabla | `datatable-search-input` |
| Fila de tabla | `datatable-row` |
| Botón exportar Excel | `btn-export-excel` |
| Drawer lateral | `sidebar-drawer` |
| Modal de confirmación | `confirm-modal` |
| Modal de sesión vencida | `session-expiration-modal` |

---

## 4. Humo E2E con pytest-playwright

Instalación, una sola vez, dentro del entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

Las credenciales de prueba se leen de variables de entorno, nunca del código:

```powershell
$env:E2E_BASE_URL = "http://localhost:5173"
$env:E2E_USER = "1000000001"
$env:E2E_PASSWORD = "<contraseña del usuario de pruebas>"
.\.venv\Scripts\python.exe -m pytest pruebas/e2e -m e2e
```

`pruebas/e2e/test_humo.py`:

```python
import os
import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:5173")
pytestmark = pytest.mark.e2e


@pytest.fixture
def sesion(page: Page) -> Page:
    usuario, clave = os.getenv("E2E_USER"), os.getenv("E2E_PASSWORD")
    if not usuario or not clave:
        pytest.skip("Defina E2E_USER y E2E_PASSWORD")
    page.goto(f"{BASE_URL}/login")
    page.get_by_test_id("input-username").fill(usuario)
    page.get_by_test_id("input-password").fill(clave)
    page.get_by_test_id("btn-login-submit").click()
    expect(page).to_have_url(re.compile(r"/dashboard"))
    return page


def test_login_lleva_al_dashboard(sesion: Page):
    expect(sesion.get_by_role("navigation")).to_be_visible()


def test_tabla_busqueda_y_drawer(sesion: Page):
    sesion.goto(f"{BASE_URL}/usuarios")
    filas = sesion.get_by_test_id("datatable-row")
    expect(filas.first).to_be_visible()

    sesion.get_by_test_id("datatable-search-input").fill("a")
    expect(filas.first).to_be_visible()  # espera por estado, no por tiempo fijo

    filas.first.get_by_role("button", name=re.compile("ver|editar", re.I)).first.click()
    drawer = sesion.get_by_test_id("sidebar-drawer")
    expect(drawer).to_be_visible()
    sesion.keyboard.press("Escape")
    expect(drawer).to_be_hidden()


def test_sesion_vencida_muestra_modal(sesion: Page):
    sesion.evaluate("window.dispatchEvent(new CustomEvent('session-expired'))")
    expect(sesion.get_by_test_id("session-expiration-modal")).to_be_visible()
```

Reglas:

- NO usar esperas fijas (`wait_for_timeout`, `sleep`). Las aserciones `expect` ya reintentan hasta que se cumple el estado. **Por qué:** las esperas fijas son la causa principal de pruebas intermitentes.
- NO envolver pasos en `if elemento.is_visible()`. Si el elemento falta, la prueba debe fallar y no pasar en silencio.
- El usuario E2E DEBE existir solo en ambientes de prueba y tener permisos mínimos.

---

## 5. Humo del backend con Pytest

```powershell
.\.venv\Scripts\python.exe -m pytest pruebas/integracion -v
```

`pruebas/integracion/test_humo_api.py`:

```python
import pytest
from django.contrib.auth import get_user_model
from fastapi.testclient import TestClient


def test_salud_vida():
    from config.fastapi_app import app

    assert TestClient(app).get("/health/live").status_code == 200


@pytest.mark.django_db
def test_ruta_protegida_rechaza_sin_token(api_client):
    assert api_client.get("/api/v1/usuarios/").status_code == 401


@pytest.mark.django_db
def test_listado_sin_n_mas_1(api_client, django_assert_max_num_queries):
    usuario = get_user_model().objects.create_user(username="qa", password="Prueba-segura-123")
    api_client.force_authenticate(user=usuario)
    with django_assert_max_num_queries(3):  # conteo + página + permisos
        respuesta = api_client.get("/api/v1/usuarios/?page=1&page_size=20")
    assert respuesta.status_code == 200
```

---

## 6. Reglas de ejecución

1. **Duración:** la suite de humo DEBERÍA terminar en menos de 1 minuto. Si tarda más, deja de ser de humo.
2. **Base de datos real:** las pruebas de integración DEBEN correr contra PostgreSQL (el contenedor de Docker o el servicio de CI), no SQLite. **Por qué:** SQLite no aplica igual las restricciones, los tipos ni los bloqueos de PostgreSQL, y deja pasar errores que aparecen en producción.
3. **Datos aislados:** cada prueba crea sus datos y no depende del orden de ejecución.
