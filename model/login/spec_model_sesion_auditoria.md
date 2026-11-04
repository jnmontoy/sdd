# Especificación de Modelos: `SesionUsuario`, `RegistroAuditoriaAcceso` y lista negra de tokens
## Módulo de Login e Identidad — SDD Joli Foods (`DATA-SPEC-SESSION-002`)

Sesiones activas, bitácora de accesos (solo-inserción) y revocación de refresh tokens.

---

## 1. `SesionUsuario`

Una fila por inicio de sesión. Permite listar y cerrar sesiones desde el perfil y revocarlas todas al cambiar la contraseña.

| Campo | Tipo (PostgreSQL) | Nulo | Restricciones | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | No | PK, default `gen_random_uuid()` | Identificador de la sesión. |
| `usuario_id` | `BIGINT` | No | FK `usuarios(id)` `ON DELETE CASCADE` | Titular. |
| `refresh_jti` | `VARCHAR(64)` | No | **UNIQUE** | `jti` del refresh token vigente; se actualiza en cada rotación. |
| `ip_origen` | `INET` | No | | IP del inicio de sesión. |
| `user_agent` | `VARCHAR(512)` | No | Truncado a 512 | Navegador y sistema operativo. |
| `dispositivo` | `VARCHAR(10)` | Sí | `Desktop`, `Mobile`, `Tablet`, `Kiosk` | Tipo de dispositivo detectado. |
| `fecha_inicio` | `TIMESTAMPTZ` | No | default `now()` | Inicio. |
| `fecha_expiracion` | `TIMESTAMPTZ` | No | | Vencimiento del refresh vigente. |
| `is_activa` | `BOOLEAN` | No | default `true` | `false` tras logout, revocación o cambio de clave. |
| `fecha_cierre` | `TIMESTAMPTZ` | Sí | | Momento del cierre. |

Índice: `(usuario_id, is_activa)`.

---

## 2. `RegistroAuditoriaAcceso` (solo-inserción)

Cada intento de acceso, exitoso o fallido.

| Campo | Tipo (PostgreSQL) | Nulo | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | No | PK. |
| `documento_ingresado` | `VARCHAR(20)` | No | Documento digitado (ya validado como dígitos; nunca la contraseña). |
| `usuario_id` | `BIGINT` | Sí | FK `usuarios(id)` `ON DELETE SET NULL`; nulo si el documento no existe. |
| `evento` | `VARCHAR(40)` | No | Ver catálogo. |
| `resultado` | `VARCHAR(10)` | No | `SUCCESS`, `FAILURE`, `BLOCKED`. |
| `motivo_fallo` | `VARCHAR(150)` | Sí | Código del motivo (`BAD_PASSWORD`, `INACTIVE_ACCOUNT`, `RATE_LIMIT_EXCEEDED`…). |
| `ip_origen` | `INET` | No | IP del cliente (resuelta según proxies de confianza). |
| `user_agent` | `VARCHAR(512)` | No | Truncado a 512. |
| `fecha_evento` | `TIMESTAMPTZ` | No | default `now()`. |
| `tiempo_respuesta_ms` | `INTEGER` | Sí | Latencia de la verificación. |

Índices: `fecha_evento DESC`, `documento_ingresado`, `ip_origen`, `(usuario_id, fecha_evento DESC)`.

### Solo-inserción (DEBE)
- **Aplicación:** el modelo rechaza `save()` sobre una fila existente y `delete()`; el admin de Django la expone en solo lectura.
- **Base de datos:** el rol con el que corre la aplicación NO DEBE tener `UPDATE` ni `DELETE` sobre la tabla (ver DDL en [`esquema_sql_canonico.md`](./esquema_sql_canonico.md)). La depuración por retención la ejecuta un rol de mantenimiento distinto.
- **Por qué:** una bitácora que la propia aplicación puede editar no sirve como evidencia ante un incidente.

### Catálogo de eventos (fuente única)
`LOGIN_SUCCESS_CREDENTIALS`, `LOGIN_SUCCESS_SSO`, `LOGIN_SUCCESS_KIOSK`, `LOGIN_FAILED_BAD_PASSWORD`, `LOGIN_FAILED_NOT_FOUND`, `LOGIN_BLOCKED_INACTIVE`, `LOGIN_BLOCKED_SSO_REQUIRED`, `LOGIN_BLOCKED_RATE_LIMIT`, `TOKEN_REFRESH_REUSED`, `LOGOUT_VOLUNTARY`, `SESSION_EXPIRED`, `SESSION_REVOKED`, `PASSWORD_RESET_REQUESTED`, `PASSWORD_RESET_COMPLETED`, `PASSWORD_CHANGED`.

---

## 3. Lista negra de refresh tokens

En Django se usa la app **`rest_framework_simplejwt.token_blacklist`** (tablas `token_blacklist_outstandingtoken` y `token_blacklist_blacklistedtoken`), activada con `ROTATE_REFRESH_TOKENS` y `BLACKLIST_AFTER_ROTATION`. NO se define un modelo propio. Una tarea diaria DEBERÍA ejecutar `manage.py flushexpiredtokens`.

Para backends que no usen SimpleJWT, la tabla equivalente es:

```sql
CREATE TABLE tokens_lista_negra (
    id               BIGSERIAL PRIMARY KEY,
    jti              VARCHAR(64) NOT NULL UNIQUE,
    usuario_id       BIGINT REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_revocacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expira_original  TIMESTAMPTZ NOT NULL
);
-- La restricción UNIQUE ya indexa jti.
```
