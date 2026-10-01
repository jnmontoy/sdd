# Catálogo y Menús de Variantes por Componente (Pick & Copy)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

Este documento contiene los **menús interactivos de selección rápida** que la Inteligencia Artificial debe presentar cuando un usuario solicite cualquier tipo de componente (ej: *"quiero un componente de KPI"*, *"quiero una tabla"*, *"quiero un modal"*, etc.).

Al seleccionar la opción deseada, el sistema ya cuenta con el código **TypeScript/React (TSX)** y los **estilos CSS** exactos listos para copiar y usar (*Drop-in Ready*), sin requerir conocimientos de proyectos anteriores.

---

## 1. Menú si el usuario dice: *"Quiero un componente de KPI / Métricas"*

> *"¿Cuál variante de tarjeta KPI deseas implementar para tu pantalla?"*

```text
====================================================================================================
                       OPCIONES DE TARJETAS KPI (INDICADORES DE NEGOCIO)
====================================================================================================
 [1] Card KPI Clásica (Métrica Simple)
     -> Estructura: Contenedor con fondo elevado, valor numérico grande, etiqueta y caja de icono
        con halo cromático (.icon-blue, .icon-amber, .icon-pink, .icon-emerald, .icon-cyan).
     -> Código y CSS listos en: .sdd/components/kpi/kpi_cards.md (Sección Variante 1)

 [2] Card KPI Interactiva con Filtro Activo (Estándar Recomendado)
     -> Estructura: Tarjeta clickeable (cursor pointer, translateY hover), estado .active-filter
        con borde de acento, y badge flotante pulsante 'FILTRO ACTIVO'. Al hacer clic activa
        un filtro dinámico en la tabla inferior.
     -> Código y CSS listos en: .sdd/components/kpi/kpi_cards.md (Sección Variante 2)

 [3] Card KPI con Indicador de Tendencia (Delta Porcentual)
     -> Estructura: Métrica principal acompañada de un badge de tendencia (+12.5% o -4.2%)
        con flecha verde/roja y leyenda 'vs mes anterior'.
     -> Código y CSS listos en: .sdd/components/kpi/kpi_cards.md (Sección Variante 3)

 [4] Card KPI con Barra de Progreso / Meta
     -> Estructura: Valor actual contra meta presupuestada (ej. $85M / $100M) con barra de progreso
        cromática animada y porcentaje de cumplimiento.
     -> Código y CSS listos en: .sdd/components/kpi/kpi_cards.md (Sección Variante 4)

 [5] Rejilla Completa Responsive de KPIs (.cartera-kpi-row)
     -> Estructura: Fila inteligente que se adapta con scroll horizontal táctil en dispositivos móviles
        y minmax(210px, 1fr) en escritorio, con soporte de Skeleton Loaders pulsantes.
     -> Código y CSS listos en: .sdd/components/kpi/kpi_cards.md (Sección Rejilla y Skeletons)
====================================================================================================
```

---

## 2. Menú si el usuario dice: *"Quiero una Tabla / Data Table"*

> *"¿Cuál variante de tabla de datos se adapta mejor a tu necesidad?"*

```text
====================================================================================================
                         OPCIONES DE TABLAS DE DATOS (DATA TABLE)
====================================================================================================
 [1] Tabla Corporativa Completa (Filtros Tipo Excel)
     -> Estructura: Encabezados <th> con ChecklistPopover (A-Z/Z-A, buscador reactivo, botón 'Solo'),
        paginación server-side, exportador a Excel, selector de columnas (Columns3) y sticky headers.
     -> Código y CSS listos en: .sdd/components/data_table/data_table.md

 [2] Tabla Compacta / Resumen Operativo
     -> Estructura: Tabla de lectura rápida con filas clickeables para inspección, badges de estado,
        alineación numérica a la derecha y paginador simplificado.
     -> Código y CSS listos en: .sdd/components/data_table/data_table.md (Variante Compacta)

 [3] Tabla con Selección Múltiple y Acciones Masivas
     -> Estructura: Casilla checkbox general en <th> y en cada fila, contador de 'X filas seleccionadas'
        y barra flotante inferior con acciones en lote (Exportar selección, Desactivar lote).
     -> Código y CSS listos en: .sdd/components/data_table/data_table.md (Variante Multi-select)
====================================================================================================
```

---

## 3. Menú si el usuario dice: *"Quiero un Modal / Diálogo"*

> *"¿Cuál variante de modal o diálogo de confirmación necesitas?"*

```text
====================================================================================================
                              OPCIONES DE MODALES Y DIÁLOGOS
====================================================================================================
 [1] Diálogo de Confirmación Segura (ConfirmModal - Cero confirm nativo)
     -> Estructura: Modal renderizado vía portal, fondo difuminado (backdrop-filter: blur),
        icono con halo cromático (danger, warning, primary), spinner asíncrono y opción emphasizeCancel.
     -> Código y CSS listos en: .sdd/components/modal/confirm_modal.md

 [2] Modal de Formulario de Captura / Edición (ModalDialog)
     -> Estructura: Contenedor centrado con tamaños sm (400px), md (600px), lg (800px), xl (1024px),
        cabecera con botón cerrar, cuerpo con scroll interno y pie de botones de acción.
     -> Código y CSS listos en: .sdd/components/modal/modal_dialog.md

 [3] Modal de Sesión Expirada (SessionExpirationModal)
     -> Estructura: Alerta desacoplada por eventos (SESSION_EXPIRED_EVENT) cuando un token JWT expira,
        bloquea la interfaz y ofrece botón directo para reautenticarse sin perder la ruta previa.
     -> Código y CSS listos en: .sdd/components/modal/session_expiration_modal.md
====================================================================================================
```

---

## 4. Menú si el usuario dice: *"Quiero un Panel Lateral / Drawer"*

> *"¿Cuál variante de panel deslizante lateral (Drawer) deseas utilizar?"*

```text
====================================================================================================
                       OPCIONES DE PANELES LATERALES (DRAWER / SLIDE-OVER)
====================================================================================================
 [1] Drawer de Inspección Rápida (Size: 'sm' - 400px)
     -> Estructura: Deslizamiento desde la derecha, backdrop blur, cabecera fija, visor de detalles
        y metadatos clave de una fila seleccionada sin abandonar la tabla de fondo.
     -> Código y CSS listos en: .sdd/components/drawer/drawer.md

 [2] Drawer de Formulario y Edición (Size: 'md' - 600px)
     -> Estructura: Cuerpo scrollable para formularios medianos, validación de inputs y pie fijo
        inferior con botones 'Guardar Cambios' y 'Cancelar'.
     -> Código y CSS listos en: .sdd/components/drawer/drawer.md

 [3] Drawer Analítico con Pestañas (Size: 'lg' - 840px)
     -> Estructura: Panel ancho con sistema de pestañas internas para navegar entre información
        general, bitácora de auditoría histórica, archivos adjuntos y observaciones.
     -> Código y CSS listos en: .sdd/components/drawer/drawer.md
====================================================================================================
```

---

## 5. Menú si el usuario dice: *"Quiero un Selector / Dropdown"*

> *"¿Cuál variante de selector necesitas?"*

```text
====================================================================================================
                           OPCIONES DE SELECTORES Y DROPDOWNS
====================================================================================================
 [1] Searchable SelectFilter Simple (Reemplazo obligatorio del select nativo)
     -> Estructura: Desplegable accesible con campo de texto con filtro en vivo, navegación
        completa por teclado (flechas y Enter), badge de selección y mensaje de 'Sin resultados'.
     -> Código y CSS listos en: .sdd/components/dropdown/select_filter.md

 [2] Popover Checklist Tipo Excel (ChecklistPopover)
     -> Estructura: Menú para cabeceras con orden A-Z/Z-A, buscador reactivo, casillas con
        conteo dinámico de registros y botón táctico 'Solo' para aislar un valor.
     -> Código y CSS listos en: .sdd/components/data_table/checklist_popover.md
====================================================================================================
```

---

## 6. Menú si el usuario dice: *"Quiero Notificaciones / Toasts"*

> *"¿Cuál variante de notificación flotante necesitas?"*

```text
====================================================================================================
                           OPCIONES DE NOTIFICACIONES Y ALERTAS
====================================================================================================
 [1] Panel Desplegable de Multi-Notificaciones en TopHeader (Estándar Tiendita / Vibra)
     -> Estructura: Campana interactiva con badge de conteo (.bell-badge-count) que despliega
        popover con pestañas segmentadas (ej. Solicitudes, Stock Crítico, Novedades), badges
        por categoría, lista de alertas con avatar/icono, severidad (rojo/ámbar/azul/verde),
        acciones en línea (Aprobar, Ver en Drawer) y estado óptimo cuando no hay pendientes.
     -> Código y CSS listos en: .sdd/components/notification/notification_popover.md

 [2] Toast Flotante Autocerrable (ToastNotification)
     -> Estructura: Alerta no intrusiva con auto-cierre diferenciado (success: 3.5s, warning: 5s,
        error: 7s/persistente), icono contextual y colores institucionales Jolifoods.
     -> Código y CSS listos en: .sdd/components/toast/toast_notification.md

 [3] Toast con Botón de Acción / Deshacer (Undo / Retry)
     -> Estructura: Toast con botón adicional para deshacer una acción reversible o reintentar una petición.
     -> Código y CSS listos en: .sdd/components/toast/toast_notification.md

 [4] Banner de Alerta en Línea (Inline Feedback)
     -> Estructura: Caja de alerta con animación de sacudida (shake) para validación de formularios.
     -> Código y CSS listos en: .sdd/components/login/feedback_alerts.md
====================================================================================================
```

---

## 7. Menú si el usuario dice: *"Quiero un Estado Vacío / Empty State"*

> *"¿Cuál variante de estado vacío necesitas?"*

```text
====================================================================================================
                            OPCIONES DE ESTADO VACÍO (EMPTY STATE)
====================================================================================================
 [1] Filtros o Búsqueda Sin Resultados
     -> Estructura: Icono SearchX, mensaje 'No se encontraron coincidencias' y botón 'Restablecer Filtros'.
     -> Código y CSS listos en: .sdd/components/empty_state/empty_state.md

 [2] Bandeja o Listado Inicial Vacío
     -> Estructura: Icono Inbox, mensaje 'Aún no hay registros en este módulo' y botón 'Crear Primer Registro'.
     -> Código y CSS listos en: .sdd/components/empty_state/empty_state.md

 [3] Fallo de Conexión Recuperable
     -> Estructura: Icono AlertTriangle, mensaje descriptivo y botón de reintento 'Recargar Datos'.
     -> Código y CSS listos en: .sdd/components/empty_state/empty_state.md
====================================================================================================
```

---

## 8. Menú si el usuario dice: *"Quiero Botones de Acción en Tabla / Toolbar"*

> *"¿Cómo deben presentarse los botones de acción para la tabla?"*

```text
====================================================================================================
                       OPCIONES DE BOTONES DE ACCIÓN (TOOLBAR)
====================================================================================================
 [1] Caja Compacta de Iconos Agrupados (Estándar Oficial Jolifoods - Sin Texto)
     -> Estructura: Contenedor .cartera-compact-action-box con altura de 28px, bordes sutiles y divisores
        verticales de 1px. Botones de solo iconos con tooltip:
        - [+] Nuevo Registro (Abre Right Drawer)
        - [FileSpreadsheet Verde] Exportar a Excel
        - [RefreshCw] Recargar / Refrescar datos
     -> Código y CSS listos en: .sdd/components/button/icon_action_group.md

 [2] Acciones por Fila en Tabla (Grupo Compacto Unificado Obligatorio)
     -> Estructura: Contenedor unificado .cartera-row-actions-group de 26px con divisores de 1px (prohibido botones sueltos):
        - [Ojo] Ver / Editar detalle en Right Drawer (.cartera-sidebar-drawer)
        - [Divisor sutil 1px]
        - [Papelera Roja] ConfirmModal destructivo con justificación de 10+ caracteres
     -> Tipografía: Códigos y números con fuente monoespaciada neutra (PROHIBIDO texto verde en códigos).
     -> Código y CSS listos en: .sdd/components/button/icon_action_group.md (Variante 2) y .sdd/components/data_table/data_table.md
====================================================================================================
```

---

## 9. Menú si el usuario dice: *"Quiero Filtros Superiores / Barra de Filtros"*

> *"¿Cómo debe configurarse la barra de filtros superior?"*

```text
====================================================================================================
                       OPCIONES DE FILTROS SUPERIORES (.cartera-topbar)
====================================================================================================
 [1] Barra de Filtros Expandibles Segmentados (.cartera-btn-group)
     -> Estructura: Agrupador con triggers horizontales que despliegan selects en línea animados:
        - Filtro Zona / Área (con badge dinámico del valor activo)
        - Filtro Tipo de Documento / Estado
        - Filtro Unidad de Negocio
        - Filtro Mes (Selector calendario / numérico)
        - Filtro Año
        - Botón FilterX (Solo icono) para limpiar todos los filtros a valores por defecto
     -> Código y CSS listos en: .sdd/components/dropdown/expandable_filter_group.md
====================================================================================================
```

---

## 10. Menú si el usuario dice: *"Quiero Layout / Estructura de Pantalla"*

> *"¿Cuál estructura de layout debe aplicarse a la pantalla?"*

```text
====================================================================================================
                       OPCIONES DE LAYOUT Y NAVEGACIÓN
====================================================================================================
 [1] Layout Estándar Full-Width (Predeterminado Oficial - CERO Sidebar)
     -> Estructura: Pantalla de ancho completo optimizada para dashboards y tablas masivas.
     -> TopHeader:
        - Lado Izquierdo (.topheader-left): Logotipo Jolifoods SVG + separador sutil + TÍTULO DEL MÓDULO/PANTALLA
          (elimina encabezados gigantes innecesarios en el cuerpo).
        - Lado Derecho (.topheader-right): Conmutador Noche/Día, campana de notificaciones y badge de perfil.
     -> Cero Sidebar de navegación lateral (máximo aprovechamiento de pantalla).
     -> Código y CSS listos en: .sdd/components/layout/navbar.md

 [2] Layout con Sidebar de Navegación Lateral (Solo si el usuario lo solicita explícitamente)
     -> Estructura: Barra lateral izquierda para ecosistemas multi-módulo con colapso a 76px.
     -> Código y CSS listos en: .sdd/components/layout/sidebar.md
====================================================================================================
```
