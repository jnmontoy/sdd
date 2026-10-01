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

[13] Suite Visual de Gráficas y Analítica (AnalyticsCharts)
     -> Ideal para: Dashboards directivos, comparativas de ventas, distribución por categorías y series temporales.
     -> Incluye: Área suave con gradiente corporativo, barras verticales redondeadas, donut/anillo con valor central,
        mini-sparklines y tooltips flotantes accesibles gobernados por variables.css.

[14] Escáner Biométrico Facial (Facial Biometric Scanner)
     -> Ideal para: Control de acceso, registro en porterías, verificación de conductores y kioscos de inspección.
     -> Incluye: Visor de cámara WebRTC en vivo, máscara/cortinilla con guía oval de encuadre,
        indicadores de estado (posicionamiento, iluminación, detección), zoom dinámico y captura fotográfica.

[15] Captura de Firma Digital en Canvas (SignatureModal)
     -> Ideal para: Aprobación de despachos, entrega de pedidos, actas de entrega, consentimientos y contratos.
     -> Incluye: Canvas táctil y ratón, recorte inteligente cropToSignature, exportación Base64 PNG transparente.

[16] Lector de Código de Barras y QR por Cámara (ScannerModal)
     -> Ideal para: Búsqueda rápida de inventario, check-in de conductores, validación de remisiones y tickets.
     -> Incluye: Integración html5-qrcode, auto-detección, visor centrado y retorno instantáneo de código escaneado.

[17] Visor de Documentos PDF en Canvas (PdfPreviewFrame)
     -> Ideal para: Visualización de facturas electrónicas, fichas técnicas y certificados sin salir de la vista.
     -> Incluye: Renderizado reactivo pdfjs-dist, paginación, zoom escalonado y efecto de hojas apiladas con sombras.

[18] Calendario Corporativo de Turnos y Novedades (CorporateCalendar)
     -> Ideal para: Gestión de cuadrillas, turnos de portería, vacaciones, incapacidades y programación semanal/mensual.
     -> Incluye: Malla mensual interactiva, badges cromáticos por novedad, leyenda segmentada y detalle al clic.

[19] Centro de Multi-Notificaciones en TopHeader (NotificationPopover)
     -> Ideal para: Centro unificado de alertas operativas, avisos de sistema, tareas asignadas y menciones.
     -> Incluye: Campana interactiva, pestañas multi-categoría, badges de estado no leído y acciones en línea.

[20] Banner de Instalación y Modo Kiosco PWA (PwaInstallBanner)
     -> Ideal para: Terminales táctiles, tablets de campo, porterías y smartphones de operarios.
     -> Incluye: Intercepción beforeinstallprompt, auto-ocultamiento si ya está instalado y botón de acción directa.

[21] Cargadores y Skeletons de Transición (PageLoader & TableSkeleton)
     -> Ideal para: Estados de carga, transiciones de pantalla y feedback visual de peticiones asíncronas.
     -> Incluye: Isotipo SVG Jolifoods animado, spinner con halo esmeralda y shimmers en tabla sin layout shift.

[22] Arquitectura de Actualización Reactiva en Tiempo Real (JS Smart Polling & Celery/Redis)
     -> Ideal para: Monitoreo en vivo de porterías, estado de pedidos, balance de inventario y jobs pesados.
     -> Incluye: Hook useSmartPolling con visibilityState y AbortController, más orquestación Celery en segundo plano.

[23] Conmutador de Estado Inmediato (ToggleSwitch / Activar Usuario)
     -> Ideal para: Habilitar/suspender usuarios en un clic, alternar directivas y switches de configuración.
     -> Incluye: Interruptor esmeralda animado, soporte de accesibilidad ARIA, variante miniatura para DataTable
        y flujo con ConfirmModal de justificación ante suspensiones de cuentas.
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

---

### Complemento [13]: Suite de Gráficas y Analítica Visual (`AnalyticsCharts`)
- **Archivos a reutilizar**:
  - Componente y estilos: [analytics_charts.md](../components/charts/analytics_charts.md)
  - Página de referencia: [dashboard/01_dashboard_especificacion.md](pages/dashboard/01_dashboard_especificacion.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Cuál es el tipo de métrica a representar?* (Serie temporal / tendencia -> `AreaGradientChart`, Comparativa por mes/sede -> `RoundedBarChart`, Distribución porcentual -> `DonutDistributionChart`, Micro-tendencia en tarjeta -> `MiniSparkline`).
  2. *¿Los datos provienen de un endpoint en vivo o de una agregación periódica de base de datos?*
  3. *¿Qué prefijo o sufijo monetario/numérico requiere el tooltip?* (ej. `$`, `kg`, `uds`, `%`).

---

### Complemento [14]: Escáner Biométrico Facial (`FacialScanner`)
- **Archivos a reutilizar**:
  - Componente y estilos: [facial_scanner.md](../components/biometrics/facial_scanner.md)
  - Cargadores y Skeletons: [page_loader.md](../components/loader/page_loader.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Cuál es el propósito de la captura facial?* (ej. Verificación 1:1 de identidad, registro de visitantes/conductores, enrolamiento de personal en portería o planta).
  2. *¿En qué dispositivo se utilizará principalmente?* (Cámara web de PC de escritorio, tablet/kiosco táctil con cámara frontal, o smartphone de operario con alternancia de cámara).
  3. *¿Se requiere envío directo de imagen Base64 / Blob hacia el backend o confirmación previa en un modal de revisión?*

---

### Complemento [15]: Captura de Firma Digital en Canvas (`SignatureModal`)
- **Archivos a reutilizar**:
  - Componente y estilos: [signature_modal.md](../components/signature/signature_modal.md)
  - Diálogo base: [modal_dialog.md](../components/modal/modal_dialog.md)
- **Preguntas que debe hacer la IA**:
  1. *¿En qué proceso se requiere la firma?* (ej. Entrega de pedido, recepción de mercancía, acta de entrega de dotación, consentimiento).
  2. *¿Se requiere obligatoriedad de trazo mínimo antes de habilitar el botón Guardar?*
  3. *¿El formato de almacenamiento requerido es PNG transparente recortado (`cropToSignature`) o lienzo completo?*

---

### Complemento [16]: Lector de Código de Barras y QR por Cámara (`ScannerModal`)
- **Archivos a reutilizar**:
  - Componente y estilos: [scanner_modal.md](../components/scanner/scanner_modal.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Qué simbología o formato se leerá principalmente?* (Códigos QR, Code 128, EAN-13, DataMatrix).
  2. *¿El escáner debe cerrar inmediatamente tras la primera lectura exitosa o permitir escaneo continuo por lotes?*
  3. *¿Sobre qué campo de la vista o formulario se cargará el valor decodificado?*

---

### Complemento [17]: Visor de Documentos PDF en Canvas (`PdfPreviewFrame`)
- **Archivos a reutilizar**:
  - Componente y estilos: [pdf_preview_frame.md](../components/pdf/pdf_preview_frame.md)
- **Preguntas que debe hacer la IA**:
  1. *¿El documento PDF se cargará desde una URL remota de API (Blob) o desde un archivo local subido por el usuario?*
  2. *¿Se requiere vista de hojas sueltas apiladas con efecto físico de sombra o vista continua de scroll?*
  3. *¿Qué controles de zoom y navegación deben habilitarse en la barra de herramientas del visor?*

---

### Complemento [18]: Calendario Corporativo de Turnos y Novedades (`CorporateCalendar`)
- **Archivos a reutilizar**:
  - Componente y estilos: [corporate_calendar.md](../components/calendar/corporate_calendar.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Qué tipos de novedades o eventos se registrarán en la cuadrícula mensual?* (ej. Turnos diurnos/nocturnos, vacaciones, incapacidades, permisos).
  2. *¿Al hacer clic en un día o evento, qué acción debe dispararse?* (Apertura de Right Drawer de detalle, formulario de asignación o modal).
  3. *¿Se requiere filtro de vista por colaborador, sede o cuadrilla?*

---

### Complemento [19]: Centro de Multi-Notificaciones en TopHeader (`NotificationPopover`)
- **Archivos a reutilizar**:
  - Componente y estilos: [notification_popover.md](../components/notification/notification_popover.md)
  - Cabecera: [navbar.md](../components/layout/navbar.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Cuáles pestañas de categorización requiere el popover?* (ej. "Todas", "Operativas", "Seguridad", "Menciones").
  2. *¿Las notificaciones se sincronizan mediante Smart Polling en tiempo real o carga bajo demanda al abrir la campana?*
  3. *¿Qué acción ejecuta el clic en cada notificación?* (Marcar como leída, redirigir a la URL del recurso, abrir modal).

---

### Complemento [20]: Banner de Instalación y Modo Kiosco PWA (`PwaInstallBanner`)
- **Archivos a reutilizar**:
  - Componente y estilos: [pwa_install_banner.md](../components/pwa/pwa_install_banner.md)
- **Preguntas que debe hacer la IA**:
  1. *¿La aplicación operará en tablets o smartphones en campo/bodega?*
  2. *¿Se debe mostrar el banner flotante en el pie de pantalla o solo un acceso directo en el menú de perfil?*
  3. *¿Se requiere soporte offline con Service Worker para almacenamiento local temporal?*

---

### Complemento [21]: Cargadores y Skeletons de Transición (`PageLoader` & `TableSkeleton`)
- **Archivos a reutilizar**:
  - Componente y estilos: [page_loader.md](../components/loader/page_loader.md)
- **Preguntas que debe hacer la IA**:
  1. *¿En qué secciones se requiere feedback de carga?* (Pantalla completa en arranque, shimmer en filas de tabla o spinner compacto en botones).
  2. *¿Cuántas filas y columnas de simulación debe tener el skeleton de tabla mientras responde la API?*

---

### Complemento [22]: Arquitectura de Actualización Reactiva en Tiempo Real (`SmartPolling` & `Celery/Redis`)
- **Archivos a reutilizar**:
  - Frontend Hook: [js_polling_architecture.md](../components/realtime/js_polling_architecture.md)
  - Backend Broker & Worker: [celery_redis_architecture.md](../stack/celery_redis_architecture.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Con qué intervalo debe ejecutarse el Smart Polling en primer plano?* (ej. 5s, 10s, 30s) y *¿a cuánto debe degradarse cuando la pestaña pasa a segundo plano?*
  2. *¿Qué endpoints o tareas en segundo plano procesa Celery Worker?* (ej. Procesamiento de archivos masivos, sincronización de base de datos externa, reportes pesados).

---

### Complemento [23]: Conmutador de Estado Inmediato (`ToggleSwitch` / Activar Usuario)
- **Archivos a reutilizar**:
  - Componente y estilos: [toggle_switch.md](../components/toggle/toggle_switch.md)
  - Modal de confirmación: [confirm_modal.md](../components/modal/confirm_modal.md)
  - Página de usuarios: [usuarios/01_usuarios_crud_especificacion.md](pages/usuarios/01_usuarios_crud_especificacion.md)
- **Preguntas que debe hacer la IA**:
  1. *¿Qué entidad o estado se conmutará?* (ej. `is_active` en usuarios, habilitación de notificaciones push, modo de mantenimiento).
  2. *¿La acción de desactivación es crítica y requiere ConfirmModal con justificación de 10+ caracteres para evitar desconexiones accidentales?*
  3. *¿En qué vista se ubicará el conmutador?* (Columna compacta en DataTable con tamaño `sm`, o control en formulario/Right Drawer con tamaño `md` y textos explicativos).




