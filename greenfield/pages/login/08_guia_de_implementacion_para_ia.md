# 08. Guía de Implementación Paso a Paso (para IA y desarrolladores)
## Módulo de Login / Autenticación — SDD Joli Foods (`SPEC-AUTH-001`)

Cómo generar el login a partir de esta especificación, sin suponer rutas locales absolutas.

---

## 0. Paso previo: nombre del proyecto

La IA DEBE preguntar el nombre del proyecto antes de escribir código: *"¿Cuál es el nombre del proyecto o módulo? (ej. Control de Inventario, Registro de Visitantes)"*. Con él:

1. Copia los logos de `.sdd/assets/` (`Jolifoods.svg`, `Joli.svg`, `logoJoli.png`) a `frontend/src/assets/`.
2. Configura `index.html`:
   ```html
   <title>[Nombre del proyecto] | Joli Foods</title>
   <link rel="icon" type="image/svg+xml" href="/src/assets/Jolifoods.svg" />
   ```
3. Define `VITE_APP_SLUG=<slug-del-proyecto>` en `frontend/.env` (prefijo de las claves de almacenamiento; evita choques entre apps del mismo dominio).
4. En `LoginPage.tsx`: título H1 = nombre del proyecto; pie = `Joli Foods • Acceso corporativo`.

---

## 1. Estructura a Generar

```
./
├── .env.example
├── .gitignore
├── .venv/                          # entorno virtual (BP-15)
├── .vscode/settings.json
├── docker-compose.yml
├── pytest.ini                      # testpaths = pruebas
├── pruebas/                        # BP-17 (ver 07_plan_de_pruebas_y_matriz_qa.md)
│   ├── unitarias/
│   ├── integracion/
│   └── e2e/
├── frontend/                       # React + Vite + Bootstrap 5 + TypeScript
│   └── src/
│       ├── assets/Jolifoods.svg
│       ├── styles/variables.css    # copia de .sdd/components/variables.css
│       ├── config/storageKeys.ts   # STORAGE_KEYS con slug de la app
│       ├── schemas/auth.schema.ts  # Zod (conforme a 03)
│       ├── types/auth.types.ts
│       ├── services/
│       │   ├── endpoints.ts        # ENDPOINTS (fuente única de rutas)
│       │   └── apiClient.ts        # axios: Bearer desde memoria, withCredentials, X-CSRFToken, cola de refresh
│       ├── context/AuthContext.tsx # access token en memoria, refresh al montar, logout
│       ├── components/
│       │   ├── auth/LoginForm.tsx
│       │   ├── auth/MicrosoftButton.tsx
│       │   └── ToastNotification.tsx
│       └── pages/
│           ├── LoginPage.tsx
│           ├── AuthCallbackPage.tsx      # destino del SSO: llama a /auth/refresh/
│           └── PasswordResetPage.tsx     # flujo de 09
└── backend/                        # Django + DRF (+ FastAPI montado en ASGI para /fast/v1)
    ├── requirements.txt            # .sdd/stack/requirements.txt
    ├── config/
    │   ├── asgi.py
    │   ├── settings.py             # ver Paso B-3
    │   └── urls.py                 # /api/v1/auth/ → apps.auth_core.urls
    └── apps/auth_core/
        ├── models.py               # .sdd/model/login/implementacion_django_orm.md
        ├── serializers.py
        ├── views.py                # login, check-user, refresh, logout, me, password-reset, microsoft
        ├── cookies.py              # set/delete de la cookie refresh_token
        ├── throttling.py           # límite por documento e IP (Redis)
        └── urls.py
```

Referencias de componentes: [`AuthContext`](../../../components/context/auth_context.md), [`api_client`](../../../components/services/api_client.md), [`endpoints_registry`](../../../components/services/endpoints_registry.md), [`ProtectedRoute`](../../../components/routing/protected_route.md), [`SessionExpirationModal`](../../../components/modal/session_expiration_modal.md). Composición de la página: [`11_componentes_de_la_pagina.md`](./11_componentes_de_la_pagina.md).

---

## 2. Frontend

### F-1. Esquema Zod (`schemas/auth.schema.ts`)
```ts
import { z } from 'zod';

export const loginSchema = z.object({
  numero_documento: z.string().trim().regex(/^[0-9]{5,15}$/, 'Ingresa entre 5 y 15 dígitos, sin puntos ni espacios.'),
  password: z.string().min(1, 'Ingresa tu contraseña.').max(128),
  rememberMe: z.boolean(),
});
export type LoginFormData = z.infer<typeof loginSchema>;
```

### F-2. Claves de almacenamiento (`config/storageKeys.ts`)
```ts
const APP = import.meta.env.VITE_APP_SLUG ?? 'app';
export const STORAGE_KEYS = {
  theme: `${APP}:theme`,
  rememberedDoc: `${APP}:remembered_doc`,
  columnWidths: (modulo: string) => `${APP}:${modulo}:col_widths`,
  visibleColumns: (modulo: string) => `${APP}:${modulo}:visible_columns`,
  pwaDismissed: `${APP}:pwa_dismissed`,
} as const;

/** Acceso a localStorage tolerante a modo privado o storage bloqueado. */
export const safeStorage = {
  get(key: string): string | null {
    try { return window.localStorage.getItem(key); } catch { return null; }
  },
  set(key: string, value: string): void {
    try { window.localStorage.setItem(key, value); } catch { /* storage no disponible */ }
  },
  remove(key: string): void {
    try { window.localStorage.removeItem(key); } catch { /* noop */ }
  },
};
```
Es el mismo archivo que define [`auth_context.md`](../../../components/context/auth_context.md) §2.1.
`localStorage` solo guarda preferencias no sensibles. Tokens y contraseñas NO DEBEN guardarse en ningún almacenamiento del navegador.

### F-3. Cliente HTTP y `AuthContext`
- `apiClient` (axios) DEBE: enviar `Authorization: Bearer <access>` desde una variable de módulo (`setAccessToken()`); usar `withCredentials: true` en `/api/v1/auth/`; leer la cookie `csrftoken` y enviarla como `X-CSRFToken` en `refresh` y `logout`; ante 401 hacer **un** refresh compartido por las peticiones concurrentes y, si falla, despachar `window.dispatchEvent(new Event('session-expired'))`.
- `AuthContext` DEBE: al montar, llamar `POST ENDPOINTS.AUTH.REFRESH` (con `AbortController` limpiado en el desmontaje) para recuperar sesión; exponer `login()`, `logout()`, `user`, `isAuthenticated`, `isLoading`; en `logout()` llamar al backend y luego borrar el access de memoria aunque la llamada falle.

### F-4. Formulario (`components/auth/LoginForm.tsx`)
- Código de referencia completo en [`11_componentes_de_la_pagina.md`](./11_componentes_de_la_pagina.md) §3.
- Estilos con tokens de [`06_ui_ux_diseno_y_accesibilidad.md`](./06_ui_ux_diseno_y_accesibilidad.md) y clases `joli-login-*`.
- Íconos `Eye`/`EyeOff`/`Loader2` de `lucide-react`.

### F-5. Notificaciones
- Usar `showToast` de [`toast_notification.md`](../../../components/toast/toast_notification.md); montar `<CorporateToaster />` una sola vez en la raíz de la app.
- NO DEBE usarse `alert()` nativo. **Por qué:** bloquea el hilo, no es accesible ni estilizable.

---

## 3. Backend

### B-0. Entorno virtual (BP-15)
Todo comando Python DEBE ejecutarse con el intérprete de `.venv`. **Por qué:** evita contaminar el Python global y garantiza versiones reproducibles.
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```
```bash
./.venv/bin/python -m pip install -r backend/requirements.txt
```
`.vscode/settings.json`: `"python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe"` y `"python.terminal.activateEnvironment": true`.

### B-1. Modelos
Copiar [`../../../model/login/implementacion_django_orm.md`](../../../model/login/implementacion_django_orm.md) y [`../../../model/roles/spec_model_roles_permisos.md`](../../../model/roles/spec_model_roles_permisos.md). `AUTH_USER_MODEL = 'auth_core.Usuario'` DEBE definirse **antes** de la primera migración.

### B-2. Consultas sin N+1
La carga del usuario autenticado DEBERÍA hacerse en una sola consulta con sus relaciones:
```python
Usuario.objects.select_related('sede').prefetch_related('roles').get(pk=user_id)
```
Los permisos consolidados se calculan una vez por petición (o se cachean por usuario con invalidación al cambiar roles).

### B-3. Configuración (`settings.py`, fragmento)
```python
import os
from datetime import timedelta

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",   # requiere argon2-cffi
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
INSTALLED_APPS += ["rest_framework_simplejwt.token_blacklist"]
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "15"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=int(os.environ.get("JWT_REFRESH_HOURS", "12"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.environ["JWT_SIGNING_KEY"],   # sin valor por defecto: falla si no está
    "UPDATE_LAST_LOGIN": True,
}
REFRESH_COOKIE = {
    "key": "refresh_token",
    "httponly": True,
    "secure": not DEBUG,
    "samesite": "Lax",
    "path": "/api/v1/auth/",
}
CSRF_COOKIE_HTTPONLY = False      # el cliente debe leer csrftoken
CSRF_COOKIE_SECURE = not DEBUG
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [o for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
```

### B-4. Vistas
- `login`: valida serializer → límite (Redis) → `authenticate()` (usa el hasher de Django) → verifica `exige_sso` e `is_active` → emite `RefreshToken.for_user(user)` → fija cookie con `response.set_cookie(**REFRESH_COOKIE, value=str(refresh), max_age=...)` → devuelve `access` en el cuerpo.
- `refresh`: decorada con `@csrf_protect`; lee `request.COOKIES['refresh_token']`, usa `TokenRefreshSerializer`, rota la cookie.
- `logout`: `@csrf_protect`; `RefreshToken(cookie).blacklist()` dentro de `try` (idempotente), `response.delete_cookie('refresh_token', path='/api/v1/auth/')`.
- Toda operación con 2 o más escrituras (sesión + bitácora + `last_login`) DEBE ir en `transaction.atomic()` (BP-12).
- Si se exponen vistas en FastAPI (`/fast/v1/...`), las llamadas al ORM dentro de `async def` DEBEN envolverse en `sync_to_async`.

---

## 4. Reglas para la IA

1. NO DEBE inventar campos de payload: los nombres coinciden con [`03_contrato_api_y_modelos_datos.md`](./03_contrato_api_y_modelos_datos.md).
2. NO DEBE guardar contraseñas ni tokens en texto claro: ni en `localStorage`/`sessionStorage`, ni en logs, ni en base de datos.
3. NO DEBE usar rutas absolutas de disco ni URLs quemadas: rutas desde `ENDPOINTS`; configuración desde `import.meta.env` o `os.environ`.
4. NO DEBE dejar secretos con valor por defecto (`JWT_SIGNING_KEY`, `SECRET_KEY`).
5. Los mensajes al usuario DEBEN estar en español claro.
6. Todo comando Python DEBE ejecutarse con `.venv` (BP-15).
7. Las pruebas DEBEN quedar en `pruebas/` (BP-17) y cubrir la matriz de [`07_plan_de_pruebas_y_matriz_qa.md`](./07_plan_de_pruebas_y_matriz_qa.md).
