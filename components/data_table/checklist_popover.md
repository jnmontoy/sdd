# Componente UI: Filtro de Columnas Tipo Excel (`ChecklistPopover`)
## Spec-Driven Development (SDD)

> **Origen:** patrón tomado de bi (módulo de cartera). Aquí se describe de forma genérica.

El **Checklist Popover** es el filtro avanzado por columna de [`DataTable`](./data_table.md). Emula el filtro de Microsoft Excel: buscar valores únicos, marcar/desmarcar con casillas, ordenar la columna y quedarse con un solo valor con un clic.

---

## 0. Implementación de referencia (Pandora, módulo Usuarios)

> Patrón completo de la pantalla: [`admin_table_screen.md`](../data_table/admin_table_screen.md). Lo de esta sección manda sobre el resto del documento cuando se contradicen; lo marcado **«Deuda en la referencia»** es lo que el código aún no cumple y NO se copia.

- Firma real: `<ChecklistPopover colKey colLabel dataType items getValue activeValues onApply onSort currentSortField currentSortOrder onClose />`. Los valores salen de `getValue(item)` sobre **todas** las filas en memoria (no hay prop `options` del servidor). `onApply(null)` = sin filtro.
- Se abre desde `button.th-filter-btn` del encabezado (ícono `Filter` 12 px + punto `.th-filter-dot` si hay filtro; `active` si hay filtro o está abierto) dentro de `div.th-filter-popover-container`; se cierra con clic fuera. Por defecto **toda columna es filtrable** salvo `filterable: false`.
- Medidas: menú de 270 px, lista de máximo 185 px, `z-index` 1100; encabezado filtrado `.th-filtered` con `rgba(brand, .12)`.
- **Deuda en la referencia:** sin `role="dialog"` ni `Escape`; lista con `div` (no `ul`/`li`); el botón «Solo» solo aparece con el mouse (invisible al foco de teclado); textos de orden para fechas genéricos («A a Z»). Lo correcto es lo del resto de este documento.

---

## 1. Características

1. **Ordenamiento integrado:** ascendente / descendente (`ASC` / `DESC`) con textos según el tipo de dato (`text`, `number`, `date`).
2. **Buscador de valores** dentro de la lista.
3. **"Seleccionar todo" tri-estado:** marcado (todos los visibles), indeterminado (algunos), desmarcado (ninguno).
4. **Conteo de ocurrencias** por valor `(count)`.
5. **Botón "Solo":** deja seleccionado únicamente ese valor. Visible al pasar el cursor **o al enfocar la fila con teclado**.
6. **Acciones:** "Limpiar" (quita el filtro de la columna), "Cancelar" y "Aplicar". `Escape` cierra sin aplicar.

### Origen de los valores (importante con paginación en servidor)

- Si la tabla pagina en el servidor, `items` solo contiene la página actual y los valores/conteos serían **incompletos**. En ese caso la vista DEBERÍA pasar `options` con los valores distintos y sus conteos calculados por el backend (p. ej. `GET /api/v1/<recurso>/valores-filtro/?columna=estado`).
- Si la tabla tiene todos los datos en memoria, PUEDE omitirse `options` y se derivan de `items`.

---

## 2. Código JSX / React de referencia (`ChecklistPopover.tsx`)

```tsx
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { ArrowDown, ArrowUp, FilterX, Search, X } from 'lucide-react';

export interface ChecklistOption {
  value: string;
  label: string;
  count: number;
}

export interface ChecklistPopoverProps<T> {
  colKey: string;
  colLabel: string;
  dataType?: 'text' | 'number' | 'date';
  /** Filas disponibles en memoria (se usan si no llegan `options`). */
  items?: T[];
  /** Valores distintos calculados por el servidor (recomendado con paginación en servidor). */
  options?: ChecklistOption[];
  activeValues: string[] | undefined;
  /** Lista vacía = sin filtro en esta columna. */
  onApply: (values: string[]) => void;
  onSort: (field: string, order: 'ASC' | 'DESC') => void;
  currentSortField?: string;
  currentSortOrder?: 'ASC' | 'DESC';
  onClose: () => void;
  formatValue?: (value: unknown) => string;
}

function deriveOptions<T>(
  items: T[],
  colKey: string,
  formatValue?: (value: unknown) => string,
): ChecklistOption[] {
  const map = new Map<string, ChecklistOption>();
  for (const item of items) {
    const raw = (item as Record<string, unknown>)[colKey];
    const value = raw === null || raw === undefined ? '' : String(raw);
    const existing = map.get(value);
    if (existing) {
      existing.count += 1;
    } else {
      const label = formatValue ? formatValue(raw) : value === '' ? '(Vacío)' : value;
      map.set(value, { value, label, count: 1 });
    }
  }
  return Array.from(map.values());
}

export function ChecklistPopover<T>({
  colKey,
  colLabel,
  dataType = 'text',
  items = [],
  options,
  activeValues,
  onApply,
  onSort,
  currentSortField,
  currentSortOrder,
  onClose,
  formatValue,
}: ChecklistPopoverProps<T>) {
  const [search, setSearch] = useState('');
  const searchRef = useRef<HTMLInputElement>(null);
  const selectAllRef = useRef<HTMLInputElement>(null);

  // 1. Opciones únicas ordenadas
  const sortedOptions = useMemo(() => {
    const base = options ?? deriveOptions(items, colKey, formatValue);
    return [...base].sort((a, b) => {
      const numA = Number(a.value);
      const numB = Number(b.value);
      if (a.value !== '' && b.value !== '' && !Number.isNaN(numA) && !Number.isNaN(numB)) return numA - numB;
      return a.label.localeCompare(b.label, 'es', { numeric: true });
    });
  }, [options, items, colKey, formatValue]);

  const allValues = useMemo(() => sortedOptions.map((o) => o.value), [sortedOptions]);

  // 2. Selección local (se confirma con "Aplicar")
  const [selected, setSelected] = useState<Set<string>>(
    () => new Set(activeValues && activeValues.length > 0 ? activeValues : allValues),
  );

  // 3. Filtrado por búsqueda
  const visibleOptions = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return sortedOptions;
    return sortedOptions.filter((o) => o.label.toLowerCase().includes(q) || o.value.toLowerCase().includes(q));
  }, [sortedOptions, search]);

  const visibleValues = visibleOptions.map((o) => o.value);
  const allVisibleSelected = visibleValues.length > 0 && visibleValues.every((v) => selected.has(v));
  const someVisibleSelected = !allVisibleSelected && visibleValues.some((v) => selected.has(v));

  useEffect(() => {
    if (selectAllRef.current) selectAllRef.current.indeterminate = someVisibleSelected;
  }, [someVisibleSelected]);

  // 4. Foco inicial y cierre con Escape
  useEffect(() => {
    searchRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [onClose]);

  const toggleAllVisible = (checked: boolean) => {
    setSelected((prev) => {
      const next = new Set(prev);
      visibleValues.forEach((v) => (checked ? next.add(v) : next.delete(v)));
      return next;
    });
  };

  const toggleValue = (value: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(value)) next.delete(value);
      else next.add(value);
      return next;
    });
  };

  const handleApply = () => {
    // Todo o nada seleccionado equivale a "sin filtro"
    const isNoFilter = selected.size === 0 || selected.size === allValues.length;
    onApply(isNoFilter ? [] : Array.from(selected));
    onClose();
  };

  const handleClearFilter = () => {
    onApply([]);
    onClose();
  };

  const isSortedAsc = currentSortField === colKey && currentSortOrder === 'ASC';
  const isSortedDesc = currentSortField === colKey && currentSortOrder === 'DESC';
  const ascLabel = dataType === 'number' ? 'Ordenar de menor a mayor' : dataType === 'date' ? 'Ordenar de más antiguo a más reciente' : 'Ordenar de A a Z';
  const descLabel = dataType === 'number' ? 'Ordenar de mayor a menor' : dataType === 'date' ? 'Ordenar de más reciente a más antiguo' : 'Ordenar de Z a A';

  return (
    <div
      className="joli-excel-popover"
      role="dialog"
      aria-label={`Filtro de ${colLabel}`}
      onClick={(e) => e.stopPropagation()}
    >
      {/* 1. Ordenamiento */}
      <div className="joli-popover-sort-section">
        <button
          type="button"
          className={`joli-popover-sort-btn ${isSortedAsc ? 'active' : ''}`}
          aria-pressed={isSortedAsc}
          onClick={() => onSort(colKey, 'ASC')}
        >
          <ArrowUp size={14} className="me-2" aria-hidden="true" />
          <span>{ascLabel}</span>
        </button>
        <button
          type="button"
          className={`joli-popover-sort-btn ${isSortedDesc ? 'active' : ''}`}
          aria-pressed={isSortedDesc}
          onClick={() => onSort(colKey, 'DESC')}
        >
          <ArrowDown size={14} className="me-2" aria-hidden="true" />
          <span>{descLabel}</span>
        </button>
      </div>

      <div className="joli-popover-divider" />

      {/* 2. Buscador */}
      <div className="joli-popover-search">
        <Search size={14} className="joli-popover-search-icon" aria-hidden="true" />
        <input
          ref={searchRef}
          type="search"
          className="joli-popover-search-input"
          placeholder={`Buscar en ${colLabel}...`}
          aria-label={`Buscar valores de ${colLabel}`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {search && (
          <button
            type="button"
            className="joli-popover-clear-btn"
            onClick={() => setSearch('')}
            aria-label="Limpiar búsqueda"
          >
            <X size={12} aria-hidden="true" />
          </button>
        )}
      </div>

      {/* 3. Seleccionar todo */}
      <div className="joli-popover-select-all">
        <label className="joli-popover-checkbox-label">
          <input
            ref={selectAllRef}
            type="checkbox"
            className="joli-checkbox"
            checked={allVisibleSelected}
            onChange={(e) => toggleAllVisible(e.target.checked)}
          />
          <span className="fw-semibold">
            {search ? '(Seleccionar todos los resultados)' : '(Seleccionar todo)'}
          </span>
        </label>
      </div>

      {/* 4. Valores únicos con conteo */}
      <ul className="joli-popover-list" aria-label={`Valores de ${colLabel}`}>
        {visibleOptions.length === 0 ? (
          <li className="joli-popover-empty">No se encontraron valores</li>
        ) : (
          visibleOptions.map((option) => (
            <li key={option.value} className="joli-popover-item">
              <label className="joli-popover-checkbox-label">
                <input
                  type="checkbox"
                  className="joli-checkbox"
                  checked={selected.has(option.value)}
                  onChange={() => toggleValue(option.value)}
                />
                <span className="joli-popover-text" title={option.label}>{option.label}</span>
              </label>
              <span className="joli-popover-count" aria-label={`${option.count} registros`}>
                ({option.count})
              </span>
              <button
                type="button"
                className="joli-popover-only-btn"
                onClick={() => setSelected(new Set([option.value]))}
                aria-label={`Seleccionar solo ${option.label}`}
              >
                Solo
              </button>
            </li>
          ))
        )}
      </ul>

      {/* 5. Acciones */}
      <div className="joli-popover-footer">
        <button type="button" className="joli-popover-action-btn" onClick={handleClearFilter}>
          <FilterX size={14} className="me-1" aria-hidden="true" />
          <span>Limpiar</span>
        </button>
        <div className="d-flex gap-2">
          <button type="button" className="joli-popover-cancel-btn" onClick={onClose}>
            Cancelar
          </button>
          <button type="button" className="joli-popover-apply-btn" onClick={handleApply}>
            Aplicar
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 3. Estilos CSS (`checklist_popover.css`)

La posición la da el contenedor `.th-filter-popover-container` de `DataTable`; el popover no se posiciona por sí mismo.

```css
.joli-excel-popover {
  width: 280px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-popover);
  animation: joliPopoverFadeIn var(--transition-fast);
}

.joli-popover-sort-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px;
}

.joli-popover-sort-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 6px 10px;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.joli-popover-sort-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.joli-popover-sort-btn.active {
  background-color: var(--status-success-bg);
  color: var(--brand-primary);
  font-weight: var(--font-weight-bold);
}

.joli-popover-divider {
  height: 1px;
  background-color: var(--border-subtle);
}

.joli-popover-search {
  position: relative;
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-subtle);
}

.joli-popover-search-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.joli-popover-search-input {
  width: 100%;
  height: 32px;
  padding: 0 24px 0 28px;
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-xs);
}

.joli-popover-search-input:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: var(--shadow-input-focus);
}

.joli-popover-clear-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.joli-popover-select-all {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-subtle);
  background-color: var(--bg-elevated);
  font-size: var(--font-size-xs);
  color: var(--text-primary);
}

.joli-popover-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  margin: 0;
  cursor: pointer;
}

.joli-checkbox {
  width: 15px;
  height: 15px;
  accent-color: var(--brand-primary);
  cursor: pointer;
}

.joli-popover-list {
  max-height: 180px;
  margin: 0;
  padding: 4px 0;
  overflow-y: auto;
  list-style: none;
}

.joli-popover-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px;
  font-size: var(--font-size-xs);
  color: var(--text-primary);
  transition: background-color var(--transition-fast);
}

.joli-popover-item:hover,
.joli-popover-item:focus-within {
  background-color: var(--bg-hover);
}

.joli-popover-text {
  max-width: 140px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.joli-popover-count {
  margin-left: auto;
  font-size: var(--font-size-2xs);
  color: var(--text-muted);
}

/* Oculto visualmente pero accesible: aparece con hover o foco de teclado */
.joli-popover-only-btn {
  opacity: 0;
  padding: 1px 6px;
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  color: var(--brand-primary);
  background-color: var(--status-success-bg);
  border: 1px solid var(--border-card-accent);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.joli-popover-item:hover .joli-popover-only-btn,
.joli-popover-item:focus-within .joli-popover-only-btn {
  opacity: 1;
}

.joli-popover-empty {
  padding: 16px;
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.joli-popover-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-elevated);
}

.joli-popover-action-btn {
  display: flex;
  align-items: center;
  background: transparent;
  border: none;
  font-size: var(--font-size-xs);
  color: var(--status-error);
  cursor: pointer;
}

.joli-popover-cancel-btn {
  padding: 4px 10px;
  font-size: var(--font-size-xs);
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
}

.joli-popover-apply-btn {
  padding: 4px 12px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  background-color: var(--brand-primary);
  color: var(--text-on-brand);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.joli-excel-popover button:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

@keyframes joliPopoverFadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}
```
