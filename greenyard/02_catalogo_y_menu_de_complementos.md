# Catálogo Maestro y Menú Interactivo de Complementos SDD
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

Este documento sirve como la guía interactiva oficial que la **Inteligencia Artificial** o el **desarrollador de software** debe consultar al crear o extender un módulo en cualquier proyecto de la organización.

---

## 1. Menú Interactivo de Selección de Complementos

Cuando un usuario o desarrollador solicite: *"Quiero crear un complemento"*, *"Añade una funcionalidad"* o *"Crea un módulo nuevo"*, el sistema debe presentar el siguiente menú numerado:

```text
====================================================================================================
               MENÚ DE COMPLEMENTOS Y MÓDULOS CORPORATIVOS — JOLIFOODS (SDD)
====================================================================================================
 [1] Listado Tabular Avanzado (Data Table Tipo Excel)
     -> Ideal para: Inventarios, pedidos, facturas, transacciones y maestros.
     -> Incluye: ChecklistPopover en cabeceras, orden A-Z/Z-A, buscador reactivo, botón 'Solo',
        selector de columnas (Columns3), paginación server-side y exportador a Excel (.xlsx).

 [2] Tablero de Control y Métricas KPI (Estándar BI Cartera)
     -> Ideal para: Dashboards directivos, monitoreo operativo e indicadores en tiempo real.
     -> Incluye: Rejilla responsive .cartera-kpi-row, tarjetas clickeables como filtros cruzados,
        halo cromático (blue, amber, pink, emerald, cyan), badge 'FILTRO ACTIVO' y skeletons.

 [3] Panel Lateral Deslizable de Detalle o Edición (Drawer / Slide-Over)
     -> Ideal para: Inspeccionar filas de tablas o editar datos sin perder el contexto visual.
     -> Incluye: Panel slide-over (sm: 400px, md: 600px, lg: 840px), backdrop blur,
        cierre con tecla ESC o clic exterior, cabecera fija, scroll y pie con botones de acción.

 [4] Selector Inteligente Tipo Búsqueda (Searchable SelectFilter)
     -> Ideal para: Formularios modales o filtros con listas largas (clientes, sedes, productos).
     -> Incluye: Erradicación del <select> nativo, campo de búsqueda reactiva en vivo,
        navegación por teclado (flechas y Enter), badge de selección y estado 'Sin resultados'.

 [5] Diálogo Modal de Confirmación y Seguridad (ConfirmModal)
     -> Ideal para: Eliminaciones lógicas, reseteos de clave, aprobaciones y acciones críticas.
     -> Incluye: Sustituto corporativo de confirm() y alert(), portal DOM, fondo difuminado,
        icono con halo cromático (danger, warning, primary), spinner asíncrono y emphasizeCancel.

 [6] Sistema de Alertas y Notificaciones Asíncronas (Toast Notification)
     -> Ideal para: Retroalimentación de éxito, error de red o advertencia tras operaciones AJAX.
     -> Incluye: Integración con sonner estilizado con tokens Jolifoods, auto-cierre
        diferenciado por severidad, posicionamiento adaptativo y botón de acción opcional.

 [7] Guardián de Resiliencia ante Despliegues (Global Error Boundary)
     -> Ideal para: Proteger la aplicación en producción de la 'pantalla blanca'.
     -> Incluye: Captura global de excepciones y detección automática de 'ChunkLoadError'
        provocado por nuevos despliegues de Vite, con auto-recarga controlada por cooldown.

 [8] Alerta Desacoplada de Sesión Expirada (Session Expiration Modal)
     -> Ideal para: Avisar al usuario que su token JWT o sesión ha caducado.
     -> Incluye: Escucha del evento global SESSION_EXPIRED_EVENT (emitido en errores 401),
        bloqueo de pantalla y redirección segura al login preservando la URL previa.

 [9] Pantalla de Estado Vacío Ilustrada (Empty State)
     -> Ideal para: Bandejas vacías, filtros sin coincidencias o errores de carga de datos.
     -> Incluye: Iconos ilustrativos grandes, mensajes claros y constructivos, y botones
        de llamada a la acción (CTA) como 'Limpiar filtros' o 'Crear nuevo registro'.

[10] Matriz de Control de Acceso por Roles (Módulo RBAC)
     -> Ideal para: Administrar perfiles y definir qué rol puede ver, crear, editar o eliminar.
     -> Incluye: Selector lateral de roles, tabla matricial con casillas por módulo y acción,
        protección de roles de sistema y guardado seguro con ConfirmModal.

[11] Flujo Obligatorio de Activación y Cambio de Clave (Primer Ingreso)
     -> Ideal para: Usuarios recién creados o con contraseña restablecida por un administrador.
     -> Incluye: Intercepción forzada de navegación, medidor visual de entropía en tiempo
        real (Débil a Fuerte) y validación de reglas de complejidad de contraseñas.

[12] Capa Backend de Alta Velocidad FastAPI (Zero N+1)
     -> Ideal para: Optimizar consultas masivas y endpoints de alta concurrencia en Django.
     -> Incluye: Servidor ASGI híbrido bajo un solo proceso, sub-ruta /fast, serialización
        directa con Pydantic, consultas select_related / .values() y refresco de sockets DB.
====================================================================================================
```

---

## 2. Ficha Técnica Detallada de Cada Complemento

### Complemento [1]: Listado Tabular Avanzado (`DataTable` Tipo Excel)
- **Archivos a reutilizar**:
  - Componente principal: [data_table.md](../components/data_table/data_table.md)
  - Popover de filtros Excel: [checklist_popover.md](../components/data_table/checklist_popover.md)
  - Paginador corporativo: [pagination.md](../components/pagination/pagination.md)
  - Exportador a Excel: [excel_export.md](../components/export/excel_export.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Cuál es el nombre de la entidad que se listará?* (ej. Facturas, Colaboradores, Activos).
  2. *¿Cuáles columnas deben tener filtros tipo Excel (`filterable: true`) y ordenamiento (`sortable: true`)?*
  3. *¿Cuáles acciones por fila se requieren?* (ej. Ver detalle, Editar, Desactivar).

---

### Complemento [2]: Tablero de Control y Métricas KPI (`KPICards` BI Cartera)
- **Archivos a reutilizar**:
  - Componente y estilos: [kpi_cards.md](../components/kpi/kpi_cards.md)
  - Página de referencia: [dashboard/01_dashboard_especificacion.md](pages/dashboard/01_dashboard_especificacion.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Cuáles son los 4 a 6 indicadores clave a mostrar?* (ej. Total Registros, Activos, Pendientes, Vencidos).
  2. *¿Al hacer clic en una tarjeta KPI, qué filtro debe activarse en la tabla o listado inferior?*
  3. *¿Qué halo cromático corresponde a cada métrica?* (`icon-blue`, `icon-amber`, `icon-pink`, `icon-emerald`, `icon-cyan`).

---

### Complemento [3]: Panel Lateral Deslizable (`Drawer` / Slide-Over)
- **Archivos a reutilizar**:
  - Componente y estilos: [drawer.md](../components/drawer/drawer.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Qué ancho se ajusta mejor a la información?* (`sm`: 400px para datos breves, `md`: 600px para formularios estándar, `lg`: 840px para tablas anidadas).
  2. *¿Qué campos o pestañas se desplegarán en el cuerpo del panel?*
  3. *¿Qué botones de acción fijos irán en el pie del panel?* (ej. Guardar, Cancelar, Imprimir).

---

### Complemento [4]: Selector Tipo Búsqueda (`SelectFilter` / Searchable Select)
- **Archivos a reutilizar**:
  - Componente y estilos: [select_filter.md](../components/dropdown/select_filter.md)
- **Preguntas que debe hacer la IA**:
  1. *¿De qué entidad o catálogo provienen las opciones?* (ej. Roles, Ciudades, Proveedores).
  2. *¿Las opciones se cargan estáticamente o mediante llamada a la API en vivo?*
  3. *¿Se requiere selección única o múltiple?*

---

### Complemento [5]: Diálogo Modal de Confirmación (`ConfirmModal`)
- **Archivos a reutilizar**:
  - Componente y estilos: [confirm_modal.md](../components/modal/confirm_modal.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Qué acción crítica se va a proteger?* (ej. Eliminar usuario, Cerrar periodo, Revertir transacción).
  2. *¿Cuál es el nivel de severidad visual?* (`danger`: rojo para destrucciones irreversibles, `warning`: ámbar para cambios sensibles, `primary`: verde corporativo para aprobaciones).
  3. *¿Se requiere enfatizar el botón Cancelar (`emphasizeCancel = true`) para evitar confirmaciones accidentales?*

---

### Complemento [6]: Notificaciones Asíncronas (`ToastNotification`)
- **Archivos a reutilizar**:
  - Utilidad y despachador: [toast_notification.md](../components/toast/toast_notification.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Qué eventos del módulo dispararán notificaciones?* (ej. Guardado exitoso, Error de red, Advertencia de cupo).
  2. *¿Algún toast requerirá botón de acción o deshacer (`actionLabel` y `onAction`)?*

---

### Complemento [7]: Guardián de Resiliencia (`GlobalErrorBoundary`)
- **Archivos a reutilizar**:
  - Componente y estilos: [error_boundary.md](../components/error_boundary/error_boundary.md)
- **Preguntas que debe hacer la IA**:
  1. *¿El límite envolverá toda la aplicación en el Router o un sub-módulo específico?*
  2. *¿Cuál es la URL de retorno seguro deseada?* (ej. `/` o `/dashboard`).

---

### Complemento [8]: Alerta de Sesión Expirada (`SessionExpirationModal`)
- **Archivos a reutilizar**:
  - Componente y estilos: [session_expiration_modal.md](../components/modal/session_expiration_modal.md)
  - Servicio HTTP emisor: [api_client.md](../components/services/api_client.md)
- **Preguntas que debe hacer la IA**:
  1. *¿El proyecto utiliza tokens JWT en `localStorage` o cookies de sesión `HttpOnly`?*

---

### Complemento [9]: Estado Vacío Ilustrado (`EmptyState`)
- **Archivos a reutilizar**:
  - Componente y estilos: [empty_state.md](../components/empty_state/empty_state.md)
- **Preguntas que debe hacer la IA**:
  1. *¿En qué vista o tabla se mostrará el estado vacío?*
  2. *¿Cuál debe ser el mensaje motivador y qué acción sugerirá al usuario?* (ej. "Aún no hay clientes registrados. Haga clic en Crear Cliente").

---

### Complemento [10]: Matriz de Control de Acceso (`Roles y Permisos RBAC`)
- **Archivos a reutilizar**:
  - Especificación de página: [roles/01_roles_permisos_especificacion.md](pages/roles/01_roles_permisos_especificacion.md)
  - Modelo de base de datos: [model/roles/spec_model_roles_permisos.md](../model/roles/spec_model_roles_permisos.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Cuáles son los módulos del sistema sobre los que se asignarán permisos?*
  2. *¿Cuáles roles de sistema tendrán privilegios de solo lectura o administración total?*

---

### Complemento [11]: Activación y Cambio de Clave (`Primer Ingreso`)
- **Archivos a reutilizar**:
  - Especificación de página: [primer_ingreso/01_primer_ingreso_especificacion.md](pages/primer_ingreso/01_primer_ingreso_especificacion.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Qué reglas de complejidad de contraseña deben aplicarse?* (longitud mínima, mayúsculas, números, símbolos).
  2. *¿Se debe restringir el uso de las últimas N contraseñas?*

---

### Complemento [12]: Capa Backend de Alta Velocidad (`FastAPI Híbrido Zero N+1`)
- **Archivos a reutilizar**:
  - Especificación técnica: [asgi_hybrid_architecture.md](../stack/asgi_hybrid_architecture.md)
  - Plantilla universal: [asgi_template.py](../stack/asgi_template.py)
- **Preguntas que debe hacer la IA**:
  1. *¿Cuáles endpoints de lectura masiva o reportes deben migrarse al prefijo `/fast`?*
  2. *¿Qué relaciones de modelos Django requieren `select_related()` o proyecciones directas `.values()`?*
