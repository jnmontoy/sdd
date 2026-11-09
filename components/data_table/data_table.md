# Componente Maestro: Tabla de Datos Empresarial (`DataTable`)
## Spec-Driven Development (SDD)

La **Data Table** es el componente base para listados operativos, inventarios, transacciones, auditorías y catálogos.

Trabaja con **paginación en el servidor** (el navegador solo recibe la página visible), buscador con espera (*debounce*) de 350 ms, filtros por columna tipo Excel, ordenamiento, visibilidad y ancho de columnas persistidos, y exportación a Excel (`.xlsx`).

> **¿Es este el componente que necesitas?** Las pantallas de listado del panel administrativo cuyo listado completo cabe en memoria (usuarios, roles, versiones, rutas) siguen el patrón [`admin_table_screen.md`](./admin_table_screen.md): datos en el navegador, botonera de vista y búsqueda desplegable, paginación arriba y al pie, y vista en tarjetas. Este `DataTable` con paginación en servidor es para catálogos grandes o que crecen sin límite.

> La paginación en servidor reduce memoria y tiempo de transferencia; **no** resuelve consultas N+1. Evitar N+1 es responsabilidad del backend (`select_related` / `prefetch_related` en Django, consultas agregadas en FastAPI).

Piezas que lo componen:

| Pieza | Documento |
| :--- | :--- |
| Filtro por columna | [`checklist_popover.md`](./checklist_popover.md) |
| Visibilidad de columnas | [`column_visibility.md`](./column_visibility.md) |
| Ancho de columnas | [`column_resizer.md`](./column_resizer.md) |
| Paginador (en la barra superior) | [`../pagination/pagination.md`](../pagination/pagination.md) |
| Acciones por fila (`btn-group`) | [`../button/icon_action_group.md`](../button/icon_action_group.md) |
| Exportación | [`../export/excel_export.md`](../export/excel_export.md) |

---

## 1. Reglas de presentación (convenciones de diseño)

Estas reglas son **DEBERÍA**: se pueden desviar con pedido explícito del usuario o una decisión registrada (ADR).

1. **Paginador arriba, en la barra de herramientas.** **Por qué:** se controla página, tamaño y búsqueda sin desplazarse al pie de la tabla.
2. **La tarjeta de la tabla llega hasta el borde inferior del viewport.** La tarjeta (`.joli-datatable-wrapper`) usa `flex: 1; min-height: 420px; display: flex; flex-direction: column; overflow: hidden;` dentro de una página `display: flex; flex-direction: column; min-height: calc(100vh - var(--topbar-height));`. La tabla interna (`.joli-table-container`) usa `flex: 1; overflow: auto;`. **Por qué:** aprovecha la altura disponible y deja el encabezado fijo con scroll interno.
3. **Acciones de fila agrupadas.** Con 2 o más botones por fila, se agrupan en `<div className="btn-group btn-group-sm row-actions-group" role="group" aria-label="Acciones de fila">`; no se separan con márgenes. **Por qué:** lectura uniforme, menos ancho y una sola zona de clic por fila.
4. **Datos en colores neutros.** Códigos, identificadores y fechas usan tipografía monoespaciada neutra (`--text-primary` / `--text-secondary`). El color se reserva para badges de estado ([`badge_status.md`](../badge/badge_status.md)). **Por qué:** el color debe significar estado, no decoración.

---

## 2. Contrato de propiedades

```typescript
import type { ChecklistOption } from './ChecklistPopover';

export interface ColumnDef<T> {
  key: Extract<keyof T, string>;
  header: string;
  render?: (row: T) => React.ReactNode;
  /** Por defecto true. */
  sortable?: boolean;
  /** Habilita el filtro tipo Excel en el encabezado (por defecto false). */
  filterable?: boolean;
  dataType?: 'text' | 'number' | 'date';
  /** Ancho por defecto en píxeles. */
  width?: number;
  formatValue?: (value: unknown) => string;
}

export interface DataTableProps<T extends { id: string | number }> {
  /** Identificador del módulo: prefijo de las preferencias guardadas (STORAGE_KEYS). */
  modulo: string;
  columns: ColumnDef<T>[];
  data: T[];
  totalRows: number;
  currentPage: number;
  pageSize: number;
  isLoading?: boolean;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  /** Se llama con debounce (350 ms). */
  onSearchChange: (query: string) => void;
  onFilterChange?: (filters: Record<string, string[]>) => void;
  onSortChange?: (field: string, order: 'ASC' | 'DESC') => void;
  /** Valores distintos por columna calculados por el servidor (ver ChecklistPopover). */
  filterOptions?: Record<string, ChecklistOption[]>;
  /** Obtiene TODOS los registros filtrados para exportar (no solo la página visible). */
  getExportData?: () => Promise<T[]>;
  filenameExportPrefix?: string;
  /** Botones de la fila; se renderizan dentro del btn-group. */
  actions?: (row: T) => React.ReactNode;
  onRowClick?: (row: T) => void;
  selectedRowId?: string | number | null;
}
```

---

## 3. Código JSX / React de referencia (`DataTable.tsx`)

```tsx
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { ChevronDown, ChevronUp, Filter, FilterX, Inbox, Loader2, RotateCcw, Search, X } from 'lucide-react';
import { ChecklistPopover, type ChecklistOption } from './ChecklistPopover';
import { ColumnVisibilityDropdown } from './ColumnVisibilityDropdown';
import { Pagination } from '../pagination/Pagination';
import { ExportExcelButton } from '../export/ExportExcelButton';
import { useColumnResize } from '../../hooks/useColumnResize';
import { useVisibleColumns } from '../../hooks/useVisibleColumns';

const SEARCH_DEBOUNCE_MS = 350;

export function DataTable<T extends { id: string | number }>({
  modulo,
  columns,
  data,
  totalRows,
  currentPage,
  pageSize,
  isLoading = false,
  onPageChange,
  onPageSizeChange,
  onSearchChange,
  onFilterChange,
  onSortChange,
  filterOptions,
  getExportData,
  filenameExportPrefix = 'Reporte',
  actions,
  onRowClick,
  selectedRowId,
}: DataTableProps<T>) {
  // 1. Búsqueda con debounce (se cancela el temporizador al teclear de nuevo o desmontar)
  const [searchTerm, setSearchTerm] = useState('');
  const onSearchChangeRef = useRef(onSearchChange);
  useEffect(() => {
    onSearchChangeRef.current = onSearchChange;
  }, [onSearchChange]);
  const isFirstRender = useRef(true);
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    const timer = setTimeout(() => onSearchChangeRef.current(searchTerm.trim()), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // 2. Ordenamiento
  const [sortField, setSortField] = useState('');
  const [sortOrder, setSortOrder] = useState<'ASC' | 'DESC'>('ASC');
  const applySort = (field: string, order: 'ASC' | 'DESC') => {
    setSortField(field);
    setSortOrder(order);
    onSortChange?.(field, order);
  };

  // 3. Filtros tipo Excel
  const [columnFilters, setColumnFilters] = useState<Record<string, string[]>>({});
  const [activeFilterCol, setActiveFilterCol] = useState<string | null>(null);
  const filterPopoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!activeFilterCol) return;
    const onMouseDown = (e: MouseEvent) => {
      if (filterPopoverRef.current && !filterPopoverRef.current.contains(e.target as Node)) {
        setActiveFilterCol(null);
      }
    };
    document.addEventListener('mousedown', onMouseDown);
    return () => document.removeEventListener('mousedown', onMouseDown);
  }, [activeFilterCol]);

  const handleApplyColumnFilter = (colKey: string, values: string[]) => {
    const next = { ...columnFilters };
    if (values.length === 0) delete next[colKey];
    else next[colKey] = values;
    setColumnFilters(next);
    onFilterChange?.(next); // efecto fuera del actualizador de estado (seguro en StrictMode)
  };

  const handleResetAll = () => {
    setColumnFilters({});
    setSearchTerm('');
    onFilterChange?.({});
    setActiveFilterCol(null);
  };

  const activeFiltersCount = Object.keys(columnFilters).length + (searchTerm ? 1 : 0);

  // 4. Preferencias persistidas por módulo (claves con prefijo de app)
  const allKeys = useMemo(() => columns.map((c) => c.key), [columns]);
  const { visibleColumns, setVisibleColumns, resetVisibleColumns } = useVisibleColumns(modulo, allKeys);
  const defaultWidths = useMemo(
    () => Object.fromEntries(columns.map((c) => [c.key, c.width ?? 150])),
    [columns],
  );
  const { colWidths, handleStartResize, handleResetWidth, handleKeyResize } = useColumnResize(modulo, defaultWidths);

  const renderedColumns = useMemo(
    () => columns.filter((c) => visibleColumns.includes(c.key)),
    [columns, visibleColumns],
  );
  const colSpan = renderedColumns.length + (actions ? 1 : 0);

  const renderCell = (row: T, col: ColumnDef<T>) => {
    if (col.render) return col.render(row);
    const value = row[col.key];
    return col.formatValue ? col.formatValue(value) : String(value ?? '');
  };

  return (
    <div className="joli-datatable-wrapper">
      {/* 1. BARRA DE HERRAMIENTAS CON PAGINADOR INTEGRADO */}
      <div className="joli-datatable-toolbar">
        <div className="toolbar-left">
          <div className="joli-search-box">
            <Search size={16} className="joli-search-icon" aria-hidden="true" />
            <input
              type="search"
              className="joli-search-input"
              placeholder="Buscar en registros..."
              aria-label="Buscar en registros"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              data-testid="datatable-search-input"
            />
            {searchTerm && (
              <button
                type="button"
                className="joli-search-clear"
                onClick={() => setSearchTerm('')}
                aria-label="Limpiar búsqueda"
              >
                <X size={14} aria-hidden="true" />
              </button>
            )}
          </div>

          {activeFiltersCount > 0 && (
            <button type="button" className="joli-btn-reset-filters" onClick={handleResetAll}>
              <FilterX size={14} aria-hidden="true" />
              <span>Limpiar filtros ({activeFiltersCount})</span>
            </button>
          )}
        </div>

        <div className="toolbar-right">
          <ColumnVisibilityDropdown
            columns={columns.map((c) => ({ key: c.key, label: c.header }))}
            visibleColumns={visibleColumns}
            onChange={setVisibleColumns}
            onResetDefault={resetVisibleColumns}
          />

          {getExportData && (
            <ExportExcelButton
              filenamePrefix={filenameExportPrefix}
              columns={renderedColumns.map((c) => ({
                header: c.header,
                key: c.key,
                formatter: c.formatValue ? (value: unknown) => c.formatValue!(value) : undefined,
              }))}
              getData={getExportData}
              totalCount={totalRows}
            />
          )}

          <Pagination
            currentPage={currentPage}
            totalItems={totalRows}
            pageSize={pageSize}
            onPageChange={onPageChange}
            onPageSizeChange={onPageSizeChange}
            disabled={isLoading}
          />
        </div>
      </div>

      {/* 2. TABLA CON ENCABEZADO FIJO Y SCROLL INTERNO */}
      <div className="joli-table-container">
        <table className="joli-table" aria-busy={isLoading}>
          <thead>
            <tr>
              {renderedColumns.map((col) => {
                const isFiltered = (columnFilters[col.key]?.length ?? 0) > 0;
                const isSorted = sortField === col.key;
                const isOpen = activeFilterCol === col.key;
                const sortable = col.sortable !== false;

                return (
                  <th
                    key={col.key}
                    scope="col"
                    style={{ width: colWidths[col.key] }}
                    className={`resizable-th ${isFiltered ? 'th-filtered' : ''}`}
                    aria-sort={isSorted ? (sortOrder === 'ASC' ? 'ascending' : 'descending') : undefined}
                  >
                    <div className="th-content-wrapper">
                      {sortable ? (
                        <button
                          type="button"
                          className="th-sort-btn"
                          onClick={() => applySort(col.key, isSorted && sortOrder === 'ASC' ? 'DESC' : 'ASC')}
                        >
                          {col.header}
                          {isSorted && (sortOrder === 'ASC'
                            ? <ChevronUp size={14} aria-hidden="true" />
                            : <ChevronDown size={14} aria-hidden="true" />)}
                        </button>
                      ) : (
                        <span className="th-label">{col.header}</span>
                      )}

                      {col.filterable && (
                        <button
                          type="button"
                          className={`th-filter-btn ${isFiltered ? 'active' : ''}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setActiveFilterCol(isOpen ? null : col.key);
                          }}
                          aria-label={isFiltered
                            ? `Filtro activo en ${col.header} (${columnFilters[col.key].length} valores)`
                            : `Filtrar por ${col.header}`}
                          aria-expanded={isOpen}
                          aria-haspopup="dialog"
                        >
                          <Filter size={12} aria-hidden="true" />
                          {isFiltered && <span className="th-filter-dot" aria-hidden="true" />}
                        </button>
                      )}
                    </div>

                    {isOpen && (
                      <div className="th-filter-popover-container" ref={filterPopoverRef}>
                        <ChecklistPopover<T>
                          colKey={col.key}
                          colLabel={col.header}
                          dataType={col.dataType}
                          items={data}
                          options={filterOptions?.[col.key]}
                          activeValues={columnFilters[col.key]}
                          onApply={(values) => handleApplyColumnFilter(col.key, values)}
                          onSort={(field, order) => {
                            applySort(field, order);
                            setActiveFilterCol(null);
                          }}
                          currentSortField={sortField}
                          currentSortOrder={sortOrder}
                          onClose={() => setActiveFilterCol(null)}
                          formatValue={col.formatValue}
                        />
                      </div>
                    )}

                    <div
                      className="resizable-th-resizer"
                      role="separator"
                      aria-orientation="vertical"
                      aria-label={`Ajustar ancho de ${col.header}`}
                      tabIndex={0}
                      onMouseDown={(e) => handleStartResize(col.key, e)}
                      onDoubleClick={() => handleResetWidth(col.key)}
                      onKeyDown={(e) => handleKeyResize(col.key, e)}
                    />
                  </th>
                );
              })}
              {actions && <th scope="col" className="text-end th-actions">Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={colSpan} className="text-center py-5" role="status">
                  <Loader2 size={32} className="table-spinner mb-2" aria-hidden="true" />
                  <p className="table-state-text mb-0">Consultando registros...</p>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={colSpan} className="text-center py-5">
                  <div className="table-empty-state">
                    <Inbox size={40} className="empty-icon mb-2" aria-hidden="true" />
                    <p className="empty-title">Sin registros encontrados</p>
                    <p className="empty-desc">
                      {activeFiltersCount > 0
                        ? 'No hay registros que coincidan con los filtros aplicados.'
                        : 'No hay datos disponibles en este módulo.'}
                    </p>
                    {activeFiltersCount > 0 && (
                      <button type="button" className="joli-btn-secondary mt-2" onClick={handleResetAll}>
                        <RotateCcw size={13} aria-hidden="true" />
                        <span>Restablecer filtros</span>
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ) : (
              data.map((row) => {
                const isSelected = selectedRowId != null && selectedRowId === row.id;
                return (
                  <tr
                    key={row.id}
                    data-testid="datatable-row"
                    className={`${isSelected ? 'row-selected' : ''} ${onRowClick ? 'row-clickable' : ''}`}
                    aria-selected={onRowClick ? isSelected : undefined}
                    tabIndex={onRowClick ? 0 : undefined}
                    onClick={onRowClick ? () => onRowClick(row) : undefined}
                    onKeyDown={onRowClick ? (e) => {
                      if (e.key === 'Enter' && e.target === e.currentTarget) onRowClick(row);
                    } : undefined}
                  >
                    {renderedColumns.map((col) => (
                      <td key={col.key}>{renderCell(row, col)}</td>
                    ))}
                    {actions && (
                      <td className="text-end" onClick={(e) => e.stopPropagation()}>
                        <div className="btn-group btn-group-sm row-actions-group" role="group" aria-label="Acciones de fila">
                          {actions(row)}
                        </div>
                      </td>
                    )}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

**Notas:**
- Los botones que entrega `actions(row)` DEBEN ser solo-ícono con `aria-label` y `title` (ver [`icon_action_group.md`](../button/icon_action_group.md)). Con más de 3 acciones, las secundarias van en un `dropdown-toggle` dentro del mismo grupo.
- La exportación usa `getExportData` para pedir al backend **todos** los registros filtrados; exportar `data` solo incluiría la página visible.
- El botón de exportación expone `data-testid="btn-export-excel"` (definido en `ExportExcelButton`).

---

## 4. Estilos CSS (`data_table.css`)

Todos los colores salen de tokens de [`variables.css`](../variables.css); por eso no hacen falta reglas `[data-theme="dark"]` separadas.

```css
.joli-datatable-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 420px;
  overflow: hidden;
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
}

/* 1. BARRA SUPERIOR */
.joli-datatable-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-card);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.joli-search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 260px;
}

.joli-search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-muted);
  pointer-events: none;
}

.joli-search-input {
  width: 100%;
  height: 32px;
  padding: 0 30px 0 32px;
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--radius-md);
  color: var(--input-text);
  font-size: var(--font-size-xs);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.joli-search-input::placeholder {
  color: var(--input-placeholder);
}

.joli-search-input:focus {
  outline: none;
  border-color: var(--input-focus-border);
  box-shadow: var(--shadow-input-focus);
  background-color: var(--bg-input-focus);
}

.joli-search-clear {
  position: absolute;
  right: 8px;
  display: flex;
  padding: 2px;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--text-muted);
  cursor: pointer;
}

.joli-search-clear:hover {
  color: var(--text-primary);
}

.joli-btn-reset-filters {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 12px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
  border: 1px solid var(--alert-error-border);
  background: var(--alert-error-bg);
  color: var(--status-error);
  cursor: pointer;
  transition: filter var(--transition-fast);
}

.joli-btn-reset-filters:hover {
  filter: brightness(1.1);
}

/* .joli-btn-secondary se define en ../button/icon_action_group.md §5 */

/* 2. TABLA Y ENCABEZADOS */
.joli-table-container {
  position: relative;
  flex: 1;
  min-height: 250px;
  overflow: auto;
}

.joli-table {
  width: 100%;
  margin: 0;
  table-layout: fixed;
  border-collapse: separate;
  border-spacing: 0;
  font-size: var(--font-size-xs);
}

.joli-table thead th {
  position: sticky;
  top: 0;
  z-index: var(--z-card);
  padding: 8px 12px;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  border-bottom: 2px solid var(--border-subtle);
}

.joli-table thead th.th-filtered {
  background: var(--status-success-bg);
  color: var(--text-primary);
}

.th-content-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.th-label,
.th-sort-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  user-select: none;
}

.th-sort-btn {
  padding: 0;
  background: none;
  border: none;
  color: inherit;
  font: inherit;
  letter-spacing: inherit;
  text-transform: inherit;
  cursor: pointer;
}

.th-sort-btn:hover {
  color: var(--text-primary);
}

.th-filter-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.th-filter-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.th-filter-btn.active {
  background: var(--status-success-bg);
  border-color: var(--border-card-accent);
  color: var(--brand-primary);
}

.th-sort-btn:focus-visible,
.th-filter-btn:focus-visible,
.joli-table tbody tr.row-clickable:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: -2px;
}

.th-filter-dot {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 5px;
  height: 5px;
  border-radius: var(--radius-full);
  background: var(--brand-primary);
}

.th-filter-popover-container {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: var(--z-popover);
  font-weight: var(--font-weight-regular);
  text-transform: none;
  letter-spacing: normal;
}

.th-actions {
  width: 110px;
}

/* 3. CUERPO Y FILAS */
.joli-table tbody td {
  padding: 8px 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-subtle);
}

.joli-table tbody tr:hover td {
  background-color: var(--bg-hover);
}

.joli-table tbody tr.row-clickable {
  cursor: pointer;
}

.joli-table tbody tr.row-selected td {
  background-color: var(--status-success-bg);
}

.table-spinner {
  color: var(--brand-primary);
  animation: joliSpin 1s linear infinite;
}

.table-state-text {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
}

/* ESTADO VACÍO */
.table-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  white-space: normal;
}

.table-empty-state .empty-icon {
  color: var(--text-muted);
  opacity: 0.6;
}

.table-empty-state .empty-title {
  margin: 0 0 4px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.table-empty-state .empty-desc {
  max-width: 360px;
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

@keyframes joliSpin {
  to { transform: rotate(360deg); }
}
```
