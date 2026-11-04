# Catálogo de Páginas — Joli Foods

Especificaciones de cada página de la plataforma bajo **Spec-Driven Development (SDD)**.

> **Antes de diseñar o crear una página:** aplica el protocolo de [`../03_asistente_interactivo_diseno_paginas.md`](../03_asistente_interactivo_diseno_paginas.md) para ofrecer al usuario opciones claras (panel lateral vs. modal, capacidades de tabla, etc.).

Cada subcarpeta corresponde a una página o flujo y contiene su arquitectura, interfaz, contratos de API y referencias.

---

## Índice

| Código | Página | Directorio | Resumen |
| :--- | :--- | :--- | :--- |
| `PAGE-001` | Login y autenticación | [`login/`](./login/README.md) | Documento + clave, Microsoft SSO, access token en memoria + refresh en cookie HttpOnly, límite de intentos y recuperación de clave. |
| `PAGE-002` | Layout maestro (App Shell) | [`layout/`](./layout/README.md) | Barra superior, menú lateral colapsable, tema noche/día y sesión vencida. |
| `PAGE-003` | Tablero principal | [`dashboard/`](./dashboard/README.md) | KPI clicables, actividad y últimos accesos. |
| `PAGE-004` | Gestión de usuarios (CRUD) | [`usuarios/`](./usuarios/README.md) | Listado paginado en servidor sin N+1, roles M2M, panel lateral de edición y suspensión. |
| `PAGE-005` | Bitácora de auditoría | [`auditoria/`](./auditoria/README.md) | Eventos solo-inserción, visor de detalle, filtros y exportación. |
| `PAGE-006` | Perfil y seguridad | [`profile/`](./profile/README.md) | Datos de identidad, cambio de contraseña y cierre de sesiones. |
| `PAGE-007` | Páginas de error (404/403/500) | [`not_found/`](./not_found/README.md) | Rutas inexistentes, accesos no autorizados y fallos con retorno seguro. |
| `PAGE-008` | Roles y permisos (RBAC) | [`roles/`](./roles/README.md) | Matriz de permisos por módulo (ver, crear, editar, eliminar, exportar). |
| `PAGE-009` | Primer ingreso | [`primer_ingreso/`](./primer_ingreso/README.md) | Cambio obligatorio de contraseña para cuentas nuevas o restablecidas. |
| `PAGE-010` | Configuración del sistema | [`configuracion/`](./configuracion/README.md) | Parámetros institucionales, políticas de sesión, correo y modo mantenimiento. |

El estado de cada especificación (borrador, revisada, implementada) se registra en el proyecto que la adopta; este catálogo no certifica implementaciones.
