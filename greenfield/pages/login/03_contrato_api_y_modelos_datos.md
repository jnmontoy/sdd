# 03. Contratos de API y Modelos de Datos
## Módulo de Login / Autenticación — SDD Joli Foods (`SPEC-AUTH-001`)

Este documento es la fuente del contrato cliente-servidor del login. Las implementaciones (backend y cliente) DEBEN respetar estos nombres de campos, códigos HTTP y cabeceras. Los cambios se versionan según [`../../09_protocolo_gobernanza_apis_y_breaking_changes.md`](../../09_protocolo_gobernanza_apis_y_breaking_changes.md).

Las rutas del cliente se consumen desde `frontend/src/services/endpoints.ts` (`ENDPOINTS.AUTH.*`), nunca quemadas en componentes. Los datos de ejemplo son ficticios.

---

## 1. Modelo de Usuario expuesto al cliente (`UserEntity`)

```typescript
export interface UserEntity {
  id: number;
  /** Documento de identidad (solo dígitos) */
  numero_documento: string;
  nombre: string;
  apellidos: string;
  email: string;
  /** Códigos de los roles asignados (tabla Rol, relación M2M — BP-19) */
  roles: string[];
  /** Claves de permiso consolidadas (p. ej. "usuarios.ver"); la UI valida por permiso, no por rol */
  permisos: string[];
  cargo: string | null;
  sede: string | null;
  is_active: boolean;
  /** true si la cuenta debe cambiar su contraseña (primer ingreso o clave temporal) */
  debe_cambiar_clave: boolean;
  /** URL protegida del avatar (ver model/archivos) */
  avatar_url: string | null;
  last_login: string | null;
}
```

El modelo de persistencia está en [`../../../model/login/spec_model_usuario.md`](../../../model/login/spec_model_usuario.md).

---

## 2. Endpoints de Sesión

### Cabeceras y cookies comunes

| Elemento | Valor |
| :--- | :--- |
| Cookie de refresh | `refresh_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/api/v1/auth/; Max-Age=43200` |
| Cookie CSRF | `csrftoken=<valor>; Secure; SameSite=Lax; Path=/` (no HttpOnly, el cliente la lee) |
| Cabecera CSRF | `X-CSRFToken: <valor de csrftoken>` — obligatoria en `/auth/refresh/` y `/auth/logout/` |
| Autorización | `Authorization: Bearer <access>` en las demás rutas autenticadas |
| Cliente | Todas las llamadas a `/api/v1/auth/` usan `withCredentials: true` |

### 2.1. `POST /api/v1/auth/login/`

- **Autenticación:** pública.
- **Límite:** ver [`05_seguridad_auditoria_y_hardening.md`](./05_seguridad_auditoria_y_hardening.md) §3.

#### Cuerpo de la petición
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "LoginCredentialsPayload",
  "type": "object",
  "properties": {
    "numero_documento": { "type": "string", "pattern": "^[0-9]{5,15}$" },
    "password":  { "type": "string", "minLength": 1, "maxLength": 128 }
  },
  "required": ["numero_documento", "password"],
  "additionalProperties": false
}
```
"Recordar mi documento" es una preferencia del cliente y **no** se envía al servidor.

#### 200 OK
Cabeceras: `Set-Cookie: refresh_token=...` y `Set-Cookie: csrftoken=...` (ver tabla).
```json
{
  "access": "<JWT de acceso>",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": 101,
    "numero_documento": "1000000001",
    "nombre": "Usuario",
    "apellidos": "Ejemplo",
    "email": "usuario@ejemplo.com",
    "roles": ["OPERADOR"],
    "permisos": ["dashboard.ver", "usuarios.ver"],
    "cargo": "Analista",
    "sede": "Sede principal",
    "is_active": true,
    "debe_cambiar_clave": false,
    "avatar_url": null,
    "last_login": "2026-11-04T13:00:00Z"
  }
}
```

#### Errores (formato único)
```json
{ "error_code": "INVALID_CREDENTIALS", "message": "Documento o contraseña incorrectos." }
```

| HTTP | `error_code` | Cuándo |
| :--- | :--- | :--- |
| 400 | `VALIDATION_ERROR` | Payload inválido (incluye `details` por campo). |
| 401 | `INVALID_CREDENTIALS` | Documento inexistente **o** contraseña errada (mismo cuerpo, mismo tiempo aproximado). |
| 403 | `SSO_REQUIRED` | Contraseña válida pero el rol exige Microsoft SSO. |
| 403 | `USER_INACTIVE` | Contraseña válida pero cuenta inactiva. |
| 429 | `RATE_LIMIT_EXCEEDED` | Bloqueo temporal. Incluye cabecera `Retry-After` (segundos) y `retry_after_seconds`. |

Los errores NO DEBEN incluir trazas, nombres de tablas ni detalles internos.

### 2.2. `POST /api/v1/auth/check-user/` (pre-chequeo de método)

- **Autenticación:** pública, con el mismo límite de tasa que el login.
- **Petición:** `{ "numero_documento": "1000000001" }`
- **Respuesta 200 (siempre):**
```json
{ "metodo": "PASSWORD" }
```
o `{ "metodo": "SSO" }`. Para documentos inexistentes o inactivos DEBE responder `PASSWORD`, igual que para una cuenta normal. NO DEBE devolver nombre, existencia, estado ni rol.
- **Riesgo aceptado:** la respuesta `SSO` revela que el documento pertenece a una cuenta privilegiada; se mitiga con el límite de tasa. Si el proyecto no lo acepta, PUEDE omitir este endpoint y mostrar siempre ambos métodos.

### 2.3. `POST /api/v1/auth/refresh/`

- **Autenticación:** cookie `refresh_token` + cabecera `X-CSRFToken`. El refresh **no** se envía en el cuerpo ni en `Authorization`.
- **200 OK:** rota la cookie (`Set-Cookie: refresh_token=<nuevo>`) y devuelve:
```json
{ "access": "<JWT de acceso>", "token_type": "Bearer", "expires_in": 900 }
```
- **401 `REFRESH_INVALID`:** cookie ausente, vencida, en lista negra o usuario inactivo. Responde además `Set-Cookie: refresh_token=; Max-Age=0`.
- **403 `CSRF_FAILED`:** falta o no coincide la cabecera CSRF.

### 2.4. `POST /api/v1/auth/logout/`

- **Autenticación:** cookie `refresh_token` + `X-CSRFToken`. Es idempotente: responde 204 aunque la cookie ya no sea válida.
- **Efecto:** refresh en lista negra, `SesionUsuario.is_activa = false`, `Set-Cookie: refresh_token=; Path=/api/v1/auth/; Max-Age=0`.
- **204 No Content.**

### 2.5. `GET /api/v1/auth/me/`

- **Autenticación:** `Authorization: Bearer <access>`.
- **200 OK:** `UserEntity`.

### 2.6. `GET /api/v1/auth/microsoft/login/` y `GET /api/v1/auth/microsoft/callback/`

Flujo de navegación completo (302), no AJAX. Ver secuencia en [`02_arquitectura_y_maquina_estados.md`](./02_arquitectura_y_maquina_estados.md) §2.2. El callback termina en una redirección al frontend (`/auth/callback`) **sin** tokens en la URL; si falla, redirige a `/login?error=sso_failed`.

---

## 3. Endpoints de Restablecimiento de Contraseña

El detalle del flujo y sus reglas de seguridad está en [`09_flujo_restablecimiento_contrasena.md`](./09_flujo_restablecimiento_contrasena.md).

| Método y ruta | Petición | Respuesta |
| :--- | :--- | :--- |
| `POST /api/v1/auth/password-reset/request/` | `{ "identificador": "1000000001" }` (documento o correo) | **202** siempre, con el mismo cuerpo exista o no la cuenta. |
| `POST /api/v1/auth/password-reset/validate/` | `{ "token": "<token del enlace>" }` | 200 `{ "valid": true }` o 400 `TOKEN_EXPIRED_OR_INVALID`. |
| `POST /api/v1/auth/password-reset/confirm/` | `{ "token": "...", "new_password": "<NUEVA_CONTRASEÑA>", "confirm_password": "<NUEVA_CONTRASEÑA>" }` | 200 o 400 (`TOKEN_EXPIRED_OR_INVALID`, `PASSWORD_POLICY`, `PASSWORD_MISMATCH`). |

---

## 4. Registro en `ENDPOINTS` (cliente)

```ts
// frontend/src/services/endpoints.ts (fragmento del grupo AUTH)
AUTH: {
  LOGIN: '/api/v1/auth/login/',
  CHECK_USER: '/api/v1/auth/check-user/',
  REFRESH: '/api/v1/auth/refresh/',
  LOGOUT: '/api/v1/auth/logout/',
  ME: '/api/v1/auth/me/',
  MICROSOFT_LOGIN: '/api/v1/auth/microsoft/login/',
  PASSWORD_RESET_REQUEST: '/api/v1/auth/password-reset/request/',
  PASSWORD_RESET_VALIDATE: '/api/v1/auth/password-reset/validate/',
  PASSWORD_RESET_CONFIRM: '/api/v1/auth/password-reset/confirm/',
  CHANGE_PASSWORD: '/api/v1/auth/change-password/',
},
```
