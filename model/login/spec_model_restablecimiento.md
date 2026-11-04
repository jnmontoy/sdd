# Especificación de Modelo: `TokenRestablecimientoClave`
## Módulo de Login e Identidad — SDD Joli Foods (`DATA-SPEC-PWDRESET-003`)

Tokens de un solo uso para restablecer contraseñas olvidadas. Flujo completo: [`../../greenfield/pages/login/09_flujo_restablecimiento_contrasena.md`](../../greenfield/pages/login/09_flujo_restablecimiento_contrasena.md).

---

## 1. Diccionario de Campos

| Campo | Tipo (PostgreSQL) | Nulo | Restricciones | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | No | PK | Identificador. |
| `usuario_id` | `BIGINT` | No | FK `usuarios(id)` `ON DELETE CASCADE` | Titular de la solicitud. |
| `token_hash` | `CHAR(64)` | No | **UNIQUE** | SHA-256 (hex) del token enviado por correo. El token en claro nunca se guarda. |
| `fecha_creacion` | `TIMESTAMPTZ` | No | default `now()` | Momento de la solicitud. |
| `fecha_expiracion` | `TIMESTAMPTZ` | No | | `fecha_creacion + 15 min` (`PASSWORD_RESET_MINUTES`). |
| `usado_en` | `TIMESTAMPTZ` | Sí | | Momento en que se consumió o invalidó. `NULL` = sin usar. |
| `ip_solicitud` | `INET` | No | | IP que hizo la solicitud. |
| `ip_cambio` | `INET` | Sí | | IP que fijó la nueva clave. |
| `user_agent_solicitud` | `VARCHAR(512)` | No | Truncado a 512 | Navegador que inició la solicitud. |

Índices: UNIQUE en `token_hash` (la restricción ya crea el índice); `(usuario_id, usado_en, fecha_expiracion)` para invalidar tokens vigentes de un usuario.

---

## 2. Invariantes (DEBE)

1. **Hash en base de datos:** el token es `secrets.token_urlsafe(32)`; se guarda `sha256(token).hexdigest()` y la búsqueda se hace por ese hash. **Por qué:** una copia robada de la BD no sirve para cambiar contraseñas.
2. **Un solo token vigente:** al crear uno nuevo, los previos del usuario con `usado_en IS NULL` reciben `usado_en = now()` en la misma transacción.
3. **Vigencia:** el token es válido solo si `usado_en IS NULL` y `now() <= fecha_expiracion`.
4. **Consumo atómico:** `transaction.atomic()` + `select_for_update()`; se fija `usado_en` y `ip_cambio`, se cambia la clave con `set_password()` y se revocan **todas** las sesiones del usuario (refresh tokens a lista negra y `SesionUsuario.is_activa = false`).
5. **Limpieza:** una tarea periódica DEBERÍA borrar tokens con `fecha_expiracion` anterior a 30 días.

---

## 3. DDL (PostgreSQL)

```sql
CREATE TABLE tokens_restablecimiento_clave (
    id                   BIGSERIAL PRIMARY KEY,
    usuario_id           BIGINT       NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token_hash           CHAR(64)     NOT NULL,
    fecha_creacion       TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion     TIMESTAMPTZ  NOT NULL,
    usado_en             TIMESTAMPTZ  NULL,
    ip_solicitud         INET         NOT NULL,
    ip_cambio            INET         NULL,
    user_agent_solicitud VARCHAR(512) NOT NULL DEFAULT '',
    CONSTRAINT uq_token_pwd_hash UNIQUE (token_hash),
    CONSTRAINT chk_token_pwd_expiracion CHECK (fecha_expiracion > fecha_creacion)
);

CREATE INDEX idx_token_pwd_vigencia ON tokens_restablecimiento_clave (usuario_id, usado_en, fecha_expiracion);
```

El código Django equivalente está en [`implementacion_django_orm.md`](./implementacion_django_orm.md).
