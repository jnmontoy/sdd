# Modelos de Datos del Login — SDD
## Directorio: `.sdd/model/login/`

Especificación de datos del inicio de sesión y la identidad en Joli Foods. Cualquier implementación (Django ORM u otro) DEBE respetar los mismos campos, tipos, restricciones e índices. El DDL de referencia es para PostgreSQL.

---

## 1. Índice

| Archivo | Entidad | Contenido |
| :--- | :--- | :--- |
| [`spec_model_usuario.md`](./spec_model_usuario.md) | `Usuario` | Identidad: documento, correo, hash de clave (Django), roles M2M, estado y bloqueo. |
| [`spec_model_sesion_auditoria.md`](./spec_model_sesion_auditoria.md) | `SesionUsuario`, `RegistroAuditoriaAcceso`, lista negra | Sesiones activas, bitácora de accesos solo-inserción y revocación de refresh tokens. |
| [`spec_model_restablecimiento.md`](./spec_model_restablecimiento.md) | `TokenRestablecimientoClave` | Tokens de un solo uso (hash SHA-256, 15 min). |
| [`esquema_sql_canonico.md`](./esquema_sql_canonico.md) | DDL | `CREATE TABLE`, índices, restricciones y permisos de la bitácora. |
| [`implementacion_django_orm.md`](./implementacion_django_orm.md) | Código ORM | `AbstractBaseUser` + `PermissionsMixin` + `BaseUserManager` y demás modelos. |

Roles y sedes: [`../roles/spec_model_roles_permisos.md`](../roles/spec_model_roles_permisos.md).

---

## 2. Diagrama Entidad-Relación

```mermaid
erDiagram
    Sede ||--o{ Usuario : "ubica"
    Usuario }o--o{ Rol : "usuarios_roles"
    Usuario ||--o{ SesionUsuario : "mantiene"
    Usuario ||--o{ RegistroAuditoriaAcceso : "genera"
    Usuario ||--o{ TokenRestablecimientoClave : "solicita"

    Usuario {
        bigint id PK
        varchar password "Hash Django (Argon2id / PBKDF2)"
        varchar numero_documento UK "5-15 dígitos"
        varchar email UK "Único sin distinguir mayúsculas"
        varchar first_name
        varchar last_name
        boolean is_active
        boolean is_staff
        boolean is_superuser
        boolean debe_cambiar_clave
        int intentos_fallidos
        timestamptz bloqueado_hasta
        timestamptz last_login
        timestamptz date_joined
        bigint sede_id FK
        varchar cargo
        varchar empresa "Unidad de negocio"
        varchar avatar "Ruta relativa en media"
    }

    Rol {
        bigint id PK
        varchar codigo UK
        jsonb permisos "Claves modulo.accion"
        boolean exige_sso
    }

    SesionUsuario {
        uuid id PK
        bigint usuario_id FK
        varchar refresh_jti UK "jti del refresh vigente"
        inet ip_origen
        varchar user_agent
        timestamptz fecha_inicio
        timestamptz fecha_expiracion
        boolean is_activa
        timestamptz fecha_cierre
    }

    RegistroAuditoriaAcceso {
        bigint id PK
        varchar documento_ingresado
        bigint usuario_id FK "Nulo si no existe"
        varchar evento
        varchar resultado "SUCCESS | FAILURE | BLOCKED"
        inet ip_origen
        timestamptz fecha_evento
    }

    TokenRestablecimientoClave {
        bigint id PK
        bigint usuario_id FK
        char token_hash UK "SHA-256"
        timestamptz fecha_expiracion
        timestamptz usado_en "Nulo = sin usar"
    }
```

La lista negra de refresh tokens usa la app `rest_framework_simplejwt.token_blacklist` (no aparece en el diagrama).
