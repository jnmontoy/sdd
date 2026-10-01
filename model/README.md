# Catálogo de Modelos de Datos — Spec-Driven Development (SDD)
## Ecosistema Jolifoods — Directorio: `.sdd/model/`

Este directorio reúne las especificaciones formales de las entidades de persistencia y esquemas relacionales para el ecosistema corporativo **Jolifoods**.

---

## 1. Módulos de Modelos

| Módulo | Directorio | Modelos Clave | Propósito |
| :--- | :--- | :--- | :--- |
| **Identidad & Autenticación** | [`login/`](./login/README.md) | `Usuario`, `SesionUsuario`, `AuditoriaAcceso`, `TokenRestablecimientoClave` | Cédula, email, credenciales con hash seguro, auditoría de login y tokens OTT de 15 min. |
| **Bitácora de Auditoría** | [`auditoria/`](./auditoria/spec_model_bitacora.md) | `RegistroBitacoraAuditoria` | Trazabilidad inmutable de eventos, modificaciones y operaciones por módulo. |
| **Roles & Sedes (RBAC)** | [`roles/`](./roles/spec_model_roles_permisos.md) | `Rol`, `Sede`, `RolPermiso` | Control de acceso basado en roles (`ADMIN`, `OPERADOR`, `AUDITOR`, `CONSULTA`) y permisos por módulo. |

---

## 2. Principios de Persistencia en el SDD

1. **Agnóstico del Motor Relacional**: Todo esquema tiene su especificación DDL SQL estándar para PostgreSQL o MySQL.
2. **Implementación de Referencia en Django ORM**: Modelos preparados para optimizaciones Anti-N+1 con `select_related()` y `prefetch_related()`.
3. **Índices Estratégicos**: Todo campo consultado con frecuencia (`numero_documento`, `email`, `codigo`, `fecha_hora`, `modulo`) cuenta con `db_index=True` o índices compuestos explícitos.
