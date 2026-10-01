# Componente Maestro: Tabla de Datos Empresarial (Data Table)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

La **Data Table** es el componente nuclear de gestión de datos para listados operativos, inventarios, transacciones, auditorías y catálogos en las aplicaciones de Jolifoods.

Implementa **paginación del lado del servidor (Server-Side Pagination)** para evitar problemas de rendimiento y sobrecarga de memoria (Anti-N+1), buscador en tiempo real con debounce, exportación directa a Excel (`.xlsx`) y ordenamiento por columnas.

---

## 1. Contrato de Propiedades (TypeScript Genérico)

```typescript
export interface ColumnDef<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
  sortable?: boolean;
  filterable?: boolean;       // ⭐ Habilita el filtro de columna desplegable tipo Excel
  dataType?: 'text' | 'number' | 'date';
  width?: string;
}

export interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  totalRows: number;
  currentPage: number;
  pageSize: number;
  isLoading?: boolean;
  onPageChange: (page: number) => void;
  onSearchChange: (query: string) => void;
  onFilterChange?: (filters: Record<string, string[]>) => void; // Filtros tipo Excel
  onExportExcel?: () => void;
  onExportPdf?: () => void;
  actions?: (row: T) => React.ReactNode;
}
```

> **FILTROS DE COLUMNA TIPO EXCEL**:
> Cada columna con `filterable: true` renderiza un icono de filtro en su encabezado `<th>`.
> Al hacer clic, despliega el componente **[`ChecklistPopover`](./checklist_popover.md)** con ordenamiento A-Z / Z-A, buscador interactivo, casilla "Seleccionar Todo" con soporte tri-estado, conteo de ocurrencias `(count)` y botón "Solo".

> **REGLAS DE PRESENTACIÓN, ACCIONES POR FILA Y LAYOUT DE PANTALLA (UX/UI)**:
> 1. **Paginador Superior Integrado en Toolbar (Estándar bi/cartera)**: En las aplicaciones de Jolifoods, el paginador **NO se ubica al pie de la tabla**. Se ubica **ARRIBA DE LA TABLA**, integrado directamente en la barra superior (`.cartera-table-header-toolbar.pagination-container`), unificando el selector "Mostrar [10 v] por página", el buscador, los filtros activos, la visibilidad de columnas, la info de registros y los botones de cambio de página (`<<`, `<`, 1, 2, 3, `>`, `>>`).
> 2. **Card Contenedora hasta Abajo de la Pantalla (`.cartera-main-card`)**: La card principal que contiene la tabla utiliza `flex: 1; min-height: 420px; display: flex; flex-direction: column; overflow: hidden;` dentro de un layout de página `min-height: calc(100vh - 80px)` (o `height: 100vh; overflow: hidden;`), garantizando que la card se extienda hasta el límite inferior del área visible sin dejar huecos vacíos. La tabla interna (`.cartera-table-wrapper`) utiliza `flex: 1; overflow: auto; min-height: 250px;`.
> 3. **Acciones Agrupadas Obligatorias**: En la columna de acciones (`<th>Acciones</th>`), los botones **NUNCA DEBEN ESTAR SUELTOS O SEPARADOS**. Deben presentarse agrupados en un contenedor compacto segmentado de 26px (`.cartera-row-actions-group`) con divisores de 1px entre cada botón (Ver [`../button/icon_action_group.md`](../button/icon_action_group.md)).
> 4. **Tipografía y Colores Neutros (Cero Textos Azules o Verdes Indebidos)**: Los códigos de registro, identificadores y fechas se renderizan en tipografía monospace neutra (`font-mono text-primary` o `text-secondary`). **Queda estrictamente prohibido usar texto verde o azul suelto en datos tabulares ordinarios**. Los colores se reservan exclusivamente para badges de estado semánticos (`OPTIMO`, `EN VIVO`, `CRITICO`).

---

## 2. Código JSX / React 19 Canónico (`DataTable.tsx`)

```tsx
import React, { useState, useRef, useMemo, useEffect } from 'react';
import { 
  Search, 
  X, 
  Filter, 
  FilterX, 
  Columns3, 
  ChevronUp, 
  ChevronDown, 
  FileSpreadsheet, 
  FileText, 
  Loader2,
  Inbox,
  RotateCcw
} from 'lucide-react';
import { ChecklistPopover } from './ChecklistPopover';
import { Pagination } from '../pagination/Pagination';
import { ExportExcelButton } from '../export/ExportExcelButton';
import '../../styles/variables.css';

export interface ColumnDef<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
  sortable?: boolean;
  filterable?: boolean;
  dataType?: 'text' | 'number' | 'date';
  width?: number;
  formatValue?: (val: any) => string;
}

export interface DataTableProps<T extends { id: string | number }> {
  columns: ColumnDef<T>[];
  data: T[];
  totalRows: number;
  currentPage: number;
  pageSize: number;
  isLoading?: boolean;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  onSearchChange: (query: string) => void;
  onFilterChange?: (filters: Record<string, string[]>) => void;
  onSortChange?: (field: string, order: 'ASC' | 'DESC') => void;
  filenameExportPrefix?: string;
  actions?: (row: T) => React.ReactNode;
  onRowClick?: (row: T) => void;
  selectedRowId?: string | number | null;
}

export function DataTable<T extends { id: string | number }>({
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
  filenameExportPrefix = 'Reporte',
  actions,
  onRowClick,
  selectedRowId
}: DataTableProps<T>) {
  // 1. Estados de búsqueda y ordenamiento
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<'ASC' | 'DESC'>('ASC');

  // 2. Filtros de columna tipo Excel
  const [columnFilters, setColumnFilters] = useState<Record<string, string[]>>({});
  const [activeFilterCol, setActiveFilterCol] = useState<string | null>(null);
  const filterPopoverRef = useRef<HTMLDivElement>(null);

  // 3. Visibilidad de columnas
  const [visibleColumns, setVisibleColumns] = useState<string[]>(() => 
    columns.map(c => String(c.key))
  );
  const [isColMenuOpen, setIsColMenuOpen] = useState(false);
  const colMenuRef = useRef<HTMLDivElement>(null);

  // 4. Ancho interactivo de columnas
  const [colWidths, setColWidths] = useState<Record<string, number>>(() => {
    const initial: Record<string, number> = {};
    columns.forEach(c => {
      initial[String(c.key)] = c.width || 150;
    });
    return initial;
  });

  // Cerrar popovers al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (filterPopoverRef.current && !filterPopoverRef.current.contains(e.target as Node)) {
        setActiveFilterCol(null);
      }
      if (colMenuRef.current && !colMenuRef.current.contains(e.target as Node)) {
        setIsColMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Manejo de búsqueda con limpieza
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearchTerm(val);
    onSearchChange(val);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    onSearchChange('');
  };

  // Manejo de filtros por columna
  const handleApplyColumnFilter = (colKey: string, selectedValues: string[]) => {
    const updated = { ...columnFilters };
    if (selectedValues.length === 0) {
      delete updated[colKey];
    } else {
      updated[colKey] = selectedValues;
    }
    setColumnFilters(updated);
    onFilterChange?.(updated);
    setActiveFilterCol(null);
  };

  const handleResetAllFilters = () => {
    setColumnFilters({});
    setSearchTerm('');
    onSearchChange('');
    onFilterChange?.({});
    setActiveFilterCol(null);
  };

  const activeFiltersCount = Object.keys(columnFilters).length + (searchTerm ? 1 : 0);

  // Columnas activas para renderizado
  const renderedColumns = useMemo(() => {
    return columns.filter(c => visibleColumns.includes(String(c.key)));
  }, [columns, visibleColumns]);

  return (
    <div className="joli-datatable-wrapper">
      {/* 1. BARRA DE HERRAMIENTAS CORPORATIVA */}
      <div className="joli-datatable-toolbar">
        <div className="toolbar-left">
          {/* Buscador reactivo */}
          <div className="joli-search-box">
            <Search size={16} className="joli-search-icon" />
            <input 
              type="text" 
              className="joli-search-input" 
              placeholder="Buscar en registros..." 
              value={searchTerm}
              onChange={handleSearch}
            />
            {searchTerm && (
              <button className="joli-search-clear" onClick={handleClearSearch} title="Limpiar búsqueda">
                <X size={14} />
              </button>
            )}
          </div>

          {/* Botón Restablecer Filtros */}
          {activeFiltersCount > 0 && (
            <button 
              type="button" 
              className="joli-btn-reset-filters" 
              onClick={handleResetAllFilters}
              title="Limpiar todos los filtros y búsqueda"
            >
              <FilterX size={14} />
              <span>Limpiar filtros ({activeFiltersCount})</span>
            </button>
          )}
        </div>

        <div className="toolbar-right">
          {/* Selector de Visibilidad de Columnas */}
          <div className="joli-col-visibility-wrapper" ref={colMenuRef}>
            <button 
              type="button" 
              className="joli-btn-secondary"
              onClick={() => setIsColMenuOpen(!isColMenuOpen)}
              title="Configurar columnas visibles"
            >
              <Columns3 size={15} />
              <span>Columnas</span>
            </button>

            {isColMenuOpen && (
              <div className="joli-col-visibility-menu">
                <div className="menu-header">Columnas Visibles</div>
                <div className="menu-body">
                  {columns.map(col => {
                    const keyStr = String(col.key);
                    const isVisible = visibleColumns.includes(keyStr);
                    return (
                      <label key={keyStr} className="col-checkbox-label">
                        <input
                          type="checkbox"
                          checked={isVisible}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setVisibleColumns([...visibleColumns, keyStr]);
                            } else {
                              if (visibleColumns.length > 1) {
                                setVisibleColumns(visibleColumns.filter(k => k !== keyStr));
                              }
                            }
                          }}
                        />
                        <span>{col.header}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Botón de Exportación a Excel */}
          <ExportExcelButton
            filenamePrefix={filenameExportPrefix}
            columns={renderedColumns.map(c => ({
              header: c.header,
              key: c.key,
              formatter: c.formatValue
            }))}
            getData={() => data}
            totalCount={totalRows}
          />
        </div>
      </div>

      {/* 2. TABLA RESPONSIVE CON FILTROS TIPO EXCEL */}
      <div className="table-responsive joli-table-container">
        <table className="table joli-table">
          <thead>
            <tr>
              {renderedColumns.map((col) => {
                const keyStr = String(col.key);
                const isFiltered = Boolean(columnFilters[keyStr] && columnFilters[keyStr].length > 0);
                const isSorted = sortField === keyStr;
                const isOpen = activeFilterCol === keyStr;

                return (
                  <th 
                    key={keyStr} 
                    style={{ width: colWidths[keyStr] || 'auto', minWidth: 120 }}
                    className={isFiltered ? 'th-filtered' : ''}
                  >
                    <div className="th-content-wrapper">
                      {/* Título de columna y trigger de ordenamiento */}
                      <span 
                        className={`th-label ${col.sortable !== false ? 'sortable' : ''}`}
                        onClick={() => {
                          if (col.sortable !== false) {
                            const newOrder = isSorted && sortOrder === 'ASC' ? 'DESC' : 'ASC';
                            setSortField(keyStr);
                            setSortOrder(newOrder);
                            onSortChange?.(keyStr, newOrder);
                          }
                        }}
                      >
                        {col.header}
                        {isSorted && (
                          sortOrder === 'ASC' ? <ChevronUp size={14} className="sort-icon" /> : <ChevronDown size={14} className="sort-icon" />
                        )}
                      </span>

                      {/* Botón de Filtro tipo Excel */}
                      {col.filterable !== false && (
                        <button
                          type="button"
                          className={`th-filter-btn ${isFiltered ? 'active' : ''}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setActiveFilterCol(isOpen ? null : keyStr);
                          }}
                          title={isFiltered ? `Filtro activo (${columnFilters[keyStr].length}): ${col.header}` : `Filtrar por ${col.header}`}
                        >
                          <Filter size={12} />
                          {isFiltered && <span className="th-filter-dot" />}
                        </button>
                      )}
                    </div>

                    {/* Popover Checklist tipo Excel */}
                    {isOpen && (
                      <div className="th-filter-popover-container" ref={filterPopoverRef}>
                        <ChecklistPopover
                          colKey={keyStr}
                          colLabel={col.header}
                          dataType={col.dataType}
                          items={data}
                          activeValues={columnFilters[keyStr]}
                          onApply={(vals) => handleApplyColumnFilter(keyStr, vals)}
                          onSort={(field, order) => {
                            setSortField(field);
                            setSortOrder(order);
                            onSortChange?.(field, order);
                            setActiveFilterCol(null);
                          }}
                          currentSortField={sortField}
                          currentSortOrder={sortOrder}
                          onClose={() => setActiveFilterCol(null)}
                          formatValue={col.formatValue}
                        />
                      </div>
                    )}
                  </th>
                );
              })}
              {actions && <th className="text-end" style={{ width: 100 }}>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={renderedColumns.length + (actions ? 1 : 0)} className="text-center py-5">
                  <Loader2 size={32} className="table-spinner mb-2 text-primary" />
                  <p className="text-muted mb-0 small">Consultando registros...</p>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={renderedColumns.length + (actions ? 1 : 0)} className="text-center py-5">
                  <div className="table-empty-state">
                    <Inbox size={40} className="empty-icon text-muted mb-2" />
                    <h6 className="empty-title">Sin registros encontrados</h6>
                    <p className="empty-desc text-muted">
                      {activeFiltersCount > 0 
                        ? 'No hay registros que coincidan con los filtros aplicados.' 
                        : 'No se encontraron datos disponibles en este módulo.'}
                    </p>
                    {activeFiltersCount > 0 && (
                      <button 
                        type="button" 
                        className="joli-btn-outline btn-sm mt-2"
                        onClick={handleResetAllFilters}
                      >
                        <RotateCcw size={13} className="me-1" />
                        <span>Restablecer Filtros</span>
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ) : (
              data.map((row) => {
                const isSelected = selectedRowId !== undefined && selectedRowId === row.id;
                return (
                  <tr 
                    key={row.id} 
                    className={`${isSelected ? 'row-selected' : ''} ${onRowClick ? 'row-clickable' : ''}`}
                    onClick={() => onRowClick?.(row)}
                  >
                    {renderedColumns.map((col, idx) => (
                      <td key={String(col.key) + idx}>
                        {col.render ? col.render(row) : (
                          col.formatValue ? col.formatValue((row as any)[col.key]) : String((row as any)[col.key] ?? '')
                        )}
                      </td>
                    ))}
                    {actions && (
                      <td className="text-end" onClick={(e) => e.stopPropagation()}>
                        <div className="d-inline-flex gap-1">{actions(row)}</div>
                      </td>
                    )}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* 3. PAGINACIÓN CORPORATIVA INTEGRADA */}
      <Pagination
        currentPage={currentPage}
        totalItems={totalRows}
        pageSize={pageSize}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
        disabled={isLoading}
      />
    </div>
  );
}
```

---

## 3. Estilos CSS Canónicos (Gobernados por `variables.css`)

```css
.joli-datatable-wrapper {
  background-color: var(--color-bg-card, #FFFFFF);
  border: 1px solid var(--color-border, #E5E7EB);
  border-radius: var(--radius-xl, 12px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

[data-theme="dark"] .joli-datatable-wrapper {
  background-color: var(--color-bg-card, #1E293B);
  border-color: var(--color-border, #334155);
}

/* 1. BARRA SUPERIOR */
.joli-datatable-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-bottom: 1px solid var(--color-border, #E5E7EB);
  gap: 12px;
  flex-wrap: wrap;
  background: var(--bg-surface, #FFFFFF);
}

[data-theme="dark"] .joli-datatable-toolbar {
  background: var(--bg-surface, #1E293B);
  border-color: var(--color-border, #334155);
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
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
  color: var(--color-text-muted, #9CA3AF);
  pointer-events: none;
}

.joli-search-input {
  width: 100%;
  height: 36px;
  padding: 0 30px 0 32px;
  background-color: var(--color-bg-input, #F9FAFB);
  border: 1px solid var(--color-border, #D1D5DB);
  border-radius: var(--radius-md, 8px);
  color: var(--color-text-primary, #111827);
  font-size: 13px;
  outline: none;
  transition: all 0.15s ease;
}

[data-theme="dark"] .joli-search-input {
  background-color: var(--color-bg-input, #0F172A);
  border-color: var(--color-border, #334155);
  color: #F8FAFC;
}

.joli-search-input:focus {
  border-color: var(--color-primary, #2D6A4F);
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.15);
  background-color: var(--bg-surface, #FFFFFF);
}

.joli-search-clear {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  color: var(--color-text-muted, #9CA3AF);
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  display: flex;
}

.joli-search-clear:hover {
  color: var(--color-text-primary, #111827);
}

.joli-btn-reset-filters {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 12px;
  font-size: 12.5px;
  font-weight: 600;
  border-radius: var(--radius-md, 8px);
  border: 1px solid #FECACA;
  background: #FEF2F2;
  color: #DC2626;
  cursor: pointer;
  transition: all 0.15s;
}

.joli-btn-reset-filters:hover {
  background: #FEE2E2;
  border-color: #FCA5A5;
}

[data-theme="dark"] .joli-btn-reset-filters {
  background: rgba(220, 38, 38, 0.15);
  border-color: rgba(220, 38, 38, 0.3);
  color: #F87171;
}

/* MENÚ VISIBILIDAD DE COLUMNAS */
.joli-col-visibility-wrapper {
  position: relative;
}

.joli-btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 12px;
  font-size: 12.5px;
  font-weight: 500;
  border-radius: var(--radius-md, 8px);
  border: 1px solid var(--color-border, #D1D5DB);
  background: var(--bg-surface, #FFFFFF);
  color: var(--color-text-secondary, #4B5563);
  cursor: pointer;
  transition: all 0.15s;
}

[data-theme="dark"] .joli-btn-secondary {
  background: var(--bg-surface, #1E293B);
  border-color: #334155;
  color: #CBD5E1;
}

.joli-btn-secondary:hover {
  border-color: var(--color-primary, #2D6A4F);
  color: var(--color-primary, #2D6A4F);
}

.joli-col-visibility-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  z-index: 100;
  width: 220px;
  background: var(--bg-surface, #FFFFFF);
  border: 1px solid var(--color-border, #E5E7EB);
  border-radius: var(--radius-md, 8px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
  padding: 8px 0;
  animation: fadeIn 0.15s ease-out;
}

[data-theme="dark"] .joli-col-visibility-menu {
  background: #1E293B;
  border-color: #334155;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
}

.joli-col-visibility-menu .menu-header {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-muted, #9CA3AF);
  padding: 4px 14px 8px;
  border-bottom: 1px solid var(--color-border, #F3F4F6);
}

.joli-col-visibility-menu .menu-body {
  max-height: 240px;
  overflow-y: auto;
  padding: 4px 8px;
}

.col-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 12.5px;
  color: var(--color-text-primary, #111827);
  cursor: pointer;
}

[data-theme="dark"] .col-checkbox-label {
  color: #F1F5F9;
}

.col-checkbox-label:hover {
  background: var(--color-bg-input, #F3F4F6);
}

[data-theme="dark"] .col-checkbox-label:hover {
  background: #0F172A;
}

/* 2. TABLA RESPONSIVE Y ENCABEZADOS */
.joli-table-container {
  max-height: calc(100vh - 280px);
  overflow-y: auto;
  overflow-x: auto;
  position: relative;
}

.joli-table {
  width: 100%;
  margin-bottom: 0;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
}

.joli-table thead th {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #F8FAFC;
  color: var(--color-text-secondary, #475569);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 10px 14px;
  border-bottom: 2px solid var(--color-border, #E2E8F0);
  white-space: nowrap;
}

[data-theme="dark"] .joli-table thead th {
  background: #0F172A;
  color: #94A3B8;
  border-bottom-color: #334155;
}

.joli-table thead th.th-filtered {
  background: #F0FDF4;
  color: var(--color-primary, #2D6A4F);
}

[data-theme="dark"] .joli-table thead th.th-filtered {
  background: rgba(45, 106, 79, 0.2);
  color: #6EE7B7;
}

.th-content-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.th-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  user-select: none;
}

.th-label.sortable {
  cursor: pointer;
}

.th-label.sortable:hover {
  color: var(--color-primary, #2D6A4F);
}

.th-filter-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-text-muted, #94A3B8);
  cursor: pointer;
  transition: all 0.15s;
}

.th-filter-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--color-text-primary, #0F172A);
}

.th-filter-btn.active {
  background: #E8F5E9;
  border-color: #A7F3D0;
  color: var(--color-primary, #2D6A4F);
}

[data-theme="dark"] .th-filter-btn.active {
  background: rgba(45, 106, 79, 0.3);
  border-color: #2D6A4F;
  color: #6EE7B7;
}

.th-filter-dot {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-primary, #2D6A4F);
}

.th-filter-popover-container {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 50;
  text-transform: none;
  font-weight: normal;
  letter-spacing: normal;
}

/* 3. CUERPO DE LA TABLA Y FILAS */
.joli-table tbody td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-border, #E5E7EB);
  color: var(--color-text-primary, #1F2937);
  vertical-align: middle;
}

[data-theme="dark"] .joli-table tbody td {
  border-bottom-color: #334155;
  color: #F1F5F9;
}

.joli-table tbody tr:hover td {
  background-color: var(--color-bg-card-hover, #F8FAFC);
}

[data-theme="dark"] .joli-table tbody tr:hover td {
  background-color: #243044;
}

.joli-table tbody tr.row-clickable {
  cursor: pointer;
}

.joli-table tbody tr.row-selected td {
  background-color: #ECFDF5 !important;
}

[data-theme="dark"] .joli-table tbody tr.row-selected td {
  background-color: rgba(45, 106, 79, 0.25) !important;
}

/* ESTADO VACÍO */
.table-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.table-empty-state .empty-icon {
  opacity: 0.4;
}

.table-empty-state .empty-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin-bottom: 4px;
}

.table-empty-state .empty-desc {
  font-size: 13px;
  max-width: 360px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
```
