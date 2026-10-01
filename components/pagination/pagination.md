# Especificación de Componente: Paginación Corporativa (Pagination)
## Ecosistema Jolifoods — Guía de Implementación SDD

El componente `Pagination` garantiza la navegación eficiente sobre conjuntos masivos de datos procesados en el backend, evitando la sobrecarga de memoria del navegador y asegurando accesibilidad total (WCAG 2.1 AA).

---

### 1. Requisitos de Negocio, Ubicación y Accesibilidad

> **REGLA DE ORO DE UBICACIÓN (ESTÁNDAR BI/CARTERA)**:  
> En el diseño corporativo Jolifoods, **la paginación NO se ubica al pie o debajo de la tabla**.  
> **SE UBICA OBLIGATORIAMENTE EN LA PARTE DE ARRIBA DE LA TABLA**, integrada directamente en la barra de herramientas superior (`.cartera-table-header-toolbar.pagination-container`).  
> Esto permite que el usuario controle la página, el tamaño de lote y la búsqueda sin tener que desplazarse hasta el fondo de la pantalla.  
> Además, la tarjeta contenedora principal (`.cartera-main-card`) tiene `flex: 1` para **extenderse hasta la parte inferior del viewport visible**, alojando la tabla con scroll interno (`overflow: auto`).

1. **Ubicación Superior en Toolbar**: El contenedor del paginador se coloca arriba de la tabla con `border-bottom: 1px solid var(--border-color)`, agrupando:
   - **Lado Izquierdo**: Selector de filas (`Mostrar [10 v] por página`), buscador en vivo, indicadores de filtros activos, selector de visibilidad de columnas (`Columns3`), botones de acción (exportar, refrescar) y el resumen `Mostrando {inicio} a {fin} de {total} registros`.
   - **Lado Derecho**: Botonera de navegación (`<<`, `<`, números de página con resaltado activo, `>`, `>>`).
2. **Respeto a Paginación Server-Side**: La paginación real se ejecuta en el backend mediante `limit` y `offset` (o `page` y `page_size`), jamás trayendo 50,000 registros al frontend.
3. **Resumen Numérico**: Muestra claramente `Mostrando {inicio} a {fin} de {total} registros` con formateo localizado en español (`1.250`).
4. **Selector de Registros por Página**: Opciones estándar: `10`, `20`, `50`, `100`.
5. **Trunca Inteligente con Elipsis**: Muestra hasta 7 botones interactivos (primera, elipsis, páginas adyacentes, última).
6. **Comportamiento Responsive**: En dispositivos móviles (< 768px), oculta botones numéricos intermedios y muestra únicamente botones `Anterior` / `Siguiente` con el contador compacto `Página X de Y`.

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/Pagination.tsx
import React, { useMemo } from 'react';
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

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 25, 50, 100],
  disabled = false
}) => {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  // Cálculo de botones de página visibles con elipsis
  const visiblePages = useMemo(() => {
    const pages: (number | 'ellipsis')[] = [];
    const maxVisible = 5;

    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('ellipsis');

      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        if (i > 1 && i < totalPages) pages.push(i);
      }

      if (currentPage < totalPages - 2) pages.push('ellipsis');
      pages.push(totalPages);
    }
    return pages;
  }, [currentPage, totalPages]);

  return (
    <nav className="joli-pagination-container" aria-label="Navegación de registros">
      {/* Resumen de Registros */}
      <div className="pagination-summary">
        Mostrando <span className="highlight">{startItem.toLocaleString('es-CO')}</span> a{' '}
        <span className="highlight">{endItem.toLocaleString('es-CO')}</span> de{' '}
        <span className="highlight">{totalItems.toLocaleString('es-CO')}</span> registros
      </div>

      <div className="pagination-controls">
        {/* Selector de tamaño de página */}
        {onPageSizeChange && (
          <div className="pagination-size-selector">
            <span className="size-label">Filas por pág:</span>
            <select
              className="size-select"
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              disabled={disabled}
            >
              {pageSizeOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Botonera de Navegación */}
        <div className="pagination-buttons">
          <button
            className="page-nav-btn"
            onClick={() => onPageChange(1)}
            disabled={currentPage === 1 || disabled}
            title="Primera página"
            aria-label="Ir a la primera página"
          >
            <ChevronsLeft size={16} />
          </button>
          <button
            className="page-nav-btn"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1 || disabled}
            title="Página anterior"
            aria-label="Ir a la página anterior"
          >
            <ChevronLeft size={16} />
          </button>

          {/* Números de Página */}
          <div className="page-numbers-group">
            {visiblePages.map((page, idx) =>
              page === 'ellipsis' ? (
                <span key={`ellipsis-${idx}`} className="page-ellipsis">
                  …
                </span>
              ) : (
                <button
                  key={page}
                  className={`page-num-btn ${currentPage === page ? 'active' : ''}`}
                  onClick={() => onPageChange(page)}
                  disabled={disabled}
                  aria-current={currentPage === page ? 'page' : undefined}
                >
                  {page}
                </button>
              )
            )}
          </div>

          <button
            className="page-nav-btn"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages || disabled}
            title="Página siguiente"
            aria-label="Ir a la página siguiente"
          >
            <ChevronRight size={16} />
          </button>
          <button
            className="page-nav-btn"
            onClick={() => onPageChange(totalPages)}
            disabled={currentPage === totalPages || disabled}
            title="Última página"
            aria-label="Ir a la última página"
          >
            <ChevronsRight size={16} />
          </button>
        </div>
      </div>
    </nav>
  );
};
```

---

### 3. Estilos CSS (`pagination.css`)

```css
/* Toolbar superior con paginador e info ARRIBA de la tabla (Estándar bi/cartera) */
.cartera-table-header-toolbar.pagination-container,
.joli-pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.85rem;
  padding: 0 0 0.85rem 0;
  margin: 0 0 0.85rem 0;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  font-family: inherit;
  font-size: var(--font-size-xs, 0.75rem);
  color: var(--text-secondary, #94a3b8);
}

.pagination-summary .highlight,
.pagination-info span {
  font-weight: 600;
  color: var(--text-primary, #f8fafc);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pagination-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-size-selector .size-label {
  font-size: 12.5px;
  color: var(--text-secondary, #6B7280);
}

.pagination-size-selector .size-select {
  padding: 4px 8px;
  font-size: 12.5px;
  border-radius: var(--radius-sm, 6px);
  border: 1px solid var(--border-default, #D1D5DB);
  background: var(--bg-surface, #FFFFFF);
  color: var(--text-primary, #111827);
  cursor: pointer;
  outline: none;
}

.pagination-size-selector .size-select:focus {
  border-color: var(--color-primary, #2D6A4F);
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
}

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
  min-width: 32px;
  height: 32px;
  padding: 0 6px;
  font-size: 13px;
  font-weight: 500;
  border-radius: var(--radius-sm, 6px);
  border: 1px solid var(--border-default, #E5E7EB);
  background: var(--bg-surface, #FFFFFF);
  color: var(--text-primary, #374151);
  cursor: pointer;
  transition: all 0.15s ease;
}

[data-theme="dark"] .page-nav-btn,
[data-theme="dark"] .page-num-btn {
  background: var(--bg-surface, #1E293B);
  border-color: var(--border-default, #334155);
  color: var(--text-secondary, #E2E8F0);
}

.page-nav-btn:hover:not(:disabled),
.page-num-btn:hover:not(:disabled) {
  background: var(--bg-muted, #F3F4F6);
  border-color: #D1D5DB;
  color: var(--color-primary, #2D6A4F);
}

.page-num-btn.active {
  background: var(--color-primary, #2D6A4F);
  border-color: var(--color-primary, #2D6A4F);
  color: #FFFFFF !important;
  font-weight: 700;
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
  width: 28px;
  height: 32px;
  color: var(--text-muted, #9CA3AF);
  font-size: 14px;
}

@media (max-width: 768px) {
  .page-numbers-group {
    display: none;
  }
  .joli-pagination-container {
    justify-content: center;
  }
}
```
