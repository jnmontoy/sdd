# Carpeta Oficial de Prototipos No-Code (`mock/`) — Ecosistema Jolifoods SDD

Esta carpeta está destinada a albergar los prototipos visuales y especificaciones de datos generados para o por **personas no técnicas (líderes de área, analistas de negocio, coordinadores operativos)** antes de que el equipo de desarrollo escriba una sola línea de código en producción.

---

## 1. Filosofía del Modo No-Code

Cuando una persona indica **"No soy desarrollador"**, el sistema SDD activa automáticamente este entorno de prototipado rápido:

1. **Cero Comandos de Terminal**: No requiere Node.js, Python, Docker ni bases de datos instaladas.
2. **Visualización Inmediata con Doble Clic**: Los archivos `.html` se abren en cualquier navegador moderno (Chrome, Edge, Firefox).
3. **Estructura Basada en Datos Reales (JSON Arrays)**: Dado que el backend siempre entrega datos en formato JSON, los mocks en HTML cargan los datos desde un arreglo JavaScript (`const MOCK_DATA = [...]`) y los iteran dinámicamente (`forEach` / `map`). Esto garantiza que cuando el programador construya la aplicación real, la estructura de datos sea 100% idéntica.
4. **Documento Acompañante de Datos (`.md`)**: Cada prototipo HTML va acompañado de un archivo Markdown (ejemplo: `datos_dashboard_ventas.md`) que enumera los campos que el backend debe proveer en su JSON.
5. **CERO Pruebas Automáticas ni Testing**: En el **Modo Mock**, queda terminantemente **prohibido e innecesario ejecutar o requerir pruebas automáticas, Pytest, Playwright, suites E2E o validaciones con `validate_endpoints.py`**. Por su naturaleza, un mock es exclusivamente una simulación visual e interactiva sin backend real ni base de datos conectada.


---

## 2. Estructura Típica de la Carpeta `mock/`

```text
mock/
├── README.md                              <- Este documento explicativo
├── mock_template_with_json.html           <- Plantilla maestra interactiva con iteración JSON
├── plantilla_datos_necesarios.md          <- Plantilla de especificación de datos para el backend
│
├── dashboard_ventas/
│   ├── dashboard_ventas.html              <- Estructura HTML semántica limpia (enlaza CSS, JS y assets/Jolifoods.svg)
│   ├── dashboard_ventas.css               <- Estilos del módulo con variables oficiales y layout
│   ├── dashboard_ventas.js                <- Lógica interactiva (filtros Excel, drawer, paginador, tema)
│   ├── datos_dashboard_ventas.md          <- Especificación de campos JSON requeridos al backend
│   └── assets/                            <- Recursos gráficos e identidad corporativa local
│       ├── Jolifoods.svg                  <- Logotipo oficial Jolifoods en SVG
│       ├── Joli.svg                       <- Isotipo oficial Jolifoods en SVG
│       └── logoJoli.png                   <- Logotipo de respaldo en PNG
│
└── gestion_pedidos/
    ├── gestion_pedidos.html
    ├── gestion_pedidos.css
    ├── gestion_pedidos.js
    ├── datos_gestion_pedidos.md
    └── assets/
        ├── Jolifoods.svg
        ├── Joli.svg
        └── logoJoli.png
```

---

## 3. Rol del Integrador / Desarrollador al Recibir la Carpeta `mock/`

Cuando el usuario no técnico aprueba el diseño visual en su navegador y entrega la subcarpeta:
1. El programador abre el `.html` (que enlaza su `.css` y `.js`) para validar la interfaz visual aprobada.
2. Abre el `.md` para diseñar los esquemas Pydantic / Serializers de Django con los nombres exactos de campos.
3. Copia el arreglo `const MOCK_DATA` del archivo `.js` como fixture inicial de pruebas (seed data o mocks de frontend).
4. Reemplaza el renderizado manual de HTML por los componentes React existentes en `.sdd/components/` (como `<KpiCard />`, `<DataTableWrapper />`, `<ConfirmModal />`, `<RightDrawer />`).

---

## 4. Reglas de Oro Visuales para la Construcción de Todo Mock

Para garantizar que el prototipo refleje la identidad de los aplicativos reales de Jolifoods, debe construirse respetando obligatoriamente:

1. **Layout Full-Width por Defecto (Cero Sidebar a menos que se pida)**:
   - **Prohibido asumir la creación del Sidebar de navegación lateral por defecto**.
   - Toda aplicación o mock se diseña de ancho completo (Full-Width) gobernada por la Top Navbar. El Sidebar **solo se crea si el usuario lo solicita explícitamente**. (Ver [sidebar.md](../components/layout/sidebar.md)).
2. **Título Directo de la Página en el Lado Izquierdo del TopHeader (Cero Breadcrumbs de Navegación)**:
   - **Prohibido gastar espacio vertical en el cuerpo de la página colocando encabezados `<h1>` o banners de títulos**.
   - El logotipo oficial de Jolifoods y el **Título de la Página Actual** (`.topheader-title-box`) se ubican obligatoriamente en el **lado izquierdo de la Top Navbar**, contiguos al isotipo y separados por una barra sutil `/`, dejando el lado derecho para los controles de tema, multi-notificaciones y perfil.
   - **Prohibido usar breadcrumbs de navegación tipo migas de pan (`Jolifoods > Módulo > Página`) a menos que el usuario lo solicite expresamente**. En ese espacio va directamente el nombre de la pantalla actual.
   - **Prohibido aplicar textos verdes a títulos o rutas de navegación** (el verde es exclusivo de badges de estado positivo). (Ver [navbar.md](../components/layout/navbar.md)).
3. **Acciones Agrupadas en Toda la Pantalla (Sin Botones Sueltos)**:
   - **Toolbar de Tabla**: Botones agrupados en una caja compacta de 28px (`.compact-action-box`) con iconos `+`, `FileSpreadsheet` verde y `RefreshCw` (sin texto).
   - **Acciones por Fila de Tabla**: En la columna de acciones de cada fila, los botones de ver detalle y desactivar **deben estar agrupados en un contenedor segmentado de 26px** (`.row-actions-group`) con divisores de 1px. (Ver [icon_action_group.md](../components/button/icon_action_group.md)).
4. **Cero Textos Verdes o Azules Innecesarios en Tablas (Tipografía Neutra)**:
   - **Prohibido aplicar color verde o azul suelto a códigos de registros, identificadores o textos comunes**.
   - El color verde se reserva **exclusivamente para badges de estado positivo** (`OPTIMO`, `PAGADA`). Los códigos usan fuente `font-mono` neutra con `var(--text-primary)` o `var(--text-secondary)`.
5. **ConfirmModal Canónico Oficial con Justificación de Auditoría**:
   - Prohibido usar modales genéricos de Bootstrap o alertas nativas.
   - Las confirmaciones críticas usan la arquitectura oficial Jolifoods (`.joli-modal-overlay`, `.joli-confirm-modal-container`, `.joli-modal-icon-wrapper` con halo cromático).
   - **Campo de Justificación Obligatorio**:
     - Contenedor `.joli-modal-justification-box` con `width: 100%` y alineación a la izquierda.
     - Etiqueta `.joli-modal-justification-label` en mayúsculas discretas (`0.72rem`, `font-weight: 700`, `--text-secondary`), integrando el contador dinámico en tiempo real (`.joli-modal-justification-counter`: `0 / 10 mín.`, que pasa a verde `.is-valid` al alcanzar los caracteres mínimos).
     - Textarea corporativo `.joli-modal-textarea` con `width: 100%`, `box-sizing: border-box`, fondo `var(--input-bg)`, borde `var(--input-border)`, radio de 8px y halo de foco de acento (prohibido textarea nativo sin estilo ni ancho rígido).
     - **Botón Confirmar Condicionado**: El botón principal de confirmación permanece **deshabilitado (`disabled`)** hasta que el usuario digite al menos 10 caracteres válidos de justificación. (Ver [confirm_modal.md](../components/modal/confirm_modal.md)).
6. **Right Drawer Obligatorio para Formularios y Detalles**:
   - **Prohibido abrir formularios de captura o edición en modales flotantes centrados**.
   - Se deslizan siempre desde la derecha en un panel lateral (`.joli-drawer-container` de 560px) con mini-KPIs contextuales y scroll propio. (Ver [drawer.md](../components/drawer/drawer.md)).
7. **Filtros Superiores Expandibles Segmentados**:
   - Los filtros de cabecera se organizan en `.expandable-filter-group` con despliegue horizontal y botón `FilterX` de solo icono para limpiar. (Ver [expandable_filter_group.md](../components/dropdown/expandable_filter_group.md)).
8. **Centro de Multi-Notificaciones Desplegable en TopHeader (Estándar Tiendita / Vibra)**:
   - **Prohibido dejar el icono de la campana sin interactividad o con un `alert()` genérico**.
   - La campana debe contar con badge numérico (`.bell-badge-count`) y desplegar un popover flotante (`.notification-popover`) con **pestañas segmentadas para múltiples tipos de notificaciones** (ej. Solicitudes vs Alertas Críticas), badges por pestaña, lista con indicadores de severidad cromáticos, botones de acción en línea y estado óptimo de stock/tareas al día. (Ver [notification_popover.md](../components/notification/notification_popover.md)).
9. **Menú Desplegable de Perfil con Salida Segura (`UserProfileDropdown` - Estándar Vibra / Tiendita)**:
   - **Prohibido dejar el nombre o avatar del usuario como un badge plano sin acción**.
   - Al hacer clic sobre el colaborador en el TopHeader, se despliega el menú flotante con avatar, nombre, correo corporativo, badge de rol, enlace a *"Mi Perfil"* y botón de **"Cerrar Sesión"**.
   - Al pulsar *"Cerrar Sesión"*, **se debe abrir obligatoriamente el `ConfirmModal` canónico** solicitando confirmación explícita para evitar cierres de sesión involuntarios. (Ver [user_profile_dropdown.md](../components/layout/user_profile_dropdown.md)).
10. **Paginación Superior Integrada y Card Contenedora hasta Abajo (Estándar SDD)**:
    - **Prohibido ubicar el paginador debajo o al pie de la tabla**.
    - La paginación va integrada **ARRIBA DE LA TABLA**, dentro de la toolbar superior (`.table-header-toolbar.pagination-container`), unificando en una sola fila compacta:
      - **A la izquierda**: Selector de tamaño (`Mostrar [10 v] por página`), buscador reactivo, botón de limpieza de filtros activos, selector de visibilidad de columnas (`Columns3`), botones de acción (exportar, refrescar) y el resumen `Mostrando {start} a {end} de {total} registros`.
      - **A la derecha**: Controles de navegación (`ChevronsLeft`, `ChevronLeft`, botones numéricos con estado `.active` en verde/acento corporativo, `ChevronRight`, `ChevronsRight`).
    - **Card de Altura Completa (`.main-card-container`)**: La tarjeta contenedora de la tabla tiene `flex: 1; min-height: 420px; display: flex; flex-direction: column; overflow: hidden;` extendiéndose hasta el borde inferior de la pantalla visible dentro de un layout `height: 100vh; overflow: hidden;` (o `min-height: calc(100vh - 80px)`). La tabla interna (`.table-wrapper-full`) tiene `flex: 1; overflow: auto; min-height: 250px;`, sin dejar huecos vacíos desaprovechados.
    - **Dataset Suficiente**: Mínimo 20 a 30 registros iniciales para verificar la funcionalidad real del paginador. (Ver [pagination.md](../components/pagination/pagination.md)).
11. **Filtros de Columna Tipo Excel Funcionales (`ChecklistPopover` - Estándar SDD)**:
    - **Prohibido dejar los encabezados de tabla sin capacidad de filtrado contextual**.
    - Cada encabezado `<th>` filtrable incluye un botón de filtro (`.filter-toggle-btn`).
    - Al hacer clic, se despliega el popover tipo Excel (`.excel-popover`) con ordenamiento A-Z / Z-A, buscador reactivo, casillas con frecuencias `(N)`, selección/deselección masiva y botones Limpiar y Aplicar.
    - Al aplicar, la tabla filtra inmediatamente el dataset y recalcula la paginación.
    - Cuando una columna tiene filtros activos, se resalta con halo cromático y un punto indicador verde (`.filter-active-dot`), y en la toolbar aparece el botón de reseteo rápido (`FilterX: Filtros (N)`). (Ver [checklist_popover.md](../components/data_table/checklist_popover.md)).
12. **Columnas Ajustables / Redimensionables (`ColumnResizer`) y Selector de Visibilidad (`Columns3`)**:
    - **Prohibido generar tablas con anchos rígidos o desbordamientos descontrolados**.
    - Cada encabezado `<th>` debe incorporar en su borde derecho el manipulador de 6px (`.resizable-th-resizer`) con cursor `col-resize` para arrastre fluido en tiempo real (mínimo 60px) y restablecimiento de ancho predeterminado mediante doble clic. (Ver [column_resizer.md](../components/data_table/column_resizer.md)).
    - La toolbar debe incluir el selector de visibilidad de columnas (`.col-visibility-wrapper`) con icono `Columns3`, badge de conteo `{visibles}/{totales}` y popover interactivo para ocultar o mostrar columnas garantizando al menos una visible. (Ver [column_visibility.md](../components/data_table/column_visibility.md)).
13. **Conformidad Absoluta de Variables CSS y Tematización Día/Noche (`variables.css`)**:
    - **Prohibido inventar nombres de variables ad-hoc** o hardcodear colores directos (ej. `#ffffff`, `#16162a`, o `rgba(...)` fijos) para fondos, textos o bordes que queden estáticos al cambiar de tema.
    - Toda vista, componente o mock debe vincularse estrictamente a la taxonomía canónica de [variables.css](../components/variables.css).
    - **Conmutación Universal Reactiva**: La alternancia de tema debe actualizar obligatoria y sincrónicamente ambos selectores en la etiqueta `<html>`: `data-theme` y `data-bs-theme`, junto con `style.colorScheme = 'light' | 'dark'`.
    - **Cero Textos Blancos Invisibles en Modo Día**: En Modo Día, ningún estado interactivo (`.active`, hover de tabs, switcher o paginador) puede forzar textos en blanco (`#ffffff`) sobre fondos claros; deben consumir siempre `var(--text-primary)`. (Ver [variables.md](../components/variables.md)).
14. **Estilo Corporativo en Controles de Formulario e Inputs (Modales y Drawers)**:
    - **Prohibido dejar inputs o formularios con estilos nativos por defecto del navegador**.
    - Todo formulario (creación, edición o filtros) debe implementar la estructura canónica:
      - Contenedor `.form-field` / `.drawer-form-field` con espaciado uniforme.
      - Etiqueta `.form-label` / `.drawer-field-label` en mayúsculas discretas (`0.72rem`, `font-weight: 700`, `color: var(--text-secondary)`).
      - Control `.input-control` / `.drawer-input-control` (`background: var(--input-bg)`, `border: 1px solid var(--input-border)`, altura mínima 38px, radio 8px, y halo de foco de acento).
      - Input `.form-control` / `.drawer-field-input` con texto en `var(--text-primary)` y placeholder en `var(--text-muted)`.
      - **Texto Contextual en Botón de Guardado**: El botón principal del footer debe reflejar la entidad (ej. *"Guardar Registro"*, *"Guardar Partido"*), prohibiendo textos genéricos o desfasados como *"Guardar Notas"*.
15. **Arquitectura Modular de 4 Archivos por Módulo (Cero HTML Monolítico)**:
    - **Prohibido generar un archivo `.html` único gigante que concentre estilos y scripts en línea**.
    - Todo paquete generado en `mock/<nombre_modulo>/` debe organizarse obligatoriamente en 4 archivos independientes:
      1. `[modulo].html`: Estructura markup semántica limpia, enlazando su archivo CSS y su archivo JS.
      2. `[modulo].css`: Hoja de estilos con variables oficiales, clases de layout, card de altura completa, toolbar y drawer.
      3. `[modulo].js`: Lógica interactiva desacoplada (dataset `MOCK_DATA`, filtros Excel, paginador superior, drawer y theme switcher).
      4. `datos_[modulo].md`: Contrato de datos JSON con esquemas, tipos y parámetros para el backend. (Ver [variables.md](../components/variables.md)).
16. **Paquete Autónomo con Inclusión Obligatoria de Assets Locales (`assets/`)**:
    - **Prohibido dejar el TopHeader sin el logo corporativo oficial o enlazando rutas absolutas o remotas no portables**.
    - Toda carpeta de módulo en `mock/<nombre_modulo>/` debe incorporar obligatoriamente su subcarpeta local `assets/` conteniendo copias directas de los activos corporativos Jolifoods (`Jolifoods.svg`, `Joli.svg`, `logoJoli.png`) tomados desde `.sdd/assets/`.
    - **Enlace Relativo Estricto**:
      - Favicon: `<link rel="icon" type="image/svg+xml" href="./assets/Jolifoods.svg">`.
      - TopHeader: `<img src="./assets/Jolifoods.svg" alt="Jolifoods" class="topheader-logo" onerror="this.onerror=null; this.src='./assets/logoJoli.png';">`.
    - **Portabilidad Offline Total**: Esta estructura asegura que al compartir o mover la carpeta del mock a cualquier equipo, el prototipo visual conserve íntegra la identidad de marca Jolifoods sin iconos de imagen rota. (Ver [logo.md](../components/login/logo.md) y [navbar.md](../components/layout/navbar.md)).




