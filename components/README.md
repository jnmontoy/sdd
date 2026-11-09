# Catálogo de Componentes UI — Spec-Driven Development (SDD)
## Sistema de componentes reutilizables de Joli Foods

Este directorio contiene las especificaciones de los componentes de interfaz que componen las páginas de las aplicaciones de Joli Foods.

Con **SDD** (*Spec-Driven Development*: desarrollo guiado por especificaciones) un componente no se codifica de forma aislada ni con estilos improvisados: cada uno tiene una especificación con su **estructura JSX/HTML, clases CSS, variantes, estados interactivos y reglas de accesibilidad**. Los colores, tipografía y espaciados salen siempre de [`variables.css`](./variables.css).

> **Selección rápida de variantes:** para ver las opciones de un componente (KPI, tabla, modal, drawer, selector, etc.) consulte [`../greenfield/04_menus_de_seleccion_por_componente.md`](../greenfield/04_menus_de_seleccion_por_componente.md).

> **Columna "Origen":** indica de qué proyecto se extrajo el patrón. Es informativa: la especificación es genérica y aplica a cualquier proyecto.

---

## Índice de componentes (59 especificaciones)

| Componente | Archivo | Uso principal | Variantes / capacidades | Origen |
| :--- | :--- | :--- | :--- | :--- |
| **Variables globales** | [`variables.css`](./variables.css) / [`variables.md`](./variables.md) | Tokens CSS y tema | Modo Noche (`:root`), Modo Día (`[data-theme='light']`), alias heredados | — |
| **Logo corporativo** | [`login/logo.md`](./login/logo.md) | Encabezado institucional | Isotipo, logotipo completo, monocromático | — |
| **Tarjeta de login** | [`login/card.md`](./login/card.md) | Contenedor del formulario de acceso | Tarjeta centrada, pantalla dividida, quiosco | — |
| **Botón Microsoft SSO** | [`login/button_microsoft.md`](./login/button_microsoft.md) | Inicio de sesión con Microsoft 365 | Logo oficial SVG, oscuro, claro | — |
| **Campo con etiqueta flotante** | [`form/floating_field.md`](./form/floating_field.md) | Todo formulario de captura (login, contraseñas, CRUD); **no** filtros ni buscadores | Input, select nativo, selector propio, textarea, contraseña; web (CSS) y React Native; animación de 220 ms | pandora |
| **Campos del login** | [`login/input_field.md`](./login/input_field.md) | Documento y contraseña | Etiqueta flotante, mostrar/ocultar, Bloq Mayús, error en línea | pandora |
| **Botón primario** | [`login/button_primary.md`](./login/button_primary.md) | Envío de formularios | Normal, con spinner, deshabilitado | — |
| **Mensajes y alertas** | [`login/feedback_alerts.md`](./login/feedback_alerts.md) | Errores y validación | Banner en línea, toast, aviso de inactividad | — |
| **Restablecer contraseña** | [`login/recovery_form.md`](./login/recovery_form.md) | Solicitud y nueva clave | Solicitud por documento/correo y nueva contraseña | — |
| **Formulario de login completo** | [`login/login_form.md`](./login/login_form.md) | Ensamblado completo | Pestañas, recordar documento, enlace de recuperación | — |
| **Plantilla de correo** | [`login/email_recovery_template.md`](./login/email_recovery_template.md) | Correo de recuperación | HTML con estilos en línea compatible con Outlook y Gmail | — |
| **Barra superior** | [`layout/navbar.md`](./layout/navbar.md) | Cabecera persistente | Título a la izquierda, tema, notificaciones, perfil | — |
| **Reglas de layout** | [`layout/layout_rules.md`](./layout/layout_rules.md) | Distribución de pantallas | Ancho completo; centrado solo en modales y login | — |
| **Menú de perfil de usuario** | [`layout/user_profile_dropdown.md`](./layout/user_profile_dropdown.md) | Sesión en el TopHeader | Avatar, datos del usuario, rol, Mi perfil, salir con confirmación | vibra, tiendita |
| **Menú lateral** | [`layout/sidebar.md`](./layout/sidebar.md) | Navegación de módulos | Opcional; por defecto sin sidebar | — |
| **Tabla de datos** | [`data_table/data_table.md`](./data_table/data_table.md) | Listados y CRUD | Paginación en servidor, buscador con espera, exportación | bi (cartera) |
| **Filtro tipo Excel por columna** | [`data_table/checklist_popover.md`](./data_table/checklist_popover.md) | Filtros de tabla | Ordenar A-Z/Z-A, buscador, lista con conteo, "Solo" | bi (cartera) |
| **Columnas redimensionables** | [`data_table/column_resizer.md`](./data_table/column_resizer.md) | Ancho de columnas | Arrastre, doble clic restablece, ancho mínimo, persistencia | bi (cartera) |
| **Visibilidad de columnas** | [`data_table/column_visibility.md`](./data_table/column_visibility.md) | Mostrar/ocultar columnas | Casillas con conteo, Todas / Restablecer | — |
| **Tarjetas KPI** | [`kpi/kpi_cards.md`](./kpi/kpi_cards.md) | Indicadores | KPI clicable como filtro, cajas de icono, esqueletos | bi (cartera) |
| **Modal accesible** | [`modal/modal_dialog.md`](./modal/modal_dialog.md) | Diálogos (no CRUD) | Tamaños `sm`–`xl`, foco atrapado | — |
| **Modal de confirmación** | [`modal/confirm_modal.md`](./modal/confirm_modal.md) | Reemplazo de `confirm()` | Justificación obligatoria, spinner, variante de peligro | — |
| **Badges de estado** | [`badge/badge_status.md`](./badge/badge_status.md) | Estados y roles | `success`, `danger`, `warning`, `info`, `admin`, `operator` | — |
| **Selector con búsqueda** | [`dropdown/select_filter.md`](./dropdown/select_filter.md) | Selectores y filtros | Reemplazo de `<select>` con búsqueda y teclado | — |
| **Notificaciones toast** | [`toast/toast_notification.md`](./toast/toast_notification.md) | Avisos no bloqueantes | `success`, `error`, `warning`, `info`, botón de acción | — |
| **Paginación** | [`pagination/pagination.md`](./pagination/pagination.md) | Navegación de registros | Arriba de la tabla, resumen, elipsis, filas por página | — |
| **Exportación a Excel** | [`export/excel_export.md`](./export/excel_export.md) | Descarga tabular | SheetJS en navegador o backend con `openpyxl`; anti inyección de fórmulas | — |
| **Estado vacío** | [`empty_state/empty_state.md`](./empty_state/empty_state.md) | Vistas sin datos | Icono, mensaje y acciones | — |
| **Cliente HTTP** | [`services/api_client.md`](./services/api_client.md) | Comunicación con el backend | `api` (Django) y `fastApi`; token en memoria; renovación con cookie | — |
| **Contexto de autenticación** | [`context/auth_context.md`](./context/auth_context.md) | Sesión global | Usuario, permisos (`hasPermission`), tema | — |
| **Rutas protegidas** | [`routing/protected_route.md`](./routing/protected_route.md) | Control de acceso a rutas | Sesión requerida, roles y permisos, pantalla de carga | — |
| **Panel lateral derecho (drawer)** | [`drawer/drawer.md`](./drawer/drawer.md) | Crear/editar y detalle | Deslizamiento derecho, cabecera y pie fijos, mini-KPIs | — |
| **Grupo de acciones con icono** | [`button/icon_action_group.md`](./button/icon_action_group.md) | Barra de acciones de tabla | Caja compacta de 28px: nuevo, Excel, recargar | — |
| **Filtros expandibles** | [`dropdown/expandable_filter_group.md`](./dropdown/expandable_filter_group.md) | Filtros de cabecera | Segmentados, badge del valor activo, limpiar filtros | — |
| **Límite de errores** | [`error_boundary/error_boundary.md`](./error_boundary/error_boundary.md) | Tolerancia a fallos | Detección de versión nueva (`ChunkLoadError`) y recuperación | — |
| **Modal de sesión expirada** | [`modal/session_expiration_modal.md`](./modal/session_expiration_modal.md) | Aviso de sesión | Evento `session-expired`, aviso previo al vencimiento | — |
| **Panel de notificaciones** | [`notification/notification_popover.md`](./notification/notification_popover.md) | Centro de alertas en el TopHeader | Campana, pestañas por categoría, contadores, acciones en línea | tiendita, vibra |
| **Modal de firma** | [`signature/signature_modal.md`](./signature/signature_modal.md) | Firma manuscrita | Lienzo de alta densidad, recorte automático, trazo mínimo | tiendita, app_tic |
| **Escáner de códigos** | [`scanner/scanner_modal.md`](./scanner/scanner_modal.md) | Lectura de barras/QR con cámara | `html5-qrcode`, una sola lectura, cierre automático | tiendita, contenedores |
| **Previsualizador PDF** | [`pdf/pdf_preview_frame.md`](./pdf/pdf_preview_frame.md) | Visor de documentos | Hojas apiladas, zoom real, worker local, reintento | tiendita |
| **Calendario** | [`calendar/corporate_calendar.md`](./calendar/corporate_calendar.md) | Turnos y novedades | Rejilla mensual, colores por tipo, fecha local | vibra |
| **Tooltip de texto truncado** | [`tooltip/truncated_tooltip.md`](./tooltip/truncated_tooltip.md) | Leer texto cortado en tablas | Teclado y fijación por clic | tiendita, app_tic |
| **Banner de instalación PWA** | [`pwa/pwa_install_banner.md`](./pwa/pwa_install_banner.md) | Instalar la app en celulares/quioscos | `beforeinstallprompt`, modo standalone, descarte por sesión | porterias |
| **Cargadores y esqueletos** | [`loader/page_loader.md`](./loader/page_loader.md) | Estados de carga | Logo animado, spinner, `TableSkeleton` | contenedores, vibra, app_tic |
| **Tiempo real (polling)** | [`realtime/js_polling_architecture.md`](./realtime/js_polling_architecture.md) | Datos en vivo | `useSmartPolling`: sin solapamiento, cancelación, pausa con pestaña oculta | app_tic, tiendita |
| **Roles y permisos** | [`roles/roles_admin_sidebar.md`](./roles/roles_admin_sidebar.md) | Administrar permisos | Drawer con matriz por grupos, permisos en `JSONField`, validación en backend | tiendita |
| **Gráficas** | [`charts/analytics_charts.md`](./charts/analytics_charts.md) | Visualización de datos | Área, barras, dona y minigráfica en SVG | — |
| **Escáner facial** | [`biometrics/facial_scanner.md`](./biometrics/facial_scanner.md) | Captura del rostro | Guía ovalada, cambio de cámara, zoom, liberación de cámara | contenedores |
| **Interruptor (toggle)** | [`toggle/toggle_switch.md`](./toggle/toggle_switch.md) | Activar/desactivar | Tamaños `sm`/`md`, estado de carga | — |
| **Tarjeta estructurada** | [`card/corporate_card.md`](./card/corporate_card.md) | Contenido con cabecera/cuerpo/pie | Tres secciones, acciones agrupadas | — |
| **Modales avanzados** | [`modal/advanced_pro_modal.md`](./modal/advanced_pro_modal.md) | Diálogos de seguridad y flujos | Reconfirmación de contraseña, asistente, maestro-detalle | — |
| **Firma con varios firmantes** | [`signature/multi_party_signature.md`](./signature/multi_party_signature.md) | Actas y acuerdos | Firma electrónica con evidencia generada en el servidor | — |
| **Gráficas avanzadas** | [`charts/advanced_analytics_charts.md`](./charts/advanced_analytics_charts.md) | Análisis multidimensional | Gantt, radar, gauge con umbrales, Sankey, mapa de calor | — |
| **Cargador de archivos** | [`upload/file_uploader_pro.md`](./upload/file_uploader_pro.md) | Adjuntos y evidencias | Arrastrar y soltar, firma de bytes, SHA-256, progreso y cancelación | — |
| **Línea de tiempo** | [`timeline/activity_timeline.md`](./timeline/activity_timeline.md) | Trazabilidad | Nodos por estado, cambios antes/después | — |
| **Asistente por etapas** | [`stepper/stepper_wizard.md`](./stepper/stepper_wizard.md) | Flujos por pasos | Indicador accesible, salto controlado entre pasos | — |
| **Dashboard de uso** | [`dashboard/platform_usage_dashboard.md`](./dashboard/platform_usage_dashboard.md) | Adopción y mejora continua | Usuarios activos, ranking de módulos, widget de opinión | — |
| **Estado del servidor** | [`dashboard/server_status_dashboard.md`](./dashboard/server_status_dashboard.md) | Operación y soporte | Punto de estado, servicios en tacómetros, peticiones por plataforma, recursos, logs enmascarados | — |
| **Tutorial dividido** | [`tutorial/split_tutorial_walkthrough.md`](./tutorial/split_tutorial_walkthrough.md) | Guías paso a paso | Parámetros a la izquierda, pasos con capturas a la derecha | bi (DataHub) |
| **Catálogo de endpoints** | [`services/endpoints_registry.md`](./services/endpoints_registry.md) | Rutas de servicio centralizadas | `endpoints.ts` en frontend y `endpoints_registry.json` en backend | — |

Además: [`mockup_template.html`](./mockup_template.html) es una plantilla HTML autocontenida (sin compilación) para maquetar pantallas con los mismos tokens y patrones.

---

## Principios de los componentes

1. **Tokens, no colores fijos.** El CSS de los componentes DEBE usar las variables de `variables.css`.
   - **Por qué:** garantiza que todo funcione en Modo Noche y Día y que un cambio de marca se haga en un solo archivo.
2. **Contratos de props tipados.** Cada componente DEBERÍA definir una interfaz TypeScript con sus propiedades obligatorias y opcionales (sin `any`).
3. **Accesibilidad.** Diálogos con `role="dialog"`, `aria-modal`, título asociado, cierre con `Escape` y foco controlado; botones solo-icono con `aria-label`; controles con etiqueta asociada.
4. **Sin dependencias del entorno local.** Los recursos (SVG, estilos) están en las especificaciones o se empaquetan con la app; las librerías externas se fijan a una versión.
5. **Layout de ancho completo.** Las vistas operativas DEBERÍAN ocupar todo el ancho de la pantalla; solo modales, diálogos de escáner/firma y la tarjeta de login se centran.
   - **Por qué:** las pantallas operativas muestran tablas y filtros extensos; un contenedor estrecho desperdicia espacio en monitores anchos.
   - **Excepciones:** se puede desviar con una decisión registrada (ADR) o por pedido explícito del usuario.
