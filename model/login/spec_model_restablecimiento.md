# Especificación de Modelo: `TokenRestablecimientoClave`
## Módulo de Login e Identidad — SDD Jolifoods (`DATA-SPEC-PWDRESET-003`)

Este documento define la entidad de base de datos para gestionar de forma segura los enlaces y tokens de un solo uso para la recuperación y restablecimiento de contraseñas olvidadas.

---

## 1. Diccionario de Campos de la Entidad `TokenRestablecimientoClave`

| Campo | Tipo de Dato | Nulo / Obligatorio | Restricciones / Índices | Descripción y Regla de Negocio |
| :--- | :--- | :--- | :--- | :--- |
| **`id`** | `BIGSERIAL` | Obligatorio (PK) | Auto-incremental | Identificador único de la solicitud de restablecimiento. |
| **`usuario_id`** | `BIGINT` | Obligatorio (FK) | `ON DELETE CASCADE` | Colaborador que solicitó el restablecimiento de su clave. |
| **`token_hash`** | `VARCHAR(64)` | Obligatorio | **UNIQUE**, **INDEX** | Hash criptográfico SHA-256 del token efímero enviado al correo. Nunca se almacena el token en texto plano en la base de datos. |
| **`fecha_creacion`** | `TIMESTAMP` | Obligatorio | Default: `now()` | Momento exacto en que se generó la solicitud. |
| **`fecha_expiracion`** | `TIMESTAMP` | Obligatorio | Indexado | Plazo de validez del enlace (fijado estrictamente en **15 minutos** desde la creación). |
| **`is_used`** | `BOOLEAN` | Obligatorio | Default: `false`, Indexado | Bandera que garantiza que el enlace sea de **un solo uso (One-Time Token)**. Una vez consumido pasa a `true`. |
| **`ip_solicitud`** | `VARCHAR(45)` | Obligatorio | IPv4 o IPv6 | Dirección IP desde donde se emitió la petición de recuperación. |
| **`ip_cambio`** | `VARCHAR(45)` | Opcional (Nullable) | IPv4 o IPv6 | Dirección IP desde donde efectivamente se definió la nueva clave. |
| **`user_agent_solicitud`**| `TEXT` | Obligatorio | Texto | Dispositivo y navegador que inició la solicitud. |

---

## 2. Reglas de Negocio e Invariantes del Modelo

1. **Un solo token activo por usuario**: Al generarse una nueva solicitud de recuperación para un usuario, cualquier token previo no utilizado debe ser marcado inmediatamente como `is_used = true` o revocado.
2. **Hash en Base de Datos**: El token generado es una cadena aleatoria de 32 bytes en base64url enviada exclusivamente en el enlace del correo. En la base de datos solo se persiste `SHA256(token)`. Si la base de datos es vulnerada, ningún atacante puede usar los hashes para cambiar contraseñas.
3. **Invalidez por Expiración**: Todo token con `now() > fecha_expiracion` se considera nulo automáticamente.
4. **Revocación Global de Sesiones**: Cuando un token es consumido exitosamente:
   - Se actualiza la contraseña del usuario.
   - Se marca `is_used = true`.
   - **Se revocan todas las sesiones activas previas** del colaborador en `sesiones_usuario` (`is_activa = false`).

---

## 3. Sentencia DDL SQL Estándar

```sql
CREATE TABLE tokens_restablecimiento_clave (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL,
    token_hash VARCHAR(64) NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    ip_solicitud VARCHAR(45) NOT NULL,
    ip_cambio VARCHAR(45) NULL,
    user_agent_solicitud TEXT NOT NULL,

    CONSTRAINT fk_token_pwd_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT uq_token_pwd_hash UNIQUE (token_hash)
);

CREATE INDEX idx_token_pwd_hash ON tokens_restablecimiento_clave(token_hash);
CREATE INDEX idx_token_pwd_validez ON tokens_restablecimiento_clave(usuario_id, is_used, fecha_expiracion);
```
