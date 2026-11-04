# 07. Plan de Pruebas y Matriz de QA
## Módulo de Login / Autenticación — SDD Joli Foods (`SPEC-AUTH-001`)

Batería mínima de pruebas automáticas para aceptar una implementación del login. Sigue [`../../11_protocolo_pruebas_automaticas_y_testing_e2e.md`](../../11_protocolo_pruebas_automaticas_y_testing_e2e.md), [`../../../stack/e2e_testing_guide.md`](../../../stack/e2e_testing_guide.md) y BP-17.

---

## 1. Ubicación y Ejecución

| Tipo | Herramienta | Ubicación |
| :--- | :--- | :--- |
| Unitarias e integración backend | Pytest + pytest-django, **contra PostgreSQL** (no SQLite) | `pruebas/unitarias/` y `pruebas/integracion/` |
| Componentes React | Vitest + Testing Library | Junto al componente: `frontend/src/**/X.test.tsx` |
| E2E | pytest-playwright (Python) | `pruebas/e2e/` |

```
pruebas/
├── unitarias/
│   └── test_auth_hashers_y_politica.py      # TC-UN-*
├── integracion/
│   ├── test_auth_login.py                   # TC-BE-01..09, 15
│   ├── test_auth_refresh_logout.py          # TC-BE-10..14
│   └── test_auth_password_reset.py          # TC-PR-*
└── e2e/
    └── test_login_e2e.py                    # TC-E2E-* (pytest-playwright)
frontend/src/schemas/auth.schema.test.ts     # TC-FE-01
frontend/src/components/auth/LoginForm.test.tsx   # TC-FE-02..04
frontend/src/services/apiClient.test.ts      # TC-FE-05..06
pytest.ini                                   # en la raíz: testpaths = pruebas
```

```powershell
# Windows
.\.venv\Scripts\python.exe -m pytest pruebas\unitarias pruebas\integracion -q
.\.venv\Scripts\python.exe -m pytest pruebas\e2e --browser chromium --browser firefox --browser webkit
cd frontend; npx vitest run
# Linux / macOS
./.venv/bin/python -m pytest pruebas/unitarias pruebas/integracion -q
./.venv/bin/python -m pytest pruebas/e2e --browser chromium --browser firefox --browser webkit
```

Datos: usuarios creados por fixtures con documentos ficticios (`1000000001`…) y contraseñas generadas en la prueba; nunca credenciales reales. En E2E las credenciales llegan por variables de entorno `E2E_USER` y `E2E_PASSWORD`. Redis de pruebas aislado (base distinta) y vaciado entre casos.

**Selectores canónicos (`data-testid`):** `input-username` (documento), `input-password`, `btn-login-submit`, `session-expiration-modal`. Evento global de sesión vencida: `session-expired`. Las pruebas E2E NO DEBEN usar esperas fijas (`wait_for_timeout`/`sleep`); se usan las aserciones con espera automática de Playwright (`expect(...).to_be_visible()`, `page.wait_for_url(...)`).

---

## 2. Integración Backend — Login, Refresh y Logout

| ID | Caso | Preparación | Acción | Resultado esperado (asertos) |
| :--- | :--- | :--- | :--- | :--- |
| **TC-BE-01** | Login exitoso | Usuario activo `1000000001` | `POST /api/v1/auth/login/` con clave correcta | 200; cuerpo con `access` y `user` sin campos de contraseña; `Set-Cookie refresh_token` contiene `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/api/v1/auth/`; se creó `SesionUsuario` activa; bitácora `LOGIN_SUCCESS_CREDENTIALS`. |
| **TC-BE-02** | Clave errada | Usuario existe | Login con clave errada | 401 `INVALID_CREDENTIALS`; contador `rl:login:doc:*` = 1; bitácora `LOGIN_FAILED_BAD_PASSWORD`. |
| **TC-BE-03** | Documento inexistente | No existe `1000000099` | Login | 401 con **cuerpo byte a byte igual** a TC-BE-02. |
| **TC-BE-04** | Usuario inactivo | `is_active=False` | Login con clave correcta | 403 `USER_INACTIVE`; sin cookie de refresh. |
| **TC-BE-05** | Usuario inactivo con clave errada | `is_active=False` | Login con clave errada | 401 `INVALID_CREDENTIALS` (no revela que está inactivo). |
| **TC-BE-06** | Rol exige SSO | Rol con `exige_sso=True` | Login con clave correcta | 403 `SSO_REQUIRED`; sin cookie. |
| **TC-BE-07** | Bloqueo por documento | — | 5 logins fallidos con `1000000001` | 6.º intento (aun con clave correcta) → 429 con `Retry-After` > 0. |
| **TC-BE-08** | Bloqueo sin enumeración | — | 5 logins fallidos con documento **inexistente** | 6.º intento → 429 idéntico a TC-BE-07. |
| **TC-BE-09** | Validación de entrada | — | `numero_documento = "1000' OR '1'='1"` | 400 `VALIDATION_ERROR`; sin consulta a la tabla de usuarios. |
| **TC-BE-10** | Refresh válido | Login previo | `POST /auth/refresh/` con cookie + `X-CSRFToken` | 200 con `access` nuevo; cookie `refresh_token` distinta; el refresh anterior queda en lista negra. |
| **TC-BE-11** | Refresh sin CSRF | Login previo | Refresh sin cabecera `X-CSRFToken` | 403 `CSRF_FAILED`. |
| **TC-BE-12** | Reutilización de refresh rotado | Refresh ya rotado | Refresh con el valor viejo | 401 `REFRESH_INVALID`; bitácora `TOKEN_REFRESH_REUSED`. |
| **TC-BE-13** | Logout | Sesión activa | `POST /auth/logout/` | 204; `Set-Cookie refresh_token` con `Max-Age=0`; refresh en lista negra; `SesionUsuario.is_activa=False`; refresh posterior → 401. |
| **TC-BE-14** | Logout idempotente | Sin cookie | `POST /auth/logout/` con CSRF | 204. |
| **TC-BE-15** | Check-user sin enumeración | Documento inexistente y uno normal | `POST /auth/check-user/` | Ambos `{ "metodo": "PASSWORD" }`, sin otros campos. |

## 3. Integración Backend — Restablecimiento de Contraseña

| ID | Caso | Resultado esperado |
| :--- | :--- | :--- |
| **TC-PR-01** | Solicitud con usuario existente | 202; se crea un `TokenRestablecimientoClave` cuyo `token_hash` ≠ token enviado por correo (correo capturado con `locmem`). |
| **TC-PR-02** | Solicitud con usuario inexistente | 202 con el mismo cuerpo que TC-PR-01; no se envía correo; no se crea token. |
| **TC-PR-03** | Token de un solo uso | Confirmar dos veces con el mismo token → la 2.ª responde 400 `TOKEN_EXPIRED_OR_INVALID`. |
| **TC-PR-04** | Expiración | Token con `fecha_expiracion` en el pasado (congelar tiempo) → 400. |
| **TC-PR-05** | Solo un token vigente | Dos solicitudes seguidas → el primer token queda inutilizable. |
| **TC-PR-06** | Revocación de sesiones | Con 2 sesiones activas, confirmar nueva clave → ambos refresh quedan en lista negra y `SesionUsuario.is_activa=False`. |
| **TC-PR-07** | Política de contraseña | `new_password = "12345678"` → 400 `PASSWORD_POLICY`. |
| **TC-PR-08** | Límite de solicitudes | 4.ª solicitud en 1 h para el mismo identificador → 202 sin envío de correo (el límite no se revela). |

## 4. Unitarias

| ID | Caso | Resultado esperado |
| :--- | :--- | :--- |
| **TC-UN-01** | Hasher | `make_password()` produce un hash con prefijo `argon2$` (o `pbkdf2_sha256$`); `check_password()` valida. |
| **TC-UN-02** | `register_failed_attempt` concurrente | Dos llamadas simultáneas incrementan el contador en 2 (uso de `F()`). |
| **TC-FE-01** | `loginSchema` (Zod) | Acepta 5–15 dígitos; rechaza letras, símbolos, vacío y >15. |
| **TC-FE-02** | Doble envío | Con la petición en curso el botón está `disabled` y solo se registra 1 llamada al mock HTTP. |
| **TC-FE-03** | Ver contraseña | El input alterna `type` y `aria-pressed`. |
| **TC-FE-04** | Recordar documento | Marcado → `localStorage[STORAGE_KEYS.rememberedDoc]` = documento; desmarcado → clave eliminada; nunca se guarda la contraseña. |
| **TC-FE-05** | Access en memoria | Tras login exitoso, ninguna clave de `localStorage`/`sessionStorage` contiene el access token. |
| **TC-FE-06** | Cola de refresh | Tres peticiones simultáneas reciben 401 → se hace **un** solo refresh y las tres se reintentan. |

## 5. E2E (pytest-playwright: Chromium, Firefox, WebKit)

| ID | Caso | Resultado esperado |
| :--- | :--- | :--- |
| **TC-E2E-01** | Flujo completo | Llenar `input-username`/`input-password` con `E2E_USER`/`E2E_PASSWORD`, clic en `btn-login-submit` → `wait_for_url` al tablero; recargar la página mantiene la sesión (vía refresh). |
| **TC-E2E-02** | Teclado | Formulario completo operable con `Tab`/`Enter`/`Espacio`; foco visible en cada paso. |
| **TC-E2E-03** | Sesión vencida | Invalidar el refresh en servidor y despachar `session-expired` (o forzar 401) → `session-expiration-modal` visible; al confirmar navega a `/login?redirect=...`. |
| **TC-E2E-04** | Accesibilidad | `axe-playwright-python` sin violaciones serias o críticas en `/login`, en tema noche y día. |

```python
# pruebas/e2e/test_login_e2e.py (fragmento)
import os
import re
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:5173")

def test_login_exitoso(page: Page) -> None:
    page.goto(f"{BASE_URL}/login")
    page.get_by_test_id("input-username").fill(os.environ["E2E_USER"])
    page.get_by_test_id("input-password").fill(os.environ["E2E_PASSWORD"])
    page.get_by_test_id("btn-login-submit").click()
    page.wait_for_url(re.compile(r".*/dashboard"))
    tokens = page.evaluate("() => JSON.stringify({...localStorage, ...sessionStorage})")
    assert "eyJ" not in tokens  # ningún JWT en el almacenamiento del navegador
```

## 6. Seguridad (manual o DAST)

- **Enumeración por tiempo:** 50 intentos con documento existente y 50 con inexistente; la diferencia de medianas DEBERÍA ser < 50 ms.
- **Fuzzing:** bytes nulos (`%00`) y Unicode atípico en ambos campos → nunca 500.
- **Almacenamiento:** inspeccionar `localStorage`, `sessionStorage` y consola tras login y logout: sin contraseñas ni tokens.
