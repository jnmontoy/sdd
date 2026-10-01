# Catálogo de Componentes UI — Spec-Driven Development (SDD)
## Sistema de Componentes Reutilizables de Greenyard / Jolifoods

Este directorio contiene las especificaciones atómicas de los componentes de interfaz de usuario (UI) que integran las páginas del ecosistema. 

Bajo la metodología **Spec-Driven Development (SDD)**, un componente no se codifica de manera aislada ni con estilos arbitrarios: cada componente tiene una especificación formal con su **estructura HTML/JSX, clases CSS exactas, variantes admitidas, estados interactivos y normas de accesibilidad**.

> **SELECCIÓN RÁPIDA DE VARIANTES**:  
> Si deseas ver las opciones y variantes disponibles para un componente específico (KPI, Tabla, Modal, Drawer, Select, etc.), consulta [`../greenyard/04_menus_de_seleccion_por_componente.md`](../greenyard/04_menus_de_seleccion_por_componente.md).

---

## Índice de Componentes del Sistema

| Componente | Archivo de Especificación | Uso Principal | Variantes Disponibles |
| :--- | :--- | :--- | :--- |
| **Variables Globales** | [`variables.css`](./variables.css) / [`variables.md`](./variables.md) | Tokens CSS y tema global | Modo Noche (`:root`), Modo Día (`[data-theme='light']`) |
| **Logo Corporativo** | [`login/logo.md`](./login/logo.md) | Encabezado institucional | Isotipo, Logotipo completo, Monocromático, Glass-badge |
| **Cards & Contenedores** | [`login/card.md`](./login/card.md) | Contenedor principal de formulario | Centered Glass Card, Split-Screen Hero, Kiosk Minimal |
| **Botón Microsoft SSO** | [`login/button_microsoft.md`](./login/button_microsoft.md) | Inicio de sesión corporativo M365 | Cuadrícula oficial SVG 4 colores, Dark, Light |
| **Campos de Entrada (Inputs)** | [`login/input_field.md`](./login/input_field.md) | Documento y Contraseña | Con icono prefijo, con botón toggle ojo, con estado de error |
| **Botón Primario & Loaders** | [`login/button_primary.md`](./login/button_primary.md) | Botón "Iniciar Sesión" / Submit | Esmeralda Glow, Con spinner Lucide, Deshabilitado |
| **Feedback y Alertas** | [`login/feedback_alerts.md`](./login/feedback_alerts.md) | Mensajes de error y validación | Banner shake en línea, Toast Sonner, Modal inactividad |
| **Formulario Restablecimiento** | [`login/recovery_form.md`](./login/recovery_form.md) | Solicitud y nueva clave | Modal de solicitud cédula/email y formulario de nueva contraseña |
| **Formulario Completo Login** | [`login/login_form.md`](./login/login_form.md) | Ensamblado completo | Formulario integrado con tabs, remember me y enlace recuperación |
| **Plantilla Correo Corporativo** | [`login/email_recovery_template.md`](./login/email_recovery_template.md) | Notificación de recuperación | HTML responsivo con inline-styles compatible con Outlook y Gmail |
| **Top Navbar** | [`layout/navbar.md`](./layout/navbar.md) | Cabecera persistente y título de módulo | Título en extremo izquierdo (`.topheader-left`) junto a marca, conmutador Noche/Día, Notificaciones, Perfil |
| **Reglas de Layout Horizontal** | [`layout/layout_rules.md`](./layout/layout_rules.md) | Norma inflexible: Prohibido centrar vistas | 100% Horizontal a lo largo de la pantalla (full-width), CERO cajas centradas tipo blog |
| **Menú de Perfil y Salida** | [`layout/user_profile_dropdown.md`](./layout/user_profile_dropdown.md) | Dropdown de sesión en TopHeader (`vibra`/`tiendita`) | Avatar interactivo, datos del colaborador, rol, enlace Mi Perfil y botón Salir con ConfirmModal |
| **Sidebar Colapsable** | [`layout/sidebar.md`](./layout/sidebar.md) | Navegación de módulos (Opcional) | Opcional (Full-Width por defecto; CERO sidebar a menos que el usuario lo pida expresamente) |
| **Tabla de Datos (Data Table)** | [`data_table/data_table.md`](./data_table/data_table.md) | Listados y CRUDs | Paginación servidor Anti-N+1, Buscador debounce, Exportar Excel/PDF |
| **Filtro Columna Tipo Excel** | [`data_table/checklist_popover.md`](./data_table/checklist_popover.md) | Filtros de tabla tipo Excel | Ordenar A-Z/Z-A, buscador interactivo, checklist con conteo y botón "Solo" |
| **Columnas Redimensionables** | [`data_table/column_resizer.md`](./data_table/column_resizer.md) | Ajuste interactivo de ancho en `<th>` | Arrastre `col-resize`, reset con doble clic, min-width 60px y persistencia local |
| **Visibilidad de Columnas** | [`data_table/column_visibility.md`](./data_table/column_visibility.md) | Selector desplegable de columnas | Trigger `Columns3`, checkboxes con conteo, enlaces Todas/Restablecer |
| **Tarjetas KPI (BI Cartera)** | [`kpi/kpi_cards.md`](./kpi/kpi_cards.md) | Métricas e indicadores | Rejilla inteligente, clickeables como filtros rápidos, cajas de iconos y skeletons |
| **Modal Accesible (Dialog)** | [`modal/modal_dialog.md`](./modal/modal_dialog.md) | Diálogos y formularios | Variantes `sm`, `md`, `lg`, `xl` con backdrop blur y focus trap |
| **Confirm Modal Corporativo** | [`modal/confirm_modal.md`](./modal/confirm_modal.md) | Reemplazo de `confirm()` | Modal con portal, spinner de carga, halo de color y opción `emphasizeCancel` |
| **Badges de Estado** | [`badge/badge_status.md`](./badge/badge_status.md) | Indicadores de rol y estado | `success`, `danger`, `warning`, `info`, `admin`, `operator` |
| **Selector Tipo Búsqueda** | [`dropdown/select_filter.md`](./dropdown/select_filter.md) | Selectores y filtros | Reemplazo de `<select>` con buscador interactivo y navegación por teclado |
| **Notificaciones Toast** | [`toast/toast_notification.md`](./toast/toast_notification.md) | Feedback asíncrono no bloqueante | Variantes `success`, `error`, `warning`, `info` con botón de acción opcional |
| **Paginación Avanzada** | [`pagination/pagination.md`](./pagination/pagination.md) | Navegación de registros masivos | Server-side friendly, resumen numérico, elipsis y selector de filas por página |
| **Exportación a Excel** | [`export/excel_export.md`](./export/excel_export.md) | Descarga tabular formateada | Frontend con `xlsx` y streaming backend, auto-ancho y respeto a filtros |
| **Estado Vacío (Empty State)** | [`empty_state/empty_state.md`](./empty_state/empty_state.md) | Vistas o búsquedas sin datos | Iconos dinámicos, mensajes constructivos y botones de acción primaria/secundaria |
| **Cliente HTTP Doble** | [`services/api_client.md`](./services/api_client.md) | Comunicación backend centralizada | Doble instancia (`api` y `fastApi`), interceptores Bearer y 401 redirect |
| **Contexto de Autenticación** | [`context/auth_context.md`](./context/auth_context.md) | Estado global de sesión | Tipado de usuario, tokens, RBAC (`hasRole`, `isAdmin`) y tema Noche/Día |
| **Rutas Protegidas (RBAC)** | [`routing/protected_route.md`](./routing/protected_route.md) | Guardias de navegación | Verificación de token, control RBAC declarativo y pantalla de carga |
| **Panel Lateral (Drawer)** | [`drawer/drawer.md`](./drawer/drawer.md) | Inspección y formularios contextuales | Deslizamiento lateral derecho obligatorio (`.cartera-sidebar-drawer`), backdrop blur, mini-KPIs |
| **Acciones Compactas de Iconos** | [`button/icon_action_group.md`](./button/icon_action_group.md) | Barra de acciones en tablas (sin texto) | Caja compacta 28px (`.cartera-compact-action-box`) con iconos agrupados: `Plus`, `FileSpreadsheet` verde, `RefreshCw` |
| **Filtros Expandibles Superiores** | [`dropdown/expandable_filter_group.md`](./dropdown/expandable_filter_group.md) | Filtros de cabecera con despliegue horizontal | Segmentado (`.cartera-btn-group`), triggers con badge dinámico y botón de limpieza `FilterX` |
| **Límite de Errores (Boundary)** | [`error_boundary/error_boundary.md`](./error_boundary/error_boundary.md) | Tolerancia a fallos y auto-recarga | Detección de ChunkLoadError (nuevas versiones) y rescate de UI |
| **Modal de Sesión Expirada** | [`modal/session_expiration_modal.md`](./modal/session_expiration_modal.md) | Alerta no intrusiva de sesión | Desacoplado por eventos (401), advertencia de inactividad y retorno a login |
| **Panel de Multi-Notificaciones** | [`notification/notification_popover.md`](./notification/notification_popover.md) | Centro de alertas en TopHeader (`tiendita`/`vibra`) | Campana interactiva, pestañas multi-categoría, badges numéricos y acciones en línea |
| **Firma Digitalizada (Modal)** | [`signature/signature_modal.md`](./signature/signature_modal.md) | Captura táctil y ratón con auto-recorte | Canvas escalado, algoritmo `cropToSignature`, PNG transparente Base64 (`tiendita`/`app_tic`) |
| **Escáner Barcode / QR** | [`scanner/scanner_modal.md`](./scanner/scanner_modal.md) | Lectura por cámara web y móvil | Integración con `html5-qrcode`, auto-cierre y visor centrado (`tiendita`/`contenedores`) |
| **Previsualizador de PDF** | [`pdf/pdf_preview_frame.md`](./pdf/pdf_preview_frame.md) | Visor de documentos en Canvas | Hojas físicas apiladas, paginación, zoom fluido e integración con `pdfjs-dist` (`tiendita`) |
| **Calendario Corporativo** | [`calendar/corporate_calendar.md`](./calendar/corporate_calendar.md) | Gestión mensual de turnos y novedades | Rejilla mensual inteligente, badges cromáticos por evento y filtrado (`vibra`) |
| **Tooltip Truncado Inteligente** | [`tooltip/truncated_tooltip.md`](./tooltip/truncated_tooltip.md) | Lectura de elipsis en tablas | Despliegue sin romper layout, soporte de teclado y fijación por clic (`tiendita`/`app_tic`) |
| **Banner de Instalación PWA** | [`pwa/pwa_install_banner.md`](./pwa/pwa_install_banner.md) | Prompt de instalación en móviles/kioscos | Detección `beforeinstallprompt`, modo standalone y descarte en sesión (`porterias`) |
| **Cargadores y Skeletons** | [`loader/page_loader.md`](./loader/page_loader.md) | Estados de carga y transiciones de ruta | Isotipo animado Jolifoods, spinner giratorio y `TableSkeleton` shimmer (`contenedores`/`vibra`/`app_tic`) |
| **Tiempo Real (JS Polling)** | [`realtime/js_polling_architecture.md`](./realtime/js_polling_architecture.md) | Polling reactivo y monitoreo en vivo | `useSmartPolling`, `AbortController`, `visibilityState`, sin caídas de túnel (`app_tic`/`tiendita`) |
| **Gráficas y Analítica (Charts)** | [`charts/analytics_charts.md`](./charts/analytics_charts.md) | Dashboards y visualización de datos | Área suave con gradiente, barras redondeadas, donut porcentual y sparklines |
| **Escáner Biométrico Facial** | [`biometrics/facial_scanner.md`](./biometrics/facial_scanner.md) | Captura y verificación biométrica facial | Guía oval con cortinilla, conmutador de cámara, zoom dinámico y validación de encuadre (`contenedores`) |
| **Interruptor Conmutador (Toggle)** | [`toggle/toggle_switch.md`](./toggle/toggle_switch.md) | Activar/desactivar estado inmediato | Conmutador esmeralda accesible, variantes `sm`/`md`, spinner de carga (`usuarios`/`config`) |


---

## Principios de Portabilidad en Componentes SDD

1. **CSS Puro y Utility-Classes**: Las especificaciones proporcionan tanto el CSS Vanilla canónico (tokens de variables CSS) como las clases equivalentes de Tailwind para máxima flexibilidad.
2. **Cero Dependencia de Entornos Locales**: Los assets SVG y estilos están autocontenidos en las especificaciones en código vectorial o CSS reproducible.
3. **Contratos de Props**: Cada componente define una interfaz TypeScript estricta con sus propiedades obligatorias y opcionales.
4. **Layout 100% Horizontal (Prohibido Desarrollos Centrados)**: Toda interfaz y módulo operativo se expande a lo largo de la pantalla de extremo a extremo (`width: 100%`, `w-full`). Queda terminantemente prohibido encoger o centrar vistas principales en columnas estrechas (`max-w-xl mx-auto`). Solo los diálogos emergentes modales o la tarjeta previa de login admiten centrado.

