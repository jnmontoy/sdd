# Esquema DDL Canónico: Módulo de Login
## Joli Foods — Spec-Driven Development (SDD)

DDL de referencia para **PostgreSQL 14+** (usa `BIGSERIAL`, `INET`, `TIMESTAMPTZ`, `gen_random_uuid()`). En proyectos Django las tablas las crean las migraciones a partir de [`implementacion_django_orm.md`](./implementacion_django_orm.md); este DDL sirve para revisar que ambos coincidan y para backends que no usen Django.

Orden de creación: `organizacion_sede` y `auth_rol` ([`../roles/spec_model_roles_permisos.md`](../roles/spec_model_roles_permisos.md)) → `usuarios` → resto.

---

## 1. `usuarios`

```sql
CREATE TABLE usuarios (
    id                 BIGSERIAL    PRIMARY KEY,
    password           VARCHAR(128) NOT NULL,
    last_login         TIMESTAMPTZ  NULL,
    is_superuser       BOOLEAN      NOT NULL DEFAULT FALSE,
    numero_documento   VARCHAR(15)  NOT NULL,
    email              VARCHAR(254) NOT NULL,
    first_name         VARCHAR(150) NOT NULL,
    last_name          VARCHAR(150) NOT NULL,
    is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
    is_staff           BOOLEAN      NOT NULL DEFAULT FALSE,
    debe_cambiar_clave BOOLEAN      NOT NULL DEFAULT TRUE,
    intentos_fallidos  INTEGER      NOT NULL DEFAULT 0,
    bloqueado_hasta    TIMESTAMPTZ  NULL,
    date_joined        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sede_id            BIGINT       NULL REFERENCES organizacion_sede(id) ON DELETE SET NULL,
    cargo              VARCHAR(120) NULL,
    empresa            VARCHAR(120) NULL,
    avatar             VARCHAR(500) NULL,

    CONSTRAINT uq_usuario_documento UNIQUE (numero_documento),
    CONSTRAINT uq_usuario_email UNIQUE (email),
    CONSTRAINT chk_usuario_documento CHECK (numero_documento ~ '^[0-9]{5,15}$'),
    CONSTRAINT chk_usuario_intentos CHECK (intentos_fallidos >= 0)
);

-- Las restricciones UNIQUE ya crean índices; no se repiten como CREATE UNIQUE INDEX.
CREATE UNIQUE INDEX uq_usuario_email_ci ON usuarios (LOWER(email));
CREATE INDEX idx_usuario_activo   ON usuarios (is_active);
CREATE INDEX idx_usuario_bloqueo  ON usuarios (bloqueado_hasta);
CREATE INDEX idx_usuario_sede     ON usuarios (sede_id);

-- Relación muchos-a-muchos con roles (BP-19)
CREATE TABLE usuarios_roles (
    id         BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    rol_id     BIGINT NOT NULL REFERENCES auth_rol(id) ON DELETE CASCADE,
    CONSTRAINT uq_usuario_rol UNIQUE (usuario_id, rol_id)
);
CREATE INDEX idx_usuarios_roles_rol ON usuarios_roles (rol_id);
```

Las tablas `usuarios_groups` y `usuarios_user_permissions` de `PermissionsMixin` las genera la migración de Django y no se repiten aquí.

---

## 2. `sesiones_usuario`

```sql
CREATE TABLE sesiones_usuario (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id       BIGINT       NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    refresh_jti      VARCHAR(64)  NOT NULL,
    ip_origen        INET         NOT NULL,
    user_agent       VARCHAR(512) NOT NULL DEFAULT '',
    dispositivo      VARCHAR(10)  NULL,
    fecha_inicio     TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMPTZ  NOT NULL,
    is_activa        BOOLEAN      NOT NULL DEFAULT TRUE,
    fecha_cierre     TIMESTAMPTZ  NULL,

    CONSTRAINT uq_sesion_refresh_jti UNIQUE (refresh_jti),
    CONSTRAINT chk_sesion_dispositivo CHECK (dispositivo IS NULL OR dispositivo IN ('Desktop', 'Mobile', 'Tablet', 'Kiosk'))
);

CREATE INDEX idx_sesion_usuario_activa ON sesiones_usuario (usuario_id, is_activa);
```

---

## 3. `registro_auditoria_acceso` (solo-inserción)

```sql
CREATE TABLE registro_auditoria_acceso (
    id                  BIGSERIAL    PRIMARY KEY,
    documento_ingresado VARCHAR(20)  NOT NULL,
    usuario_id          BIGINT       NULL REFERENCES usuarios(id) ON DELETE SET NULL,
    evento              VARCHAR(40)  NOT NULL,
    resultado           VARCHAR(10)  NOT NULL,
    motivo_fallo        VARCHAR(150) NULL,
    ip_origen           INET         NOT NULL,
    user_agent          VARCHAR(512) NOT NULL DEFAULT '',
    fecha_evento        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tiempo_respuesta_ms INTEGER      NULL,

    CONSTRAINT chk_auditoria_resultado CHECK (resultado IN ('SUCCESS', 'FAILURE', 'BLOCKED'))
);

CREATE INDEX idx_auditoria_fecha        ON registro_auditoria_acceso (fecha_evento DESC);
CREATE INDEX idx_auditoria_doc          ON registro_auditoria_acceso (documento_ingresado);
CREATE INDEX idx_auditoria_ip           ON registro_auditoria_acceso (ip_origen);
CREATE INDEX idx_auditoria_usuario_fecha ON registro_auditoria_acceso (usuario_id, fecha_evento DESC);

-- Solo-inserción para el rol de la aplicación (ajusta "app_user" al rol real)
REVOKE UPDATE, DELETE, TRUNCATE ON registro_auditoria_acceso FROM app_user;
GRANT  SELECT, INSERT ON registro_auditoria_acceso TO app_user;
```

`ON DELETE SET NULL` en `usuario_id` requiere `UPDATE` interno del motor, que no depende de los permisos del rol de la aplicación. Aun así, los usuarios se desactivan (`is_active = false`) en lugar de borrarse.

---

## 4. `tokens_restablecimiento_clave`

```sql
CREATE TABLE tokens_restablecimiento_clave (
    id                   BIGSERIAL    PRIMARY KEY,
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

---

## 5. Lista negra de refresh tokens

En Django: app `rest_framework_simplejwt.token_blacklist` (sus tablas las crea la migración). Para otros backends, ver [`spec_model_sesion_auditoria.md`](./spec_model_sesion_auditoria.md) §3.
