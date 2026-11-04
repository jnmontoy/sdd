# Especificación del Modelo: `Usuario`
## Módulo de Login e Identidad — SDD Joli Foods (`DATA-SPEC-USER-001`)

Entidad de identidad sobre la que descansan autenticación, autorización y trazabilidad. Implementación: [`implementacion_django_orm.md`](./implementacion_django_orm.md). DDL: [`esquema_sql_canonico.md`](./esquema_sql_canonico.md).

---

## 1. Diseño en Django

- `Usuario` hereda de **`AbstractBaseUser` + `PermissionsMixin`** y usa un **`UsuarioManager(BaseUserManager)`** propio.
- `USERNAME_FIELD = 'numero_documento'`; `REQUIRED_FIELDS = ['email', 'first_name', 'last_name']`.
- `AUTH_USER_MODEL = 'auth_core.Usuario'` DEBE fijarse antes de la primera migración. **Por qué:** cambiar el modelo de usuario después exige rehacer migraciones y datos.
- Los **roles** NO son un campo de texto del usuario: se asignan por la relación muchos-a-muchos `roles` con la tabla `Rol` (BP-19, ver [`../roles/spec_model_roles_permisos.md`](../roles/spec_model_roles_permisos.md)).
- La contraseña la gestiona Django (`set_password`, `check_password`) con `PASSWORD_HASHERS` (Argon2id primero, PBKDF2 alternativa). NO DEBE implementarse hashing propio.

---

## 2. Diccionario de Campos

| Campo | Tipo (PostgreSQL) | Nulo | Restricciones | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | No | PK | Identificador interno. |
| `password` | `VARCHAR(128)` | No | Heredado de `AbstractBaseUser` | Cadena `algoritmo$parámetros$salt$hash`. Nunca texto plano. Cuentas solo-SSO usan contraseña inutilizable (`set_unusable_password`). |
| `last_login` | `TIMESTAMPTZ` | Sí | Heredado | Último ingreso exitoso. |
| `is_superuser` | `BOOLEAN` | No | Heredado de `PermissionsMixin`, default `false` | Todos los permisos de Django admin. |
| `numero_documento` | `VARCHAR(15)` | No | **UNIQUE**, CHECK `^[0-9]{5,15}$` | Documento de identidad, solo dígitos. |
| `email` | `VARCHAR(254)` | No | **UNIQUE** sobre `LOWER(email)` | Correo; el manager lo guarda en minúsculas. |
| `first_name` | `VARCHAR(150)` | No | | Nombres. |
| `last_name` | `VARCHAR(150)` | No | | Apellidos. |
| `is_active` | `BOOLEAN` | No | default `true` | Cuenta habilitada. Las bajas son lógicas (`false`), no borrados físicos. |
| `is_staff` | `BOOLEAN` | No | default `false` | Acceso a Django admin. |
| `debe_cambiar_clave` | `BOOLEAN` | No | default `true` | Obliga a cambiar la contraseña en el primer ingreso o tras una clave temporal. |
| `intentos_fallidos` | `INTEGER` | No | default `0`, CHECK `>= 0` | Contador persistente para bloqueo prolongado (el límite de corto plazo vive en Redis, ver login/05 §3). |
| `bloqueado_hasta` | `TIMESTAMPTZ` | Sí | Índice | Bloqueo prolongado por reincidencia o decisión de seguridad. |
| `date_joined` | `TIMESTAMPTZ` | No | default `now()` | Creación de la cuenta. |
| `sede_id` | `BIGINT` | Sí | FK `organizacion_sede(id)` `ON DELETE SET NULL` | Sede principal. |
| `cargo` | `VARCHAR(120)` | Sí | | Cargo. |
| `empresa` | `VARCHAR(120)` | Sí | | Unidad de negocio (p. ej. corporativo, Colorisa, Inali). PUEDE convertirse en FK a un catálogo. |
| `avatar` | `VARCHAR(500)` | Sí | Ruta relativa en `MEDIA_ROOT` | Foto de perfil. Se valida tipo y tamaño (ver [`../archivos/spec_model_archivos_media.md`](../archivos/spec_model_archivos_media.md)). |

Tablas de relación:

| Tabla | Origen | Contenido |
| :--- | :--- | :--- |
| `usuarios_roles` | `Usuario.roles` (M2M) | `usuario_id`, `rol_id`, UNIQUE (`usuario_id`, `rol_id`). |
| `usuarios_groups`, `usuarios_user_permissions` | `PermissionsMixin` | Grupos y permisos nativos de Django (los genera la migración). |

---

## 3. Índices

| Índice | Columnas | Motivo |
| :--- | :--- | :--- |
| `uq_usuario_documento` | `numero_documento` (UNIQUE) | Búsqueda en login. La restricción UNIQUE ya crea el índice; no se duplica. |
| `uq_usuario_email_ci` | `LOWER(email)` (UNIQUE) | Unicidad sin distinguir mayúsculas y búsqueda en restablecimiento. |
| `idx_usuario_activo` | `is_active` | Listados filtrados por estado. |
| `idx_usuario_bloqueo` | `bloqueado_hasta` | Desbloqueos programados. |

---

## 4. Métodos

| Método | Comportamiento |
| :--- | :--- |
| `is_locked() -> bool` | `True` si `bloqueado_hasta` no es nulo y es posterior a `now()`. |
| `register_failed_attempt(max_attempts=5, lock_minutes=60)` | Incrementa `intentos_fallidos` de forma **atómica** (`F('intentos_fallidos') + 1`); si alcanza el umbral, fija `bloqueado_hasta`. **Por qué atómico:** dos intentos simultáneos no deben perder un incremento. |
| `reset_failed_attempts()` | Pone el contador en 0 y `bloqueado_hasta` en nulo tras un login exitoso. |
| `exige_sso` (propiedad) | `True` si algún rol activo del usuario tiene `exige_sso = True`. |
| `get_permisos() -> set[str]` | Unión de las claves de permiso de sus roles activos (para `/api/v1/mis-permisos/`). |
| `check_password(raw)` | Heredado de Django: verificación en tiempo constante y rehash automático si cambia el algoritmo preferido. |
