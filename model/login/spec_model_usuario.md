# Especificación del Modelo: `Usuario` (User Entity)
## Módulo de Login e Identidad — SDD Jolifoods (`DATA-SPEC-USER-001`)

Este documento define la especificación técnica inmutable de la entidad **`Usuario`**, el modelo de datos medular sobre el cual descansa la autenticación, autorización y trazabilidad de identidad de la plataforma.

---

## 1. Diccionario de Campos de la Entidad `Usuario`

| Nombre del Campo | Tipo de Dato | Nulo / Obligatorio | Restricciones / Índices | Descripción y Regla de Negocio |
| :--- | :--- | :--- | :--- | :--- |
| **`id`** | `BIGINT` | Obligatorio (PK) | Auto-incremental / Primary Key | Identificador único numérico en la base de datos. |
| **`numero_documento`** | `VARCHAR(15)` | **Obligatorio** | **UNIQUE**, **INDEX**, Regex: `^[0-9]{5,15}$` | Número de cédula de ciudadanía o documento oficial. No admite letras ni caracteres especiales. |
| **`email`** | `VARCHAR(254)` | **Obligatorio** | **UNIQUE**, **INDEX**, Formato Email | Correo electrónico corporativo o personal del colaborador. |
| **`password`** | `VARCHAR(255)` | Obligatorio | Formato Hash Seguro | Cadena que contiene el algoritmo, salt e iteraciones (PBKDF2/Bcrypt/Argon2). Nunca texto plano. |
| **`first_name`** | `VARCHAR(150)` | Obligatorio | Longitud máxima 150 | Nombres del usuario según documento oficial. |
| **`last_name`** | `VARCHAR(150)` | Obligatorio | Longitud máxima 150 | Apellidos del usuario según documento oficial. |
| **`tipo`** | `VARCHAR(20)` | **Obligatorio** | Valores: `Administrador`, `Colaborador`, `Operario`, `Auditor` | Rol jerárquico de seguridad. Los `Administrador` deben autenticarse obligatoriamente mediante SSO. |
| **`is_active`** | `BOOLEAN` | Obligatorio | Default: `true` | Determina si la cuenta está habilitada. Si es `false`, el login rechaza el acceso con HTTP 403. |
| **`is_staff`** | `BOOLEAN` | Obligatorio | Default: `false` | Autoriza al usuario a ingresar al panel de administración técnica. |
| **`is_superuser`** | `BOOLEAN` | Obligatorio | Default: `false` | Otorga todos los permisos del sistema sin asignación explícita de grupos. |
| **`intentos_fallidos`** | `INTEGER` | Obligatorio | Default: `0`, Min: `0` | Contador acumulativo de intentos fallidos consecutivos de contraseña. |
| **`bloqueado_hasta`** | `TIMESTAMP` | Opcional (Nullable) | Indexado para consultas de desbloqueo | Marca temporal hasta la cual el usuario no puede autenticarse (enfriamiento de 15 minutos). |
| **`last_login`** | `TIMESTAMP` | Opcional (Nullable) | Actualizado en cada login exitoso | Momento exacto del último ingreso satisfactorio a la plataforma. |
| **`date_joined`** | `TIMESTAMP` | Obligatorio | Default: `CURRENT_TIMESTAMP` | Fecha y hora de creación de la cuenta en el sistema. |
| **`avatar_url`** | `VARCHAR(500)` | Opcional (Nullable) | URI o ruta relativa a `/media/` | Fotografía de perfil del colaborador. |
| **`cargo`** | `VARCHAR(120)` | Opcional (Nullable) | Cadena de texto | Cargo nominal en la estructura organizacional de Jolifoods. |
| **`empresa`** | `VARCHAR(120)` | Opcional (Nullable) | Default: `'Jolifoods'` | Unidad de negocio o empresa del grupo a la que pertenece. |

---

## 2. Índices de Rendimiento Requeridos

Para asegurar tiempos de respuesta inferiores a **50ms** en la consulta de credenciales:

1. **`idx_usuario_documento`**: `CREATE UNIQUE INDEX idx_usuario_documento ON usuarios (numero_documento);`
2. **`idx_usuario_email`**: `CREATE UNIQUE INDEX idx_usuario_email ON usuarios (email);`
3. **`idx_usuario_activo_tipo`**: `CREATE INDEX idx_usuario_activo_tipo ON usuarios (is_active, tipo);`
4. **`idx_usuario_bloqueo`**: `CREATE INDEX idx_usuario_bloqueo ON usuarios (bloqueado_hasta);`

---

## 3. Métodos y Lógica de Negocio Obligatoria del Modelo

Toda clase que implemente este modelo debe incorporar los siguientes métodos canónicos:

### 3.1. `is_locked() -> bool`
- **Comportamiento**: Retorna `true` si `bloqueado_hasta` no es nulo y la hora actual es menor que `bloqueado_hasta`. En caso contrario, retorna `false`.

### 3.2. `register_failed_attempt(max_attempts=5, lock_duration_minutes=15)`
- **Comportamiento**: Incrementa `intentos_fallidos += 1`. Si el contador alcanza `max_attempts`, fija `bloqueado_hasta = now() + timedelta(minutes=lock_duration_minutes)` y persiste los cambios.

### 3.3. `reset_failed_attempts()`
- **Comportamiento**: Al ingresar satisfactoriamente, reinicia `intentos_fallidos = 0` y `bloqueado_hasta = null`.

### 3.4. `check_password(raw_password) -> bool`
- **Comportamiento**: Compara de forma resistente a ataques de temporización (*constant-time comparison*) la contraseña en texto plano contra el hash almacenado.
