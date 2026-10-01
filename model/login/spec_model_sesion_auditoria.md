# Especificación de Modelos: `SesionUsuario` y `AuditoriaAcceso`
## Módulo de Login e Identidad — SDD Jolifoods (`DATA-SPEC-SESSION-002`)

Este documento define la especificación técnica de las entidades encargadas de gestionar las sesiones activas, la auditoría inmutable de accesos y la revocación de tokens JWT.

---

## 1. Entidad: `SesionUsuario` (Control de Sesiones Activas)

Gestiona la concurrencia, ubicación y ciclo de vida de los tokens emitidos.

### Diccionario de Campos
| Campo | Tipo de Dato | Nulo / Obligatorio | Restricciones | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **`id`** | `UUID` | Obligatorio (PK) | Default: `gen_random_uuid()` | Identificador universal único de la sesión. |
| **`usuario_id`** | `BIGINT` | Obligatorio (FK) | `ON DELETE CASCADE` | Colaborador al que pertenece la sesión. |
| **`jti`** | `VARCHAR(64)` | Obligatorio | **UNIQUE**, Indexado | Identificador único del JWT (*JWT ID Claim*). |
| **`ip_origen`** | `VARCHAR(45)` | Obligatorio | Admite IPv4 e IPv6 | Dirección IP desde donde se autenticó. |
| **`user_agent`** | `TEXT` | Obligatorio | Información de navegador y SO | Cadena completa del navegador para análisis forense. |
| **`dispositivo`** | `VARCHAR(50)` | Opcional | Valores: `Desktop`, `Mobile`, `Tablet`, `Kiosk` | Detección normalizada del dispositivo. |
| **`fecha_inicio`** | `TIMESTAMP` | Obligatorio | Default: `now()` | Momento en que se aprobó el inicio de sesión. |
| **`fecha_expiracion`** | `TIMESTAMP` | Obligatorio | Calculado según política | Momento exacto en que expira el refresh token. |
| **`is_activa`** | `BOOLEAN` | Obligatorio | Default: `true`, Indexado | `false` si el usuario hizo logout o fue cerrada remotamente. |
| **`fecha_cierre`** | `TIMESTAMP` | Opcional (Nullable) | Registrado al hacer logout | Momento voluntario de cierre de sesión. |

---

## 2. Entidad: `RegistroAuditoriaAcceso` (Bitácora Inmutable)

Registra de forma inmutable cada intento de acceso a la plataforma, ya sea exitoso o fallido, para auditorías de seguridad informática.

### Diccionario de Campos
| Campo | Tipo de Dato | Nulo / Obligatorio | Descripción |
| :--- | :--- | :--- | :--- |
| **`id`** | `BIGINT` | Obligatorio (PK) | Auto-incremental. |
| **`documento_ingresado`** | `VARCHAR(50)` | Obligatorio | Cédula o identificador digitado en el formulario. |
| **`usuario_id`** | `BIGINT` | Opcional (Nullable) | ForeignKey al usuario si existía en la base de datos. |
| **`evento`** | `VARCHAR(30)` | Obligatorio | Tipo de evento (ver catálogo de eventos abajo). |
| **`resultado`** | `VARCHAR(15)` | Obligatorio | `SUCCESS`, `FAILURE`, `BLOCKED`. |
| **`motivo_fallo`** | `VARCHAR(150)` | Opcional | Causa del rechazo (ej. `BAD_PASSWORD`, `INACTIVE_ACCOUNT`, `RATE_LIMIT_EXCEEDED`). |
| **`ip_origen`** | `VARCHAR(45)` | Obligatorio | IP del cliente. |
| **`user_agent`** | `TEXT` | Obligatorio | User agent de la solicitud. |
| **`fecha_evento`** | `TIMESTAMP` | Obligatorio | Default: `CURRENT_TIMESTAMP`. |
| **`tiempo_respuesta_ms`** | `INTEGER` | Opcional | Latencia de validación en milisegundos. |

### Catálogo Canónico de Eventos de Auditoría
- `LOGIN_SUCCESS_CREDENTIALS`: Inicio de sesión exitoso por cédula + contraseña.
- `LOGIN_SUCCESS_SSO`: Inicio de sesión exitoso por Microsoft 365 Azure AD.
- `LOGIN_SUCCESS_KIOSK`: Inicio de sesión operativo por cédula en quiosco.
- `LOGIN_FAILED_BAD_PASSWORD`: Contraseña errónea para un usuario existente.
- `LOGIN_FAILED_NOT_FOUND`: Número de documento no registrado en el sistema.
- `LOGIN_BLOCKED_INACTIVE`: Intento de ingreso de cuenta desactivada por RRHH.
- `LOGIN_BLOCKED_RATE_LIMIT`: Solicitud rechazada por exceder tasa de intentos.
- `LOGOUT_VOLUNTARY`: Cierre de sesión ejecutado por el colaborador.
- `SESSION_TIMEOUT_EXPIRED`: Sesión caducada por inactividad.

---

## 3. Entidad: `TokenListaNegra` (Revocación Instantánea)

Utilizada para invalidar tokens de refresco (*Refresh Tokens*) en casos de logout o revocación administrativa inmediata.

```sql
CREATE TABLE tokens_lista_negra (
    id BIGSERIAL PRIMARY KEY,
    jti VARCHAR(64) UNIQUE NOT NULL,
    usuario_id BIGINT REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_revocacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expira_original TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_tokens_blacklist_jti ON tokens_lista_negra(jti);
```
