# Especificación de Componente: Paginación Corporativa (`Pagination`)
## Guía de implementación SDD

El componente `Pagination` navega conjuntos grandes de datos paginados en el backend, sin cargar todos los registros en el navegador.

---

### 1. Requisitos, ubicación y accesibilidad

#### Regla de ubicación: paginador arriba de la tabla

- **Regla:** el paginador DEBERÍA ubicarse **arriba de la tabla**, integrado en la barra de herramientas superior de [`DataTable`](../data_table/data_table.md) (`.joli-datatable-toolbar`), y no como bloque suelto al pie.
- **Por qué:** el usuario controla página, tamaño de lote y búsqueda sin desplazarse al final; la tabla ocupa el resto de la altura con scroll interno.
- **Excepciones:** tablas embebidas muy cortas (p. ej. dentro de un drawer) o una decisión registrada (ADR).

1. **Contenido de la barra superior:** a la izquierda, buscador y filtros activos; a la derecha, visibilidad de columnas, exportar, resumen `Mostrando {inicio} a {fin} de {total}`, selector de filas por página y botonera (`<<`, `<`, números, `>`, `>>`).
2. **Paginación en servidor:** el backend pagina con `page` y `page_size` (o `limit`/`offset`); el frontend nunca descarga el conjunto completo.
3. **Resumen numérico** con formato local (`1.250`, `es-CO`).
4. **Filas por página:** `10`, `20`, `50`, `100`.
5. **Elipsis:** máximo 7 posiciones (primera, elipsis, adyacentes, última).
6. **Móvil (< 768px):** se ocultan los números y se muestra `Página X de Y` con anterior/siguiente.
7. **Accesibilidad:** `<nav aria-label>`, `aria-current="page"` en la página activa, botones solo-ícono con `aria-label`, selector con etiqueta asociada.

---

### 2. Implementación TypeScript / React (`src/components/ui/Pagination.tsx`)

```tsx
import React, { useId, useMemo } from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

export interface PaginationProps {
  currentPage: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
  onPageSizeChange?: (newPageSize: number) => void;
  pageSizeOptions?: number[];
  disabled?: boolean;
}

type PageSlot = number | 'ellipsis-start' | 'ellipsis-end';

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 20, 50, 100],
  disabled = false,
}) => {
  const sizeSelectId = useId();
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const page = Math.min(Math.max(1, currentPage), totalPages);
  const startItem = totalItems === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, totalItems);
  const fmt = (n: number) => n.toLocaleString('es-CO');

  const slots = useMemo<PageSlot[]>(() => {
    if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1);
    const result: PageSlot[] = [1];
    if (page > 3) result.push('ellipsis-start');
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) result.push(i);
    if (page < totalPages - 2) result.push('ellipsis-end');
    result.push(totalPages);
    return result;
  }, [page, totalPages]);

  const goTo = (target: number) => {
    if (!disabled && target >= 1 && target <= totalPages && target !== page) onPageChange(target);
  };

  return (
    <nav className="joli-pagination-container" aria-label="Paginación de registros">
      <div className="pagination-summary" aria-live="polite">
        Mostrando <span className="highlight">{fmt(startItem)}</span> a{' '}
        <span className="highlight">{fmt(endItem)}</span> de{' '}
        <span className="highlight">{fmt(totalItems)}</span>
      </div>

      {onPageSizeChange && (
        <div className="pagination-size-selector">
          <label htmlFor={sizeSelectId} className="size-label">Mostrar</label>
          <select
            id={sizeSelectId}
            className="size-select"
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            disabled={disabled}
          >
            {pageSizeOptions.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          <span className="size-label" aria-hidden="true">por página</span>
        </div>
      )}

      <div className="pagination-buttons">
        <button type="button" className="page-nav-btn" onClick={() => goTo(1)}
          disabled={page === 1 || disabled} aria-label="Primera página" title="Primera página">
          <ChevronsLeft size={16} aria-hidden="true" />
        </button>
        <button type="button" className="page-nav-btn" onClick={() => goTo(page - 1)}
          disabled={page === 1 || disabled} aria-label="Página anterior" title="Página anterior">
          <ChevronLeft size={16} aria-hidden="true" />
        </button>

        <div className="page-numbers-group">
          {slots.map((slot) =>
            typeof slot === 'number' ? (
              <button
                key={slot}
                type="button"
                className={`page-num-btn ${page === slot ? 'active' : ''}`}
                onClick={() => goTo(slot)}
                disabled={disabled}
                aria-label={`Página ${slot}`}
                aria-current={page === slot ? 'page' : undefined}
              >
                {slot}
              </button>
            ) : (
              <span key={slot} className="page-ellipsis" aria-hidden="true">…</span>
            ),
          )}
        </div>

        <span className="page-compact-indicator">Página {page} de {totalPages}</span>

        <button type="button" className="page-nav-btn" onClick={() => goTo(page + 1)}
          disabled={page === totalPages || disabled} aria-label="Página siguiente" title="Página siguiente">
          <ChevronRight size={16} aria-hidden="true" />
        </button>
        <button type="button" className="page-nav-btn" onClick={() => goTo(totalPages)}
          disabled={page === totalPages || disabled} aria-label="Última página" title="Última página">
          <ChevronsRight size={16} aria-hidden="true" />
        </button>
      </div>
    </nav>
  );
};
```

---

### 3. Estilos CSS (`pagination.css`)

```css
/* Grupo compacto que se inserta en la barra superior de la tabla */
.joli-pagination-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.85rem;
  font-family: inherit;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.pagination-summary .highlight {
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.pagination-size-selector {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination-size-selector .size-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.pagination-size-selector .size-select {
  height: 28px;
  padding: 0 8px;
  font-size: var(--font-size-xs);
  border-radius: var(--radius-sm);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--input-text);
  cursor: pointer;
}

.pagination-size-selector .size-select:focus-visible {
  outline: none;
  border-color: var(--input-focus-border);
  box-shadow: var(--shadow-input-focus);
}

.pagination-buttons,
.page-numbers-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-nav-btn,
.page-num-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 6px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
}

.page-nav-btn:hover:not(:disabled),
.page-num-btn:hover:not(:disabled) {
  background: var(--bg-elevated);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.page-nav-btn:focus-visible,
.page-num-btn:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

.page-num-btn.active {
  background: var(--brand-primary);
  border-color: var(--brand-primary);
  color: var(--text-on-brand);
  font-weight: var(--font-weight-bold);
}

.page-nav-btn:disabled,
.page-num-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-ellipsis {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 28px;
  color: var(--text-muted);
}

.page-compact-indicator {
  display: none;
  padding: 0 6px;
  color: var(--text-secondary);
  white-space: nowrap;
}

@media (max-width: 768px) {
  .page-numbers-group { display: none; }
  .page-compact-indicator { display: inline; }
}
```
