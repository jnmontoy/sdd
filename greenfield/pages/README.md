# Catálogo de Páginas — Ecosistema Greenyard

Esta carpeta almacena las especificaciones de cada página de la plataforma bajo el estándar **Spec-Driven Development (SDD)**.

> **GUÍA DE ASESORÍA AL DISEÑAR O CREAR PÁGINAS**:  
> Antes de codificar una nueva página o CRUD, consulte y aplique el protocolo guiado en [`../03_asistente_interactivo_diseno_paginas.md`](../03_asistente_interactivo_diseno_paginas.md) para asesorar al usuario con opciones claras (Modal vs Drawer, capacidades de tabla, etc.).

Cada subcarpeta corresponde a una página o flujo de pantalla único y contiene su arquitectura, especificación de UI, contratos de API y análisis de referencia.

---

## Índice de Páginas

| Código | Página | Directorio | Estado | Resumen |
| :--- | :--- | :--- | :--- | :--- |
| **`PAGE-001`** | **Login & Autenticación** | [`login/`](./login/README.md) | ✅ Completo | Autenticación (Cédula, Clave, M365 SSO), cookies HttpOnly, Rate Limiting y recuperación de clave. |
| **`PAGE-002`** | **Layout Maestro (App Shell)** | [`layout/`](./layout/README.md) | ✅ Completo | Top Navbar, Sidebar colapsable, selector Noche/Día y detector de sesión expirada. |
| **`PAGE-003`** | **Tablero Principal (Dashboard)**| [`dashboard/`](./dashboard/README.md) | ✅ Completo | Rejilla de KPIs, telemetría de peticiones en vivo y bitácora de accesos recientes. |
| **`PAGE-004`** | **Gestión de Usuarios (CRUD)** | [`usuarios/`](./usuarios/README.md) | ✅ Completo | Listado server-side Anti-N+1, asignación de roles RBAC, modal de edición y suspensión. |
| **`PAGE-005`** | **Bitácora de Auditoría** | [`auditoria/`](./auditoria/README.md) | ✅ Completo | Trazabilidad inmutable de eventos, visor de detalles, filtros y exportación Excel/PDF. |
| **`PAGE-006`** | **Perfil y Seguridad** | [`profile/`](./profile/README.md) | ✅ Completo | Datos de identidad, formulario de cambio de contraseña voluntario y revocación de sesiones. |
| **`PAGE-007`** | **Páginas de Error (404/403)** | [`not_found/`](./not_found/README.md) | ✅ Completo | Manejo amigable de rutas inexistentes y accesos no autorizados con retorno seguro. |
| **`PAGE-008`** | **Roles y Permisos (RBAC)** | [`roles/`](./roles/README.md) | ✅ Completo | Matriz interactiva de permisos por módulo (ver, crear, editar, eliminar, exportar). |
| **`PAGE-009`** | **Activación / Primer Ingreso** | [`primer_ingreso/`](./primer_ingreso/README.md) | ✅ Completo | Cambio obligatorio de contraseña con medidor de entropía visual para cuentas nuevas o reseteadas. |
| **`PAGE-010`** | **Configuración del Sistema** | [`configuracion/`](./configuracion/README.md) | ✅ Completo | Parametrización institucional, directivas de inactividad, canales SMTP y modo mantenimiento. |
