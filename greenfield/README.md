# `greenfield/` — normativa, guías y protocolos del SDD

Documentos para construir proyectos nuevos (**modo greenfield**: desarrollo desde cero) y para evolucionar proyectos existentes de Joli Foods con el método de desarrollo guiado por especificaciones (**SDD**, *Spec-Driven Development*).

Lenguaje normativo: **DEBE / NO DEBE** (obligatorio, para seguridad e integridad), **DEBERÍA** (convención; se puede desviar con un ADR o pedido explícito), **PUEDE** (opcional), según la RFC 2119.

---

## 1. Por dónde empezar

| Documento | Para qué sirve |
| :--- | :--- |
| [`SPEC_GUIDE.md`](./SPEC_GUIDE.md) | Guía maestra: niveles de formalidad, preguntas iniciales, estructura de proyecto. |
| [`00_normativa_buenas_practicas_y_auditoria.md`](./00_normativa_buenas_practicas_y_auditoria.md) | Fuente única de las buenas prácticas BP-01 a BP-22 y lista de verificación. |
| [`01_calificacion_final_ecosistema_sdd.md`](./01_calificacion_final_ecosistema_sdd.md) | Evaluación de madurez: qué está implementado, qué solo documentado y qué falta. |

## 2. Catálogos y asistentes de diseño

| Documento | Para qué sirve |
| :--- | :--- |
| [`02_catalogo_y_menu_de_complementos.md`](./02_catalogo_y_menu_de_complementos.md) | Menú de 32 complementos con preguntas por cada uno. |
| [`03_asistente_interactivo_diseno_paginas.md`](./03_asistente_interactivo_diseno_paginas.md) | Flujo guiado para diseñar una página antes de programar. |
| [`04_menus_de_seleccion_por_componente.md`](./04_menus_de_seleccion_por_componente.md) | Variantes de cada componente (tablas, KPI, modales, drawers…). |
| [`05_metodologia_mocks_no_programadores.md`](./05_metodologia_mocks_no_programadores.md) | Prototipos sin código para usuarios de negocio y su paso a React. |

## 3. Protocolos de ingeniería

| # | Protocolo | Estado de herramientas en el SDD |
| :--- | :--- | :--- |
| 06 | [DevOps, CI/CD y puertas de calidad](./06_protocolo_devops_cicd_y_calidad.md) | Normativo; sin CI ni pre-commit de referencia en `stack/`. |
| 07 | [Observabilidad y telemetría](./07_protocolo_observabilidad_telemetria_apm.md) | Sondas de salud implementadas; resto normativo. |
| 08 | [Migraciones sin interrupción y recuperación](./08_protocolo_migraciones_zero_downtime.md) | Normativo. |
| 09 | [Gobierno de APIs y cambios incompatibles](./09_protocolo_gobernanza_apis_y_breaking_changes.md) | Normativo; `oasdiff` no integrado aún. |
| 10 | [Incidentes y post-mortem sin culpa](./10_protocolo_incidentes_sre_y_postmortem.md) | Normativo. |
| 11 | [Pruebas automáticas y E2E](./11_protocolo_pruebas_automaticas_y_testing_e2e.md) | `pytest.ini`, `requirements-dev.txt` y validador generados por el andamiaje. |
| 12 | [Ciclo de vida y mejora continua](./12_protocolo_ciclo_de_vida_sdlc_y_mejora_continua.md) | Normativo. |
| 13 | [Fuentes y procedencia de los patrones](./13_catalogo_innovaciones_y_mejores_practicas_proyectos.md) | Referencia. |
| 14 | [Cambios atómicos y especificaciones vivas](./14_protocolo_cambios_atomicos_y_especificaciones_vivas.md) | Plantilla en [`../changes_template/`](../changes_template/README.md). |
| 15 | [Memoria persistente del proyecto](./15_protocolo_memoria_persistente_y_aprendizaje_agentes.md) | Plantilla en [`../memory/`](../memory/README.md). |

Otros: [`config_referencia.env.example`](./config_referencia.env.example) (variables de entorno de referencia) y [`pages/`](./pages/README.md) (especificaciones de páginas).

---

## 4. Componentes de interfaz (`.sdd/components/`)

Catálogo completo y actualizado: [`../components/README.md`](../components/README.md). Los más usados:

1. **Tokens y tema**: [`variables.css`](../components/variables.css) — claro / oscuro.
2. **Layout**: [`layout_rules.md`](../components/layout/layout_rules.md), [`navbar.md`](../components/layout/navbar.md) — ancho completo.
3. **Tablas**: [`data_table.md`](../components/data_table/data_table.md), [`checklist_popover.md`](../components/data_table/checklist_popover.md), [`column_resizer.md`](../components/data_table/column_resizer.md), [`column_visibility.md`](../components/data_table/column_visibility.md).
4. **Acciones**: [`icon_action_group.md`](../components/button/icon_action_group.md) — barra de 28 px y fila de 26 px.
5. **KPI**: [`kpi_cards.md`](../components/kpi/kpi_cards.md).
6. **Gráficas**: [`analytics_charts.md`](../components/charts/analytics_charts.md), [`advanced_analytics_charts.md`](../components/charts/advanced_analytics_charts.md).
7. **Modales**: [`confirm_modal.md`](../components/modal/confirm_modal.md), [`modal_dialog.md`](../components/modal/modal_dialog.md), [`session_expiration_modal.md`](../components/modal/session_expiration_modal.md).
8. **Drawer**: [`drawer.md`](../components/drawer/drawer.md).
9. **Selectores y filtros**: [`select_filter.md`](../components/dropdown/select_filter.md), [`expandable_filter_group.md`](../components/dropdown/expandable_filter_group.md).
10. **Captura**: [`facial_scanner.md`](../components/biometrics/facial_scanner.md), [`signature_modal.md`](../components/signature/signature_modal.md), [`scanner_modal.md`](../components/scanner/scanner_modal.md), [`file_uploader_pro.md`](../components/upload/file_uploader_pro.md).
11. **Documentos y calendario**: [`pdf_preview_frame.md`](../components/pdf/pdf_preview_frame.md), [`corporate_calendar.md`](../components/calendar/corporate_calendar.md).
12. **Avisos y estados**: [`notification_popover.md`](../components/notification/notification_popover.md), [`toast_notification.md`](../components/toast/toast_notification.md), [`empty_state.md`](../components/empty_state/empty_state.md), [`badge_status.md`](../components/badge/badge_status.md), [`page_loader.md`](../components/loader/page_loader.md).
13. **Navegación de datos**: [`pagination.md`](../components/pagination/pagination.md), [`excel_export.md`](../components/export/excel_export.md).
14. **Resiliencia y tiempo real**: [`error_boundary.md`](../components/error_boundary/error_boundary.md), [`js_polling_architecture.md`](../components/realtime/js_polling_architecture.md).
15. **Otros**: [`pwa_install_banner.md`](../components/pwa/pwa_install_banner.md), [`toggle_switch.md`](../components/toggle/toggle_switch.md).
