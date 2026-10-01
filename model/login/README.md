# Especificación de Modelos de Datos para Login — SDD
## Directorio: `.sdd/model/login/`

Este directorio define la **especificación formal de datos (Data Models)** para el módulo de inicio de sesión y gestión de identidad corporativa en el ecosistema **Jolifoods / Greenyard**.

Garantiza que cualquier base de datos (PostgreSQL, SQLite, MySQL) o cualquier ORM (Django ORM, SQLAlchemy, Prisma, TypeORM) implemente exactamente los mismos campos, tipos de datos, restricciones de integridad, índices y mecanismos de auditoría.

---

## 1. Índice de Especificaciones de Modelos

| Archivo | Modelo / Entidad | Propósito y Contenido |
| :--- | :--- | :--- |
| **[`spec_model_usuario.md`](./spec_model_usuario.md)** | **`Usuario` (User Entity)** | Modelo principal de identidad: documento (cédula), email, hash de clave, roles, estado activo y control de fuerza bruta. |
| **[`spec_model_sesion_auditoria.md`](./spec_model_sesion_auditoria.md)** | **`SesionUsuario` & `AuditoriaAcceso`** | Registro inmutable de cada intento de acceso, IP, agente de usuario, token JTI y trazabilidad de sesiones activas. |
| **[`spec_model_restablecimiento.md`](./spec_model_restablecimiento.md)** | **`TokenRestablecimientoClave`** | Tokens criptográficos efímeros (15 min) de un solo uso para recuperación segura de contraseñas. |
| **[`esquema_sql_canonico.md`](./esquema_sql_canonico.md)** | **DDL SQL Universal** | Sentencias `CREATE TABLE`, `CREATE INDEX` y restricciones relacionales agnósticas de motor. |
| **[`implementacion_django_orm.md`](./implementacion_django_orm.md)** | **Código de Referencia ORM** | Implementación completa lista para usar en Django (`AbstractBaseUser`, `BaseUserManager`, `PermissionsMixin`). |

---

## 2. Diagrama Entidad-Relación (ERD)

```mermaid
erDiagram
    Usuario ||--o{ SesionUsuario : "mantiene"
    Usuario ||--o{ RegistroAuditoriaAcceso : "genera"
    Usuario ||--o{ TokenListaNegra : "posee"

    Usuario {
        bigint id PK
        varchar numero_documento UK "Cédula indexada (5-15 dígitos)"
        varchar email UK "Correo corporativo único"
        varchar password_hash "Hash criptográfico seguro (PBKDF2/Argon2)"
        varchar first_name "Nombres del colaborador"
        varchar last_name "Apellidos del colaborador"
        varchar tipo "Administrador | Colaborador | Operario | Auditor"
        boolean is_active "Estado de habilitación en plataforma"
        boolean is_staff "Acceso al panel administrativo"
        boolean is_superuser "Permisos totales de sistema"
        int intentos_fallidos "Contador para rate limiting"
        timestamp bloqueado_hasta "Enfriamiento por fuerza bruta"
        timestamp last_login "Último acceso exitoso"
        timestamp date_joined "Fecha de creación del registro"
        varchar avatar_url "Ruta o URI de foto de perfil"
        varchar cargo "Puesto formal"
        varchar empresa "Unidad de negocio Jolifoods"
    }

    SesionUsuario {
        uuid id PK
        bigint usuario_id FK "Referencia al Usuario"
        varchar jti UK "JWT ID único para trazabilidad"
        varchar ip_origen "Dirección IP de conexión"
        text user_agent "Navegador y sistema operativo"
        timestamp fecha_inicio "Momento del login"
        timestamp fecha_expiracion "Vencimiento del refresh token"
        boolean is_activa "Bandera de sesión vigente"
        timestamp fecha_cierre "Momento de logout voluntario"
    }

    RegistroAuditoriaAcceso {
        bigint id PK
        varchar documento_ingresado "Cédula digitada en login"
        bigint usuario_id FK "Null si no existe"
        varchar evento "LOGIN_SUCCESS | BAD_PASSWORD | USER_NOT_FOUND | BLOCKED"
        varchar ip_origen "IP pública o interna"
        text user_agent "Dispositivo detectado"
        timestamp fecha_evento "Timestamp exacto del intento"
        int tiempo_respuesta_ms "Latencia de verificación"
    }

    TokenListaNegra {
        bigint id PK
        varchar jti UK "Identificador del JWT revocado"
        timestamp fecha_revocacion "Momento del baneo/logout"
        timestamp expira_original "Para limpieza periódica"
    }
```
