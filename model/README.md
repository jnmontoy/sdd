# Catálogo de Modelos de Datos — Spec-Driven Development (SDD)
## Joli Foods — Directorio: `.sdd/model/`

Especificaciones de las entidades de persistencia comunes a las aplicaciones de Joli Foods. Cada modelo tiene su DDL de referencia para **PostgreSQL** y su implementación en Django ORM, y ambos DEBEN coincidir en tipos, nulabilidad, índices, unicidad y `on_delete`.

---

## 1. Módulos

| Módulo | Directorio | Modelos | Propósito |
| :--- | :--- | :--- | :--- |
| **Identidad y autenticación** | [`login/`](./login/README.md) | `Usuario`, `SesionUsuario`, `RegistroAuditoriaAcceso`, `TokenRestablecimientoClave` | Usuario custom (`AbstractBaseUser` + `PermissionsMixin`), sesiones, bitácora de accesos solo-inserción y tokens de restablecimiento con hash. |
| **Roles y sedes (RBAC)** | [`roles/`](./roles/spec_model_roles_permisos.md) | `Rol`, `Sede` | Roles en tabla propia con permisos `modulo.accion` (JSON) y relación M2M con usuarios (BP-19). |
| **Bitácora de operaciones** | [`auditoria/`](./auditoria/spec_model_bitacora.md) | `RegistroBitacoraAuditoria` | Trazabilidad solo-inserción de cambios por módulo, sin datos sensibles en los payloads. |
| **Telemetría y feedback** | [`telemetria/`](./telemetria/spec_model_telemetria.md) | `EventoUsoPlataforma`, `RespuestaFeedback` | Adopción por módulo y micro-encuestas, con minimización de datos personales. |
| **Archivos adjuntos** | [`archivos/`](./archivos/spec_model_archivos_media.md) | `ArchivoAdjunto` | Archivos en `backend/media/` con validación de tipo/tamaño, SHA-256 y descarga controlada de archivos privados. |

---

## 2. Principios de Persistencia

1. **DDL y ORM coinciden.** En proyectos Django las tablas las crean las migraciones; el DDL sirve para revisión y para otros backends.
2. **Sin N+1.** Las relaciones se cargan con `select_related()` (FK) y `prefetch_related()` (M2M e inversas).
3. **Índices justificados.** Se indexa lo que se filtra u ordena con frecuencia. Una restricción `UNIQUE` ya crea su índice; no se duplica con `CREATE UNIQUE INDEX`.
4. **Bajas lógicas.** Usuarios y catálogos se desactivan (`is_active = false`) en lugar de borrarse, para conservar la trazabilidad.
5. **Bitácoras solo-inserción** a nivel de aplicación y de permisos de base de datos.
6. **Datos personales mínimos** (Ley 1581 de 2012): solo se guarda lo necesario para la finalidad declarada, con retención definida.
