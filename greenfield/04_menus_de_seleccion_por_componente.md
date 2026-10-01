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

 [2] Modal de Diálogo Especial (ModalDialog - Solo si se pide específicamente)
     -> NOTA: Toda creación/edición CRUD se hace en Right Drawer. Los modales son solo para confirmación, firmas o diálogos puntuales.
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

## 4. Menú si el usuario dice: *"Quiero un Panel Lateral / Drawer / Crear o Editar Registro"*

> *"¿Cuál variante de panel deslizante lateral (Drawer) deseas utilizar para tu CRUD o detalle?"*

```text
====================================================================================================
              OPCIONES DE PANELES LATERALES (DRAWER / SLIDE-OVER) — OBLIGATORIO CRUD
====================================================================================================
 [!] REGLA DE ORO DE EXPERIENCIA DE USUARIO:
     -> Toda creación (+ Nuevo) o edición (Editar) de cualquier CRUD debe realizarse desde el Right Drawer.
     -> Queda prohibido generar modales o redirigir a páginas separadas salvo solicitud específica del usuario.

 [1] Drawer de Formulario y Edición CRUD (Estándar Oficial - Size: 'md' - 560px)
     -> Estructura: Deslizamiento lateral derecho (.cartera-sidebar-drawer), backdrop blur,
        cuerpo scrollable para inputs, y pie fijo con botones 'Guardar' y 'Cancelar'.
     -> Código y CSS listos en: .sdd/components/drawer/drawer.md (Variante 2)

 [2] Drawer de Inspección Rápida de Detalle (Size: 'sm' - 400px)
     -> Estructura: Visor de solo lectura con metadatos clave, badges y mini-kpis de la fila seleccionada.
     -> Código y CSS listos en: .sdd/components/drawer/drawer.md (Variante 1)

 [3] Drawer Extenso con Pestañas Multi-Sección (Size: 'lg' - 840px)
     -> Estructura: Panel ancho con sistema de pestañas internas para formularios densos,
        historial de auditoría, bitácora y documentos adjuntos.
     -> Código y CSS listos en: .sdd/components/drawer/drawer.md (Variante 3)
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

 [2] Toast Flotante Autocerrable con Sonner (ToastNotification)
     -> Estructura: Alerta no intrusiva impulsada por Sonner con auto-cierre inteligente diferenciado
        (success: 3.5s, info: 4s, warning: 5s, error: 7s/persistente), icono contextual de Lucide,
        diseño responsive y colores institucionales Jolifoods.
     -> Código y CSS listos en: .sdd/components/toast/toast_notification.md

 [3] Toast Sonner con Botón de Acción / Deshacer (Undo / Retry)
     -> Estructura: Notificación Sonner con botón de acción interactivo para deshacer una acción
        reversible (ej. eliminar registro) o reintentar una petición fallida.
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

 [2] Acciones por Fila en Tabla (Agrupación Obligatoria con Bootstrap btn-group)
     -> Estructura: Contenedor Bootstrap `<div class="btn-group btn-group-sm cartera-row-actions-group" role="group">`:
        - [Ojo] Ver / Editar detalle en Right Drawer (.cartera-sidebar-drawer)
        - [Llave] Restablecer clave o acción secundaria
        - [Papelera Roja] ConfirmModal destructivo con justificación de 10+ caracteres
     -> REGLA: Si hay más de un botón en opciones, NUNCA deben estar sueltos ni separados por márgenes;
        deben agruparse con `btn-group btn-group-sm` para unificar bordes redondeados y divisores limpios.
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
                       OPCIONES DE LAYOUT Y NAVEGACIÓN (100% HORIZONTAL)
====================================================================================================
 [!] REGLA DE ORO DE MAQUETACIÓN: PROHIBIDO CENTRAR EL FRONTEND
     -> NINGÚN desarrollo debe estar centrado ni encogido en medio de la pantalla (prohibido max-w-xl mx-auto).
     -> TODO debe expandirse a lo largo de la pantalla en horizontal (100% width) de extremo a extremo.
     -> Normativa completa en: .sdd/components/layout/layout_rules.md

 [1] Layout Estándar Full-Width Horizontal (Predeterminado Oficial - CERO Sidebar)
     -> Estructura: Pantalla de ancho completo (100% width) optimizada para dashboards y tablas masivas.
     -> TopHeader:
        - Lado Izquierdo (.topheader-left): Logotipo Jolifoods SVG + separador sutil + TÍTULO DEL MÓDULO/PANTALLA
          (elimina encabezados gigantes innecesarios en el cuerpo).
        - Lado Derecho (.topheader-right): Conmutador Noche/Día, campana de notificaciones y badge de perfil.
     -> Cero Sidebar de navegación lateral (máximo aprovechamiento de pantalla).
     -> Código y CSS listos en: .sdd/components/layout/navbar.md y .sdd/components/layout/layout_rules.md

 [2] Layout con Sidebar de Navegación Lateral (Solo si el usuario lo solicita explícitamente)
     -> Estructura: Barra lateral izquierda para ecosistemas multi-módulo con colapso a 76px.
        El área de trabajo principal continúa siendo 100% horizontal ocupando todo el ancho restante.
     -> Código y CSS listos en: .sdd/components/layout/sidebar.md
====================================================================================================
```

---

## 11. Menú si el usuario dice: *"Quiero Gráficas / Charts / Analítica Visual"*

> *"¿Cuál variante de gráfica necesitas para tu dashboard o reporte?"*

```text
====================================================================================================
                        OPCIONES DE GRÁFICAS Y ANALÍTICA VISUAL
====================================================================================================
 [1] Gráfica de Área con Gradiente Suave (AreaGradientChart)
     -> Estructura: Curva Bézier continua con relleno vertical semitransparente degradado,
        ejes interactivos, rejilla tenue punteada y crosshair vertical con tooltip card.
     -> Ideal para: Tendencias temporales de ventas, cobros, ingresos o tickets a lo largo de días/meses.
     -> Código y CSS listos en: .sdd/components/charts/analytics_charts.md (Variante 1)

 [2] Gráfica de Barras Verticales Redondeadas (RoundedBarChart)
     -> Estructura: Columnas con radio superior suave (rx=6), colores de tokens Jolifoods,
        iluminación en hover y tooltips con formato de moneda o unidades.
     -> Ideal para: Comparativas por sede, tipo de novedad, categoría de producto o vendedor.
     -> Código y CSS listos en: .sdd/components/charts/analytics_charts.md (Variante 2)

 [3] Gráfica Donut / Anillo de Distribución (DonutDistributionChart)
     -> Estructura: Anillo SVG con grosor balanceado, métrica totalizadora en el centro,
        leyenda interactiva con porcentajes y bullets cromáticos.
     -> Ideal para: Estado de cartera (Corriente, 30d, 60d, 90d+), distribución de roles o tipos de tickets.
     -> Código y CSS listos en: .sdd/components/charts/analytics_charts.md (Variante 3)

 [4] Micro-Sparklines de Tendencia para Tarjetas KPI (MiniSparkline)
     -> Estructura: Curva ultra-compacta (90x28px) sin ejes ni textos, renderizada directamente
        dentro de la esquina de una tarjeta KPI o fila de tabla para visualizar la tendencia sin recargar.
     -> Código y CSS listos en: .sdd/components/charts/analytics_charts.md (Variante 4)
====================================================================================================
```

---

## 12. Menú si el usuario dice: *"Quiero Biometría / Escáner Facial / Captura de Rostro"*

> *"¿Cuál modalidad de captura o verificación biométrica necesitas?"*

```text
====================================================================================================
               OPCIONES DE CAPTURA BIOMÉTRICA FACIAL (FACIAL SCANNER)
====================================================================================================
 [1] Kiosco o Terminal con Guía Oval y Cortinilla SVG (Estándar Contenedores / Porterías)
     -> Estructura: Visor de cámara WebRTC en vivo con overlay SVG transparente recortado en óvalo,
        indicadores visuales de estado (Centrar Rostro, Distancia Correcta, Iluminación Óptima),
        animación de barrido de haz láser verde y disparador automático o por botón.
     -> Código y CSS listos en: .sdd/components/biometrics/facial_scanner.md (Variante 1)

 [2] Captura Portátil con Selección de Cámara Frontal / Trasera (Móvil / PWA)
     -> Estructura: Selector dinámico de `facingMode` (user / environment), control táctil de zoom
        digital (1x, 1.5x, 2x) y confirmación de captura con recorte estricto del rostro en Base64/Blob.
     -> Código y CSS listos en: .sdd/components/biometrics/facial_scanner.md (Variante 2)
====================================================================================================
```

---

## 13. Menú si el usuario dice: *"Quiero Capturar Firma Digital / Firma en Pantalla"*

> *"¿Cuál modalidad de firma digital necesitas implementar?"*

```text
====================================================================================================
                   OPCIONES DE CAPTURA DE FIRMA DIGITAL (SIGNATURE)
====================================================================================================
 [1] Modal con Lienzo Táctil y Auto-Recorte Inteligente (cropToSignature)
     -> Estructura: Diálogo con canvas responsive, soporte de stylus/dedo/ratón, botón Limpiar trazo,
        y algoritmo que recorta automáticamente el bounding box exacto de la firma a PNG transparente.
     -> Código y CSS listos en: .sdd/components/signature/signature_modal.md (Variante 1)

 [2] Campo de Firma en Línea Incrustado en Formulario o Right Drawer
     -> Estructura: Bloque canvas integrado directamente dentro del formulario con trazo en tiempo real,
        línea base de firma y previsualización inmediata.
     -> Código y CSS listos en: .sdd/components/signature/signature_modal.md (Variante 2)
====================================================================================================
```

---

## 14. Menú si el usuario dice: *"Quiero Lector / Escáner de Código de Barras o QR"*

> *"¿Cómo debe operar el escaneo de códigos de barra / QR?"*

```text
====================================================================================================
                 OPCIONES DE ESCÁNER DE CÓDIGO DE BARRAS Y QR
====================================================================================================
 [1] Modal Emergente de Escaneo Rápido con Auto-Cierre
     -> Estructura: Ventana modal con visor de cámara WebRTC y librería html5-qrcode. Cierra
        automáticamente al detectar el primer código válido e inyecta el valor en el input.
     -> Código y CSS listos en: .sdd/components/scanner/scanner_modal.md (Variante 1)

 [2] Modo Inventario Continuo por Lotes (Múltiples Lecturas)
     -> Estructura: Escáner continuo con feedback sonoro (beep) y lista acumulada de lecturas
        sin cerrar la cámara entre lecturas sucesivas.
     -> Código y CSS listos en: .sdd/components/scanner/scanner_modal.md (Variante 2)
====================================================================================================
```

---

## 15. Menú si el usuario dice: *"Quiero Visualizar / Previsualizar Documentos PDF"*

> *"¿Qué tipo de experiencia de visor de PDF requieres?"*

```text
====================================================================================================
                 OPCIONES DE VISOR DE DOCUMENTOS PDF (CANVAS)
====================================================================================================
 [1] Visor de Hojas Físicas Apiladas con Zoom Escalonado (PdfPreviewFrame)
     -> Estructura: Renderizado en Canvas mediante pdfjs-dist con sombras realistas de papel,
        barra de herramientas superior (Página X de Y, Zoom -, Zoom +, Ajustar ancho) y descarga.
     -> Código y CSS listos en: .sdd/components/pdf/pdf_preview_frame.md (Variante 1)

 [2] Previsualizador Compacto Incrustado en Right Drawer
     -> Estructura: Panel lateral deslizante con visor responsivo optimizado para inspección rápida
        de facturas electrónicas o soportes de pago vinculados a una fila de tabla.
     -> Código y CSS listos en: .sdd/components/pdf/pdf_preview_frame.md (Variante 2)
====================================================================================================
```

---

## 16. Menú si el usuario dice: *"Quiero Calendario de Turnos / Novedades / Programación"*

> *"¿Cómo debe estructurarse la visualización del calendario corporativo?"*

```text
====================================================================================================
               OPCIONES DE CALENDARIO CORPORATIVO (CALENDAR)
====================================================================================================
 [1] Malla Mensual Interactiva con Badges Cromáticos y Filtros (CorporateCalendar)
     -> Estructura: Cuadrícula de 7 columnas (Lunes a Domingo), selector de mes/año, badges
        de novedad de colores (Turno, Vacaciones, Incapacidad, Permiso) y contador por día.
     -> Código y CSS listos en: .sdd/components/calendar/corporate_calendar.md (Variante 1)

 [2] Vista Semanal Detallada con Asignación por Franjas Horarias
     -> Estructura: Desglose por horas y cuadrillas con interacción para agregar novedades.
     -> Código y CSS listos en: .sdd/components/calendar/corporate_calendar.md (Variante 2)
====================================================================================================
```

---

## 17. Menú si el usuario dice: *"Quiero Centro de Alertas / Multi-Notificaciones"*

> *"¿Cómo deben desplegarse las notificaciones en el TopHeader?"*

```text
====================================================================================================
                 OPCIONES DE CENTRO DE NOTIFICACIONES (POPOVER)
====================================================================================================
 [1] Popover Segmentado con Pestañas Multi-Categoría (NotificationPopover)
     -> Estructura: Campana en TopHeader con badge numérico, despliegue flotante con tabs
        (Todas, Alertas Operativas, Seguridad), opción 'Marcar todo leído' y enlace a detalle.
     -> Código y CSS listos en: .sdd/components/notification/notification_popover.md
====================================================================================================
```

---

## 18. Menú si el usuario dice: *"Quiero Banner de Instalación PWA / Modo Kiosco"*

> *"¿Cómo debe manejarse la instalación en dispositivos móviles o kioscos?"*

```text
====================================================================================================
                   OPCIONES DE INSTALACIÓN PWA (MOBILE / KIOSK)
====================================================================================================
 [1] Banner Flotante Inferior No Intrusivo (PwaInstallBanner)
     -> Estructura: Barra horizontal en el pie con isotipo Jolifoods, texto explicativo,
        botón 'Instalar Aplicación' y botón cerrar con persistencia en localStorage.
     -> Código y CSS listos en: .sdd/components/pwa/pwa_install_banner.md
====================================================================================================
```

---

## 19. Menú si el usuario dice: *"Quiero Cargador / Loader / Skeleton de Carga"*

> *"¿Qué tipo de indicador visual de espera necesitas?"*

```text
====================================================================================================
                OPCIONES DE CARGADORES Y SKELETONS (LOADERS)
====================================================================================================
 [1] Shimmer de Carga Tabular (TableSkeleton)
     -> Estructura: Filas fantasma con animación de brillo suave (shimmer) que respetan exactamente
        las columnas de la tabla evitando saltos de diseño (cero Cumulative Layout Shift).
     -> Código y CSS listos en: .sdd/components/loader/page_loader.md (Variante 1)

 [2] Cargador de Transición de Pantalla Completa (PageLoader)
     -> Estructura: Isotipo oficial Jolifoods con animación de pulso y spinner perimetral esmeralda.
     -> Código y CSS listos en: .sdd/components/loader/page_loader.md (Variante 2)
====================================================================================================
```

---

## 20. Menú si el usuario dice: *"Quiero Toggle / Interruptor / Activar Usuario"*

> *"¿Cómo debe configurarse el conmutador o interruptor de estado?"*

```text
====================================================================================================
                 OPCIONES DE INTERRUPTOR CONMUTADOR (TOGGLE SWITCH)
====================================================================================================
 [1] Toggle Compacto para Fila de Tabla (DataTable Status Switch)
     -> Estructura: Conmutador miniatura de 32x18px (`.joli-toggle-sm`) con halo esmeralda,
        badge de estado ('Activo' / 'Inactivo') y ConfirmModal condicionado solo a desactivaciones.
     -> Código y CSS listos en: .sdd/components/toggle/toggle_switch.md (Variante sm)

 [2] Toggle Estándar para Formulario o Right Drawer (Form Switch con Descripción)
     -> Estructura: Conmutador de 42x24px (`.joli-toggle-md`) en caja destacada con título de directiva,
        subtítulo descriptivo y cambio de estado inmediato con feedback visual.
     -> Código y CSS listos en: .sdd/components/toggle/toggle_switch.md (Variante md)
====================================================================================================
```




