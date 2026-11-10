# Patrón: Pantalla de Tabla Administrativa (`UI-PATTERN-ADMIN-TABLE`)
## Ubicación SDD: `sdd/components/data_table/admin_table_screen.md`

Cómo se arma una **pantalla de listado del panel administrativo** (usuarios, clientes, rutas, versiones, logs): una tarjeta con barra de herramientas, tabla o tarjetas, y paginación. Es el patrón por defecto de los módulos del panel.

**Referencia:** módulo Usuarios de Pandora (`frontend-admin/src/components/users/`): `UsersManagement.tsx` (contenedor), `UsersToolbar.tsx`, `UsersTabla.tsx`, `UsersCards.tsx`, `UsuariosVacio.tsx`, `useVistaUsuarios.ts` (estado de la vista), `usuariosConfig.ts` (columnas y claves). Las demás pantallas (Clientes, Historial de rutas, Control de versiones, Logs) siguen la misma división de archivos.

> **¿Cuándo usar este patrón y cuándo [`data_table.md`](./data_table.md)?**
> - **Este patrón (datos en el navegador):** el listado completo cabe en memoria (hasta unos pocos miles de filas). Se trae todo, se filtra, ordena y pagina en el navegador, y se refresca con sondeo. Es el caso de usuarios, roles, versiones, rutas del día.
> - **`DataTable` con paginación en servidor:** catálogos grandes o que crecen sin límite (facturas, movimientos, logs históricos). Búsqueda con espera, filtros y conteos calculados por el backend.

> **Convención de este documento:** «DEBE» marca lo que define el patrón. Las piezas repetidas de la barra y del encabezado de la tabla ya existen como **componentes compartidos** (§11): una pantalla nueva DEBE usarlos en vez de copiar el marcado.

---

## 1. Composición de la pantalla

```tsx
<div className="users-page-container">                       {/* flex columna, gap 1rem, flex:1, min-height:0 */}
  {isLoading && <PageLoader variant="curtain" message={...} subMessage={...} />}
  <section className="joli-table-card" aria-busy={isLoading}>
    <UsersToolbar {...} />                                    {/* §2 */}
    <div className="joli-table-wrapper">
      {isLoading && !usuarios.length
        ? <TableSkeleton rows={8} columns={columnasVisibles.length || 7} />
        : vista === 'table'
          ? <UsersTabla {...} />                              {/* §4 */}
          : filtrados.length ? <UsersCards {...} /> : <UsuariosVacio {...} />}
    </div>
    <footer className="joli-table-footer" aria-label="Paginación de usuarios">
      <Pagination ... pageSizeOptions={[10, 20, 50, 100]} itemLabel="Colaboradores" />   {/* §3 */}
    </footer>
  </section>
  {/* Fuera de la tarjeta: drawers y modales */}
  <UserFormDrawer ... /> <ConfirmModal ... /> {puedeDefinirRoles && <RolePermissionsDrawer ... />}
</div>
```

- **Sin encabezado de página ni fila de KPIs dentro del módulo:** el título vive en la barra superior del layout. Los KPIs de [`kpi_cards.md`](../kpi/kpi_cards.md) son opcionales y van encima de la tarjeta solo si el módulo los necesita.
- El contenedor recibe por props lo que depende de la sesión: el usuario actual (p. ej. `currentUserDocumento`, para impedir acciones sobre la propia cuenta), los permisos de sección (`puedeDefinirRoles`, BP-19) y un callback para el contador del menú lateral (`onUsersCountChange(total)`, en cada carga y sondeo).

```css
.joli-table-card    { flex: 1; min-height: 420px; display: flex; flex-direction: column; overflow: hidden;
                      border-radius: var(--radius-xl); box-shadow: var(--shadow-card); }
.joli-table-toolbar { display: flex; flex-wrap: wrap; justify-content: space-between; gap: .75rem; padding: .875rem 1.25rem; }
.joli-table-wrapper { flex: 1; min-height: 250px; overflow: auto; }
.joli-table-footer  { padding: .75rem 1.25rem; min-height: 52px; }
.joli-table-footer .joli-toolbar-pagination { width: 100%; justify-content: space-between; }
```

---

## 2. Barra de herramientas

`div.joli-table-toolbar.pagination-container` con dos zonas, en este orden exacto:

| Zona | Elementos (en orden) |
| :--- | :--- |
| **Izquierda** `div.toolbar-left` (con `ref` para cerrar al hacer clic fuera) | 1. Botonera de los tres (vista tabla, vista tarjetas, buscar) · 2. Filtros expandibles · 3. Visibilidad de columnas (solo escritorio y vista tabla) · 4. Exportar · 5. Limpiar todo |
| **Derecha** `div.toolbar-right` | 1. Paginación solo botones · 2. Caja compacta de acciones · 3. Botones con texto del módulo (p. ej. «Definición de roles», según permiso) |

### 2.1. Botonera de los tres (vista y búsqueda)
```tsx
<div className="view-switcher" role="group" aria-label="Vista y búsqueda rápida">
  {!isMobile && (
    <button type="button" className={`switcher-btn ${vista === 'table' ? 'is-active' : ''}`}
            aria-pressed={vista === 'table'} aria-label="Vista en tabla" title="Vista en tabla">
      <Table2 size={15} />
    </button>
  )}
  <button type="button" className={`switcher-btn ${vista === 'cards' ? 'is-active' : ''}`}
          aria-pressed={vista === 'cards'} aria-label="Vista en tarjetas" title="Vista en tarjetas">
    <LayoutGrid size={15} />
  </button>
  <span className="switcher-divider" aria-hidden="true" />
  <div className={`switcher-search-item ${abierto ? 'is-open' : ''} ${q ? 'has-active-val' : ''}`}>
    <button type="button" className="switcher-btn switcher-search-btn" aria-expanded={abierto}
            aria-controls="busqueda-usuarios" aria-label="Buscar por cédula, nombre, correo, cargo, área o zona"
            title="Buscar por cédula, nombre, correo, cargo, área o zona">
      <Search size={15} />
      {q && !abierto && <span className="switcher-search-dot" />}
    </button>
    <div className="switcher-search-expanded" id="busqueda-usuarios">
      <input type="search" className="switcher-search-input" aria-label="Buscar usuarios"
             placeholder="Buscar por cédula, nombre, correo, cargo, área o zona..." value={q} onChange={...} />
      <button type="button" className="filter-expanded-close" aria-label="Limpiar búsqueda"><X size={14} /></button>
    </div>
  </div>
</div>
```
- **Comportamiento:** el campo se enfoca 60 ms después de abrir; `Escape` cierra sin borrar; un clic fuera de `.toolbar-left` cierra solo si está vacío; la X borra, vuelve a página 1 y cierra; al escribir se vuelve a página 1. Con texto y cerrado, un punto (`.switcher-search-dot`, 6 px, `--brand-solid`) avisa que hay búsqueda activa.
- **Búsqueda en el navegador, sin espera:** `includes` sin distinguir mayúsculas sobre los campos declarados (en Usuarios: documento, nombre, correo, cargo, área y zona).
- **CSS:** `.view-switcher` 38 px de alto, `padding: 3px`, `gap: 2px`, `radius-md`, `bg-input`; `.switcher-btn` 32 px de ancho; activo con `rgba(var(--brand-primary-rgb), .16)` y `--brand-primary` (tema claro: fondo blanco). Divisor 18 px. La búsqueda se expande hasta `--busqueda-ancho-max` (340 px) en 0.34 s (`cubic-bezier(.16, 1, .3, 1)`, opacidad y `scaleX(.85 → 1)`); input flexible de 28 px de alto. **Nunca empuja los demás elementos a otra línea:** el campo desplegado lleva `contain: inline-size` y `flex: 1 1 0` (no aporta ancho propio al cálculo de salto de línea), sin padding propio (los márgenes van en el input y la X), y la botonera abierta (`.is-searching`) crece con `flex-grow` solo hasta el espacio libre de su línea, con tope = controles cerrados + campo (`.sin-tabla` en móvil, `.sin-vistas` solo buscador). `.toolbar-left` lleva `flex: 1 1 auto; min-width: 0` para ceder ese espacio. En móvil: 36 px de alto.

### 2.2. Filtros expandibles
Cada filtro de la cabecera (en Usuarios: Rol y Estado) es un ítem de [`expandable_filter_group.md`](../dropdown/expandable_filter_group.md):

```tsx
<div className="expandable-filter-group" role="group" aria-label="Filtros">
  <div className={`expandable-filter-item ${abierto ? 'is-open' : ''} ${valor ? 'has-active-val' : ''}`}>
    <button type="button" className="filter-trigger-btn" aria-expanded={abierto} aria-controls="filtro-rol" title="Filtrar por rol">
      <Shield size={15} className="trigger-icon" />
      <span className="trigger-text">Rol</span>
      {valor && !abierto && <span className="trigger-badge">{nombreDelRol}</span>}
      <ChevronDown size={13} className="trigger-arrow" />
    </button>
    <div className="filter-expanded-content" id="filtro-rol">
      <select className="filter-expanded-select" aria-label="Rol" value={valor} onChange={...}>
        <option value="">Todos los roles</option>
        {/* ... */}
      </select>
      <button type="button" className="filter-expanded-close" title="Contraer filtro de rol"><X size={14} /></button>
    </div>
  </div>
</div>
```
- Al elegir: aplica, vuelve a página 1 y **cierra** el filtro. Un solo filtro abierto a la vez; se cierra con clic fuera y con `Escape` (devuelve el foco al disparador).
- **CSS:** disparador de 38 px, `padding: 0 .875rem`, `font-size: var(--font-size-xs)`; abierto con `rgba(brand, .1)`, con valor `rgba(brand, .06)`; la flecha rota **−90°** al abrir; expansión `max-width: 420px` con `border-left: 1px dashed`; select mínimo 165 × 28.
- Se ocultan en ≤768 px.

### 2.3. Limpiar todo
```tsx
<div className="filter-actions-group">
  <div className={`filter-action-clear-wrapper ${hayFiltros ? 'is-visible' : ''}`}>
    <button type="button" className="filter-action-btn filter-clear-btn" onClick={limpiarTodo}
            aria-label="Limpiar búsqueda, ordenamiento y filtros" title="Limpiar búsqueda, ordenamiento y filtros aplicados">
      <FilterX size={16} />
    </button>
  </div>
</div>
```
- `hayFiltros` cuenta búsqueda, filtros de cabecera, filtros de columna **y orden**. Limpiar reinicia todo, vuelve a página 1 y cierra filtros y buscador.
- CSS: 38 × 38, `radius-md`; hover rojo (`color-mix` 12 %, borde 35 %); el contenedor aparece animando hasta `max-width: 44px`.

### 2.4. Visibilidad de columnas
`ColumnVisibilityDropdown` ([`column_visibility.md`](./column_visibility.md)) con `columns={[{key, label}]}`, `onResetDefault` (todas visibles) y la clave de almacenamiento del módulo. Mínimo una columna visible. Al leer de almacenamiento se descartan claves de columnas que ya no existen. Botón de 38 px; menú de 230 px abierto hacia la derecha (`left: 0`). Solo en escritorio y vista tabla.

### 2.5. Exportar
- Botón con texto `button.btn.btn--secondary` (36 px de alto), `FileSpreadsheet` 15 px en color de éxito, texto «Exportar», **fuera** de la caja compacta. Deshabilitado mientras carga o sin resultados.
- Exporta **todas las filas filtradas** (todas las páginas, con filtros de cabecera y de columna), con columnas propias de exportación que **no dependen** de las visibles.
- Avisos: sin filas → advertencia «Sin datos para exportar»; éxito → «Archivo Excel generado» con «Se exportaron N usuarios.» (número en es-CO); error → «No fue posible generar el archivo Excel».
- Formato y seguridad: ver [`excel_export.md`](../export/excel_export.md) §0 (XML Spreadsheet `.xls` generado en el navegador, sin dependencias, con encabezado con estilo y neutralización de fórmulas).

### 2.6. Paginación solo botones (arriba)
`<Pagination currentPage totalItems pageSize onPageChange disabled={isLoading} buttonsOnly />` — ver §3.

### 2.7. Caja compacta de acciones
```tsx
<div className="compact-action-box" role="toolbar" aria-label="Acciones de colaboradores">
  <button type="button" className="btn-icon-compact btn-icon-add" title="Nuevo usuario" aria-label="Nuevo usuario"><UserPlus size={15} /></button>
  <button type="button" className="btn-icon-compact btn-icon-agreement" title="Contrato de uso" aria-label="Contrato de uso"><FileText size={15} /></button>
  <span className="compact-divider" aria-hidden="true" />
  <button type="button" className="btn-icon-compact btn-icon-refresh" title="Recargar datos" aria-label="Recargar datos"
          aria-busy={isLoading} disabled={isLoading}>
    <RotateCcw size={14} className={isLoading ? 'spin-antihorario' : ''} />
  </button>
</div>
```
- Orden: crear → acciones del módulo → divisor → recargar al final.
- CSS: caja de 36 px (32 en móvil), `radius-md`, `bg-input`; botones de 36 px (32 en móvil); `.btn-icon-add` en `--brand-primary`; las demás en `--text-secondary` con hover de marca; divisor de 18 px.
- `RotateCcw` gira con `spin-antihorario` (no `spin`); ver [`bug_lessons.md`](../../memory/learnings/bug_lessons.md).
- Acciones de un **permiso aparte** (p. ej. «Definición de roles») van como botón con texto `btn btn--secondary` de 36 px a la derecha de la caja, solo si el usuario tiene el permiso.
- Acciones que traen datos de **otro sistema** (p. ej. «Actualizar usuarios» desde Vibra) no van en la barra: se abren desde el menú lateral con un `ConfirmModal` con barra de progreso ([`confirm_modal.md`](../modal/confirm_modal.md) §props de carga).

---

## 3. Paginación (dos instancias)

| Ubicación | Uso | Contenido |
| :--- | :--- | :--- |
| **Arriba** (barra, derecha) | `buttonsOnly` | `«` `‹` números `›` `»` |
| **Pie** (`footer.joli-table-footer`) | completa | «Mostrar [10/20/50/100]» · «Mostrando X a Y de Z {itemLabel}» · botones |

- Tamaño por defecto 10; al cambiarlo se vuelve a página 1; la página se limita al total cuando el filtro reduce resultados.
- Ventana de **3 números** alrededor de la página actual, sin elipsis. En ≤768 px se ocultan los números y la etiqueta «Mostrar».
- Detalle del componente: [`pagination.md`](../pagination/pagination.md) §0.

---

## 4. Tabla

### 4.1. Columnas declarativas
Las columnas se declaran en un archivo de configuración del módulo (`usuariosConfig.ts`):

```ts
export interface ColumnaTabla<T> {
  key: string;
  label: string;
  defaultWidth: number;          // px
  dataType?: 'text' | 'number' | 'date';
  filterable?: boolean;          // filtro tipo Excel; por defecto true
  getValue: (fila: T) => string; // texto para filtrar y mostrar en el filtro (y ordenar, si no hay sortValue)
  sortValue?: (fila: T) => string; // valor para ordenar cuando el texto mostrado no ordena bien (fechas: ISO)
}
```

Ejemplo (Usuarios):

| key | Etiqueta | Ancho | `getValue` |
| :--- | :--- | :--- | :--- |
| `nombre` | Usuario | 260 | nombre |
| `cargo` | Cargo / Área | 190 | `"{cargo \| 'Sin cargo asignado'} - {area \| 'Sin área'}"` |
| `zona` | Zona | 120 | zona o «Sin zona» |
| `rol` | Rol | 110 | rol o «Sin rol» |
| `estado` | Estado | 115 | «Activo» / «Inactivo» |
| `ultimo_inicio` | Último inicio APK | 175 | fecha formateada; `sortValue` = fecha ISO; `dataType: 'date'`, `filterable: false` |
| `ubicacion` | Ubicación | 260 | dirección, «Dirección pendiente» o «Sin ubicación» (nunca coordenadas) |

Más una columna **Acciones** fija de 124 px, alineada a la derecha. Valores vacíos se muestran con un texto («Sin cargo asignado»), nunca en blanco.

### 4.2. Estructura y CSS
```tsx
<table className="joli-data-table">
  <thead><tr>
    <th scope="col" className={`resizable-th ${filtrada ? 'th-filtered' : ''}`} style={{ width, minWidth: width, maxWidth: width }}
        aria-sort={orden === col.key ? (asc ? 'ascending' : 'descending') : 'none'}>
      <button type="button" className="th-label sortable" onClick={() => ordenar(col.key)} title={`Ordenar por ${col.label}`}>
        {col.label}{orden === col.key && (asc ? <ChevronUp size={13} className="sort-icon" /> : <ChevronDown size={13} className="sort-icon" />)}
      </button>
      {col.filterable !== false && <BotonFiltroExcel ... />}       {/* §4.4 */}
      <div className="resizable-th-resizer" role="separator" aria-orientation="vertical" tabIndex={0} ... />   {/* §4.5 */}
    </th>
    ...
    <th scope="col" className="actions-th" style={{ width: 124 }}>Acciones</th>
  </tr></thead>
  <tbody>...</tbody>
</table>
```
```css
.joli-data-table { table-layout: fixed; border-collapse: collapse; font-size: var(--font-size-sm); }
.joli-data-table th { position: sticky; top: 0; z-index: 10; padding: .75rem 1rem; font-size: 11.5px;
                      text-transform: uppercase; letter-spacing: .05em; color: var(--text-muted); }
.joli-data-table td { padding: .875rem 1rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.joli-data-table td:has(button, a, input, select, .joli-badge, .row-actions-group) { text-overflow: clip; white-space: normal; }
.joli-data-table td.actions-cell { overflow: visible; }
.joli-data-table tbody tr:hover { background: var(--bg-hover); }
```

### 4.3. Ordenar
Clic en otra columna → ascendente; en la misma → alterna. Todas las columnas se pueden ordenar. Comparación con `localeCompare('es', { numeric: true, sensitivity: 'base' })` sobre `sortValue ?? getValue`. Las columnas de **fecha** DEBEN declarar `sortValue` con el valor crudo (ISO o timestamp): ordenar por el texto formateado («08/11/2026») da un orden falso.

### 4.4. Filtro tipo Excel por columna
Botón en el encabezado y [`ChecklistPopover`](./checklist_popover.md) con los valores de **todas** las filas:
```tsx
<button type="button" className={`th-filter-btn ${activo || abierto ? 'active' : ''}`} aria-label={`Filtrar por ${col.label}`}
        aria-haspopup="dialog" aria-expanded={abierto} title={activo ? `Filtro activo (${n}): ${col.label}` : `Filtrar por ${col.label}`}>
  <Filter size={12} />{activo && <span className="th-filter-dot" />}
</button>
{abierto && (
  <div className="th-filter-popover-container" ref={popoverRef}>
    <ChecklistPopover colKey colLabel dataType items={filas} getValue={col.getValue} activeValues
                      onApply={(valores) => ...} onSort={...} currentSortField currentSortOrder onClose={...} />
  </div>
)}
```
- `onApply(null)` = sin filtro. El filtro compara `getValue(fila).trim()` con los valores permitidos. `onSort` ordena y cierra. El encabezado filtrado lleva `.th-filtered` (`rgba(brand, .12)`, color de marca).

### 4.5. Columnas redimensionables y persistidas
Separador `div.resizable-th-resizer` (5 px; hover `--brand-solid`) en el borde derecho del encabezado: arrastrar cambia el ancho; doble clic restablece el ancho por defecto. Ancho mínimo **70 px**. Detalle en [`column_resizer.md`](./column_resizer.md) §0.

### 4.6. Celdas tipo
| Celda | Estructura | Notas |
| :--- | :--- | :--- |
| **Persona** | `div.user-cell` > `div.user-cell-avatar` (34 px redondo; foto `img.user-avatar-image` que se oculta con `onError`, o iniciales 12 px bold blancas sobre degradado `--brand-solid → --brand-solid-hover`) + `div.user-cell-info` (`span.user-cell-name`, `span.user-cell-doc` «CC {doc}» monoespaciada 2xs, `span.user-cell-email`) | Todos con `title` |
| **Texto con subtexto** | `div.user-cargo-cell` > `span.user-cargo-title.table-cell-truncate` + `span.user-area-subtext` | Cargo arriba, área debajo |
| **Etiqueta** | `span.role-tag` (11 px semibold, `bg-input`, borde, `radius-sm`) | Rol u otra categoría corta |
| **Estado** | `span.status-pill.{active\|inactive}` > `span.status-dot-indicator` (6 px, `currentColor`) + texto | Verde / rojo con fondo `-bg` y borde `color-mix` 30 %. Ver [`badge_status.md`](../badge/badge_status.md) §0 |
| **Fecha + sesión** | fecha formateada + `SessionIndicator` (punto de 7 px, «Sesión activa» en `--status-success` o «Sesión cerrada» en `--text-muted`, 0.75rem) | |
| **Ubicación** | dirección (`text-secondary`) + debajo `.texto-tenue` (0.75rem) «Última conocida · {fecha}» si llegó más de 10 min tarde | `title` con dirección y «Registrada: …»; nunca coordenadas |
| **Contador que abre detalle** | `button.clientes-sap-btn` con ícono + palabra («Clientes») + `span` del número en monoespaciada con `min-width: 3ch`, `tabular-nums` y alineado a la derecha | Con 0 queda `disabled` con `title` que explica por qué; abre un drawer con la tabla del detalle. El ancho de 3 dígitos evita botones de tamaños distintos (pedido del usuario, 2026-11-10) |

### 4.7. Acciones de fila
```tsx
<td className="actions-cell">
  <div className="row-actions-group" role="group" aria-label="Acciones de colaborador">
    <MapButton ... />                                                  {/* action-btn map */}
    <button type="button" className="action-btn edit" aria-label="Editar usuario" title="Editar usuario"><Edit2 size={14} /></button>
    <button type="button" className={`action-btn toggle ${activo ? 'danger' : 'success'}`}
            aria-label={activo ? 'Desactivar cuenta' : 'Activar cuenta'} title={...} disabled={esPropiaCuenta}><Power size={14} /></button>
  </div>
</td>
```
- Grupo de 28 px, `radius-md`, `bg-input`, borde; botones de 30 × 28 separados por `border-right`. Hover: editar `bg-hover`, peligro rojo, éxito verde, mapa marca. Deshabilitado `opacity: .4`.
- **Mapa:** con ubicación, `MapPin` abre `https://www.google.com/maps/search/?api=1&query={lat},{lon}` en otra pestaña (`noopener,noreferrer`) y su `title` lleva dirección, fecha y «Precisión: ±N m»; sin ubicación, deshabilitado con `MapPinOff` y «Sin ubicación registrada».
- **Sobre la propia cuenta:** el botón de activar/desactivar va deshabilitado con «No puedes activar ni desactivar tu propia cuenta» (el backend también lo impide).

### 4.8. Activar / desactivar
Botón `Power` + [`ConfirmModal`](../modal/confirm_modal.md) **en ambos sentidos** (no un interruptor en la fila):
- Desactivar: `type="danger"`, título «Desactivar cuenta», botón «Desactivar», mensaje que explica las consecuencias («No podrá ingresar a la APK ni al panel, se cerrarán sus sesiones abiertas…»).
- Activar: `type="success"`, «Activar cuenta» / «Activar», «Podrá volver a ingresar con su documento y contraseña.»
- Mientras se procesa no se puede cerrar. Éxito: toast «Cuenta activada» / «Cuenta desactivada» y recarga. La justificación (`requiresJustification`) es opcional por módulo.

---

## 5. Vista en tarjetas

- Rejilla `div.users-cards-grid`: 3 columnas, `gap: 1rem`, `padding: 1.25rem`; ≤1200 px 2 columnas; ≤768 px 1 columna (`gap/padding .65rem`).
- Cada fila es una [`CorporateCard`](../card/corporate_card.md) (§0): `title` = nombre, `subtitle` = correo, `elevation="glow"`, `icon` = avatar de 36 px, `headerActions` = `status-pill`, `footerMetadata` = `SessionIndicator`, `footerCustomActions` = el mismo `row-actions-group` de la tabla. Inactivos con `.is-inactive` (borde superior rosa, `opacity: .9`).
- Cuerpo `div.corp-card__plain-grid` (2 columnas, `gap: 6px 14px`) con filas `div.user-card-meta-row` > `span.meta-label` (ícono 12 px + texto) + `span.meta-value` (o `mono-badge` para documentos).
- En ≤768 px la vista de tarjetas es obligatoria (se oculta el botón Tabla).

---

## 6. Carga, vacío y refresco

- **Primera carga:** `TableSkeleton` (8 filas) dentro de la tarjeta y cortinilla `PageLoader variant="curtain"` solo con `isLoading && datos.length === 0`. En recargas y después de guardar basta con el giro del botón Recargar y `aria-busy`; sin botón Recargar, la tabla se atenúa con `.joli-table-wrapper.is-recargando` (ver [`page_loader.md`](../loader/page_loader.md)).
- **Tabla dentro de un drawer:** el esqueleto va **en la misma tabla**, bajo los encabezados reales y con los mismos anchos, con tantas filas como mostrará la primera página (`min(tamaño de página, total esperado)`); las filas de datos y de esqueleto llevan la misma altura fija (`tbody tr { height }`) para que nada salte al llegar los datos. El vacío se muestra solo cuando ya no está cargando.
- **Vacío:** `div.table-centered-empty-state role="status"` (ilustración SVG de 58 px + `p.table-empty-message`), centrado, `min-height: 260px`. En tabla va **después** del `<table>` (el encabezado se queda); en tarjetas reemplaza la rejilla. Mensaje según la causa, en este orden: «No hay datos registrados» → `No se encontraron datos para "{búsqueda}"` → filtro de estado → filtro de cabecera (con el **nombre** visible del valor, no su id) → «No se encontraron datos».
- **Sondeo:** `useSmartPolling(cargar, { intervalMs: 30000, pauseOnHidden: true, immediate: false })` ([`js_polling_architecture.md`](../realtime/js_polling_architecture.md)). Se salta mientras el drawer de edición está abierto o guardando, y solo reemplaza el estado si los datos cambiaron (comparación del JSON). Con sesión vencida no muestra toast.

---

## 7. Preferencias guardadas

| Qué | Clave | Formato |
| :--- | :--- | :--- |
| Columnas visibles | `<app>_<modulo>_visible_columns_v<N>` (Pandora: `pandora_users_visible_columns_v3`) | arreglo JSON de `key`; subir `vN` al cambiar las columnas |
| Anchos de columna | `<app>_<modulo>_col_widths` | objeto JSON que se mezcla con los anchos por defecto |
| Ancho de drawers | `<app>_drawer_ancho_{sm\|md\|lg}` | número (px) |

Toda lectura y escritura con `try/catch` (normativa 6.8). La vista (tabla/tarjetas), el tamaño de página y los filtros **no** se guardan: cada visita empieza limpia.

---

## 8. Responsive

| Ancho | Cambios |
| :--- | :--- |
| ≤1200 px | Tarjetas en 2 columnas |
| ≤768 px (`matchMedia`) | Vista de tarjetas forzada y sin botón Tabla; se ocultan filtros de cabecera y visibilidad de columnas; la barra se apila y `toolbar-right` ocupa el ancho con `border-top`; se ocultan los números de página y «Mostrar»; botones compactos de 32 px; drawers sin redimensionar ni expandir |
| ≤640 px | Formulario y mini-KPIs del drawer en una columna |

La vista inicial depende del ancho de la ventana al entrar.

---

## 9. Formularios de crear y editar

En un drawer ([`drawer.md`](../drawer/drawer.md) §1.1), con campos de etiqueta flotante ([`floating_field.md`](../form/floating_field.md)) en rejilla de 2 columnas (`form.drawer-form-grid`). Patrones del drawer de Usuarios: mini-KPIs, foto de perfil, contraseña con botón «requiere cambio» y campo de solo lectura con candado → ver [`drawer.md`](../drawer/drawer.md) §1.2.

---

## 10. Lista de revisión de una pantalla nueva

- [ ] Composición §1: tarjeta, barra, tabla/tarjetas, pie con paginación completa; drawers fuera de la tarjeta.
- [ ] Barra §2 en el orden exacto; buscador desplegable; filtros de cabecera; limpiar todo; columnas; exportar; paginación solo botones; caja compacta.
- [ ] Columnas declarativas §4.1 con `getValue`; fechas ordenan por valor crudo.
- [ ] Encabezados accesibles: botón para ordenar, `scope`, `aria-sort`; filtro Excel con `aria-expanded`.
- [ ] Celdas tipo §4.6 y acciones de fila §4.7 con `aria-label` y `title`.
- [ ] Vista en tarjetas §5 y obligatoria en móvil.
- [ ] Esqueleto, vacío con mensaje según la causa y sondeo de 30 s que se pausa al editar.
- [ ] Claves de almacenamiento §7 con `try/catch`.
- [ ] Revisado en tema claro y oscuro, escritorio y móvil.

---

## 11. Componentes compartidos (`frontend-admin/src/components/ui/tabla/`)

Las 6 pantallas de tabla del panel (Usuarios, Clientes, Historial de rutas, Programación de ruta, Control de versiones y Logs) los usan; la accesibilidad y la persistencia se corrigen una sola vez aquí.

| Pieza | Reemplaza | Lo que garantiza |
| :--- | :--- | :--- |
| `BotoneraVista` | `.view-switcher` escrito a mano (§2.1) | `aria-pressed` en las vistas, búsqueda `type="search"` con `aria-label`/`aria-controls`, foco al abrir, `Escape` cierra sin borrar, la X borra y cierra. `sinVistas` para pantallas solo con buscador |
| `GrupoFiltros` + `FiltroExpandible` | `.expandable-filter-group` / `-item` (§2.2) | `role="group"`, `aria-controls`, `aria-label` en el select, foco al abrir, `Escape` cierra y devuelve el foco, insignia con el texto de la opción y `title` |
| `BotonLimpiarFiltros` | `.filter-actions-group` (§2.3) | `aria-label`; fuera del orden de Tab cuando está oculto |
| `EncabezadoColumna` | `<th className="resizable-th">` (§4.2–4.5) | `scope="col"`, `aria-sort`, ordenar con un botón, filtro Excel con `aria-haspopup`/`aria-expanded`/`aria-controls`, separador de ancho `role="separator"` con teclado |
| `useAnchosColumnas(clave, porDefecto)` | estado de anchos de cada pantalla (§4.5) | mínimo 70 px, guardar al soltar con `try/catch`, doble clic y Enter restablecen, flechas ajustan |

Fuera de `tabla/`, también compartidos: `Pagination` (§3), `ChecklistPopover` (§4.4), `ColumnVisibilityDropdown` (§2.4), `RightDrawer` + `useFocoAtrapado` (§9) y `ConfirmModal`.

Se quedan propios de cada pantalla los controles que no son 1 a 1 con un componente: el filtro de **Fecha** del planeador de rutas (selector de fecha + flechas + insignia calculada) y los filtros rápidos por KPI (Clientes, Versiones).
