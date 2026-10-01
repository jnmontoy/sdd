# Ecosistema Greenfield / Jolifoods — Especificaciones SDD
## Guía Central de Arquitectura, Componentes y Catálogo Interactivo

Bienvenido al repositorio central de especificaciones de desarrollo guiado por especificaciones (**Spec-Driven Development - SDD**) para el ecosistema de aplicaciones de **Greenfield / Jolifoods** (desarrollo limpio desde cero).

---

## 1. Menús Interactivos de Selección y Armado de Componentes

Para armar cualquier pantalla, CRUD o módulo, la IA y los desarrolladores disponen de los siguientes catálogos interactivos:

| Documento | Propósito | Enlace Directo |
| :--- | :--- | :--- |
| **Catálogo de Complementos (1 a 22)** | Menú maestro de selección para incorporar módulos y funcionalidades al proyecto | [`02_catalogo_y_menu_de_complementos.md`](./02_catalogo_y_menu_de_complementos.md) |
| **Menús de Selección por Componente** | Opciones y variantes para cada componente individual (Tablas, KPIs, Modales, Drawers, etc.) | [`04_menus_de_seleccion_por_componente.md`](./04_menus_de_seleccion_por_componente.md) |
| **Normativa y Buenas Prácticas** | Reglas inflexibles: `.venv` obligatorio, layout 100% horizontal y uso de componentes auditados | [`00_normativa_buenas_practicas_y_auditoria.md`](./00_normativa_buenas_practicas_y_auditoria.md) |
| **Calificación y Madurez (10.0/10.0)** | Evaluación por pilares arquitectónicos y balance en los 7 proyectos del ecosistema | [`01_calificacion_final_ecosistema_sdd.md`](./01_calificacion_final_ecosistema_sdd.md) |
| **Asistente de Diseño de Páginas** | Flujo paso a paso para diseñar vistas y módulos interactivos | [`03_asistente_interactivo_diseno_paginas.md`](./03_asistente_interactivo_diseno_paginas.md) |
| **Metodología Mocks No-Code** | Prototipado rápido en 4 archivos para usuarios funcionales y líderes de negocio | [`05_metodologia_mocks_no_programadores.md`](./05_metodologia_mocks_no_programadores.md) |
| **Guía Maestra SDD (Universal)** | Manual operativo agnóstico y portable de desarrollo | [`SPEC_GUIDE.md`](./SPEC_GUIDE.md) |

---

## 2. Catálogo Completo de Componentes UI Auditados (`.sdd/components/`)

Todos los componentes están listos para ser seleccionados y ensamblados sin inventar CSS:

1. **Variables y Tema**: [`variables.css`](../components/variables.css) — Tokens Modo Noche / Modo Día.
2. **Layout Maestro**: [`layout/layout_rules.md`](../components/layout/layout_rules.md) y [`layout/navbar.md`](../components/layout/navbar.md) (100% Horizontal de extremo a extremo).
3. **Tablas Masivas**: [`data_table/data_table.md`](../components/data_table/data_table.md), [`data_table/checklist_popover.md`](../components/data_table/checklist_popover.md), [`data_table/column_resizer.md`](../components/data_table/column_resizer.md) y [`data_table/column_visibility.md`](../components/data_table/column_visibility.md).
4. **Toolbars y Botones**: [`button/icon_action_group.md`](../components/button/icon_action_group.md) (Caja compacta 28px y fila 26px).
5. **Métricas y KPIs**: [`kpi/kpi_cards.md`](../components/kpi/kpi_cards.md) — Tarjetas interactivas con filtro cruzado.
6. **Gráficas Analíticas**: [`charts/analytics_charts.md`](../components/charts/analytics_charts.md) — Área gradiente, barras redondeadas, donut y sparklines.
7. **Modales y Diálogos**: [`modal/confirm_modal.md`](../components/modal/confirm_modal.md), [`modal/modal_dialog.md`](../components/modal/modal_dialog.md) y [`modal/session_expiration_modal.md`](../components/modal/session_expiration_modal.md).
8. **Detalle y Edición Lateral**: [`drawer/drawer.md`](../components/drawer/drawer.md) — Right Drawer deslizable.
9. **Selectores con Búsqueda**: [`dropdown/select_filter.md`](../components/dropdown/select_filter.md) y [`dropdown/expandable_filter_group.md`](../components/dropdown/expandable_filter_group.md).
10. **Biometría Facial**: [`biometrics/facial_scanner.md`](../components/biometrics/facial_scanner.md) — Escáner con guía oval y cortinilla.
11. **Firma Digital**: [`signature/signature_modal.md`](../components/signature/signature_modal.md) — Canvas con auto-recorte `cropToSignature`.
12. **Escáner Barcode / QR**: [`scanner/scanner_modal.md`](../components/scanner/scanner_modal.md) — Cámara WebRTC con `html5-qrcode`.
13. **Visor de PDF**: [`pdf/pdf_preview_frame.md`](../components/pdf/pdf_preview_frame.md) — Canvas PDF con zoom y hojas apiladas.
14. **Calendario Corporativo**: [`calendar/corporate_calendar.md`](../components/calendar/corporate_calendar.md) — Programación de turnos y novedades.
15. **Centro de Notificaciones**: [`notification/notification_popover.md`](../components/notification/notification_popover.md) — Popover con pestañas.
16. **PWA Kiosco / Mobile**: [`pwa/pwa_install_banner.md`](../components/pwa/pwa_install_banner.md) — Banner de instalación.
17. **Cargadores y Skeletons**: [`loader/page_loader.md`](../components/loader/page_loader.md) — Isotipo pulsante y shimmers en tabla.
18. **Alertas Flotantes**: [`toast/toast_notification.md`](../components/toast/toast_notification.md) — Toasts Sonner corporativos.
19. **Paginación Avanzada**: [`pagination/pagination.md`](../components/pagination/pagination.md) y **Exportación**: [`export/excel_export.md`](../components/export/excel_export.md).
20. **Estados Vacíos**: [`empty_state/empty_state.md`](../components/empty_state/empty_state.md) y **Badges**: [`badge/badge_status.md`](../components/badge/badge_status.md).
21. **Resiliencia de Frontend**: [`error_boundary/error_boundary.md`](../components/error_boundary/error_boundary.md) — Auto-recarga ante `ChunkLoadError`.
22. **Tiempo Real**: [`realtime/js_polling_architecture.md`](../components/realtime/js_polling_architecture.md) — Smart Polling sin caídas.
23. **Interruptor Conmutador**: [`toggle/toggle_switch.md`](../components/toggle/toggle_switch.md) — Activar/suspender usuarios y opciones.

