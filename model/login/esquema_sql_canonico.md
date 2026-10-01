# Esquema DDL SQL Canónico: Módulo de Login
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Este documento contiene las sentencias DDL en lenguaje **SQL estándar** para inicializar las tablas de autenticación en bases de datos relacionales (PostgreSQL, SQLite, MySQL).

---

## 1. Tabla: `usuarios`

```sql
CREATE TABLE usuarios (
    id BIGSERIAL PRIMARY KEY,
    numero_documento VARCHAR(15) NOT NULL,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'Colaborador',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    intentos_fallidos INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta TIMESTAMP WITH TIME ZONE NULL,
    last_login TIMESTAMP WITH TIME ZONE NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    avatar_url VARCHAR(500) NULL,
    cargo VARCHAR(120) NULL,
    empresa VARCHAR(120) NOT NULL DEFAULT 'Jolifoods',
    
    -- Restricciones de Unicidad
    CONSTRAINT uq_usuario_documento UNIQUE (numero_documento),
    CONSTRAINT uq_usuario_email UNIQUE (email),
    
    -- Restricción de Dominio en Tipo
    CONSTRAINT chk_usuario_tipo CHECK (tipo IN ('Administrador', 'Colaborador', 'Operario', 'Auditor'))
);

-- Índices de Rendimiento
CREATE UNIQUE INDEX idx_usuario_documento ON usuarios(numero_documento);
CREATE UNIQUE INDEX idx_usuario_email ON usuarios(email);
CREATE INDEX idx_usuario_activo_tipo ON usuarios(is_active, tipo);
CREATE INDEX idx_usuario_bloqueado ON usuarios(bloqueado_hasta);
```

---

## 2. Tabla: `sesiones_usuario`

```sql
CREATE TABLE sesiones_usuario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id BIGINT NOT NULL,
    jti VARCHAR(64) NOT NULL,
    ip_origen VARCHAR(45) NOT NULL,
    user_agent TEXT NOT NULL,
    dispositivo VARCHAR(50) NULL,
    fecha_inicio TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP WITH TIME ZONE NOT NULL,
    is_activa BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_cierre TIMESTAMP WITH TIME ZONE NULL,

    CONSTRAINT fk_sesion_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT uq_sesion_jti UNIQUE (jti)
);

CREATE INDEX idx_sesion_usuario_activa ON sesiones_usuario(usuario_id, is_activa);
CREATE INDEX idx_sesion_jti ON sesiones_usuario(jti);
```

---

## 3. Tabla: `registro_auditoria_acceso`

```sql
CREATE TABLE registro_auditoria_acceso (
    id BIGSERIAL PRIMARY KEY,
    documento_ingresado VARCHAR(50) NOT NULL,
    usuario_id BIGINT NULL,
    evento VARCHAR(35) NOT NULL,
    resultado VARCHAR(15) NOT NULL,
    motivo_fallo VARCHAR(150) NULL,
    ip_origen VARCHAR(45) NOT NULL,
    user_agent TEXT NOT NULL,
    fecha_evento TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tiempo_respuesta_ms INTEGER NULL,

    CONSTRAINT fk_auditoria_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuarios(id) ON DELETE SET NULL
);

CREATE INDEX idx_auditoria_fecha ON registro_auditoria_acceso(fecha_evento DESC);
CREATE INDEX idx_auditoria_doc ON registro_auditoria_acceso(documento_ingresado);
CREATE INDEX idx_auditoria_ip ON registro_auditoria_acceso(ip_origen);
```

---

## 4. Tabla: `tokens_restablecimiento_clave`

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
