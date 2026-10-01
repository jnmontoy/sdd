# Componente UI: Filtro de Columnas Tipo Excel (Checklist Popover)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)
### Patrón Canónico de Referencia: Módulo BI Cartera

El **Checklist Popover** es el componente de filtrado avanzado por columna para tablas de datos en el ecosistema Jolifoods. Emula el comportamiento interactivo de **Microsoft Excel**, permitiendo a los usuarios buscar valores únicos, seleccionar/deseleccionar mediante casillas de verificación, ordenar la columna y filtrar con un solo clic.

---

## 1. Características Técnicas

1. **Ordenamiento Rápido Integrado**: Botones para ordenar ascendente o descendente (`ASC` / `DESC`) según el tipo de dato (`text`, `number`, `date`).
2. **Buscador en Tiempo Real**: Input con icono de lupa para filtrar rápidamente la lista de valores de la columna.
3. **Casilla "Seleccionar Todo" (Tri-Estado)**:
   - Marcado: Todos los valores visibles seleccionados.
   - Indeterminado (`-`): Algunos valores seleccionados.
   - Desmarcado: Ningún valor seleccionado.
4. **Conteo de Ocurrencias por Valor**: Muestra entre paréntesis cuántas veces aparece cada valor en el conjunto de datos `(count)`.
5. **Botón Rápido "Solo"**: Al pasar el cursor sobre una opción, aparece un botón "Solo" que desmarca todo lo demás y selecciona únicamente esa opción.
6. **Acciones de Filtro**: Botón "Limpiar Filtro" y botón "Aplicar".

---

## 2. Código JSX / React 19 Canónico (`ChecklistPopover.tsx`)

```tsx
import React, { useState, useMemo } from 'react';
import { 
  ArrowUp, 
  ArrowDown, 
  FilterX, 
  Search, 
  X, 
  Check 
} from 'lucide-react';
import '../../styles/variables.css';

export interface ChecklistPopoverProps {
  colKey: string;
  colLabel: string;
  dataType?: 'text' | 'number' | 'date';
  items: any[];
  activeValues: string[] | undefined;
  onApply: (vals: string[] | null) => void;
  onSort: (field: string, order: 'ASC' | 'DESC') => void;
  currentSortField?: string;
  currentSortOrder?: 'ASC' | 'DESC';
  onClose: () => void;
  formatValue?: (val: any) => string;
}

export const ChecklistPopover: React.FC<ChecklistPopoverProps> = ({
  colKey,
  colLabel,
  dataType = 'text',
  items,
  activeValues,
  onApply,
  onSort,
  currentSortField,
  currentSortOrder,
  onClose,
  formatValue
}) => {
  const [search, setSearch] = useState('');

  // 1. Mapeo de frecuencias de valores únicos
  const valueMap = useMemo(() => {
    const map = new Map<string, { label: string; count: number }>();
    items.forEach((item) => {
      const rawVal = item[colKey];
      const strVal = rawVal === null || rawVal === undefined ? '' : String(rawVal);
      if (!map.has(strVal)) {
        const displayLabel = formatValue ? formatValue(rawVal) : strVal === '' ? '(Vacío)' : strVal;
        map.set(strVal, { label: displayLabel, count: 1 });
      } else {
        map.get(strVal)!.count += 1;
      }
    });
    return map;
  }, [items, colKey, formatValue]);

  // 2. Ordenar las opciones
  const sortedEntries = useMemo(() => {
    return Array.from(valueMap.entries()).sort((a, b) => {
      const numA = Number(a[0]);
      const numB = Number(b[0]);
      if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
      return a[1].label.localeCompare(b[1].label, undefined, { numeric: true });
    });
  }, [valueMap]);

  const allKeys = useMemo(() => sortedEntries.map(([val]) => val), [sortedEntries]);

  // 3. Selección local
  const [localSelected, setLocalSelected] = useState<Set<string>>(() => {
    if (activeValues && activeValues.length > 0) {
      return new Set(activeValues);
    }
    return new Set(allKeys);
  });

  // 4. Filtrado por búsqueda
  const filteredEntries = useMemo(() => {
    if (!search.trim()) return sortedEntries;
    const q = search.toLowerCase();
    return sortedEntries.filter(([rawVal, meta]) =>
      meta.label.toLowerCase().includes(q) || rawVal.toLowerCase().includes(q)
    );
  }, [sortedEntries, search]);

  const visibleKeys = useMemo(() => filteredEntries.map(([val]) => val), [filteredEntries]);
  const isAllVisibleSelected = visibleKeys.length > 0 && visibleKeys.every((k) => localSelected.has(k));
  const isSomeVisibleSelected = visibleKeys.some((k) => localSelected.has(k)) && !isAllVisibleSelected;

  const handleToggleSelectAll = (checked: boolean) => {
    setLocalSelected((prev) => {
      const next = new Set(prev);
      if (checked) {
        visibleKeys.forEach((k) => next.add(k));
      } else {
        visibleKeys.forEach((k) => next.delete(k));
      }
      return next;
    });
  };

  const handleToggleItem = (val: string) => {
    setLocalSelected((prev) => {
      const next = new Set(prev);
      if (next.has(val)) next.delete(val);
      else next.add(val);
      return next;
    });
  };

  const handleSelectOnly = (val: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setLocalSelected(new Set([val]));
  };

  const handleApply = () => {
    if (localSelected.size === allKeys.length || localSelected.size === 0) {
      onApply(null);
    } else {
      onApply(Array.from(localSelected));
    }
    onClose();
  };

  const isSortedAsc = currentSortField === colKey && currentSortOrder === 'ASC';
  const isSortedDesc = currentSortField === colKey && currentSortOrder === 'DESC';

  return (
    <div className="joli-excel-popover" onClick={(e) => e.stopPropagation()}>
      {/* 1. SECCIÓN DE ORDENAMIENTO */}
      <div className="joli-popover-sort-section">
        <button
          type="button"
          className={`joli-popover-sort-btn ${isSortedAsc ? 'active' : ''}`}
          onClick={() => onSort(colKey, 'ASC')}
        >
          <ArrowUp size={14} className="text-primary me-2" />
          <span>{dataType === 'number' ? 'Ordenar de Menor a Mayor' : 'Ordenar de A a Z'}</span>
        </button>
        <button
          type="button"
          className={`joli-popover-sort-btn ${isSortedDesc ? 'active' : ''}`}
          onClick={() => onSort(colKey, 'DESC')}
        >
          <ArrowDown size={14} className="text-primary me-2" />
          <span>{dataType === 'number' ? 'Ordenar de Mayor a Menor' : 'Ordenar de Z a A'}</span>
        </button>
      </div>

      <div className="joli-popover-divider" />

      {/* 2. BUSCADOR DE VALORES */}
      <div className="joli-popover-search">
        <Search size={14} className="joli-popover-search-icon" />
        <input
          type="text"
          className="joli-popover-search-input"
          placeholder={`Buscar en ${colLabel}...`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          autoFocus
        />
        {search && (
          <button type="button" className="joli-popover-clear-btn" onClick={() => setSearch('')}>
            <X size={12} />
          </button>
        )}
      </div>

      {/* 3. CASILLA SELECCIONAR TODO */}
      <div className="joli-popover-select-all">
        <label className="joli-popover-checkbox-label">
          <input
            type="checkbox"
            className="joli-checkbox"
            checked={isAllVisibleSelected}
            ref={(input) => {
              if (input) input.indeterminate = isSomeVisibleSelected;
            }}
            onChange={(e) => handleToggleSelectAll(e.target.checked)}
          />
          <span className="fw-semibold">
            {search ? '(Seleccionar todos los resultados)' : '(Seleccionar todo)'}
          </span>
        </label>
      </div>

      {/* 4. LISTA DE VALORES ÚNICOS CON CONTEO */}
      <div className="joli-popover-list">
        {filteredEntries.length === 0 ? (
          <div className="joli-popover-empty">No se encontraron valores</div>
        ) : (
          filteredEntries.map(([rawVal, meta]) => {
            const isChecked = localSelected.has(rawVal);
            return (
              <div key={rawVal} className="joli-popover-item" onClick={() => handleToggleItem(rawVal)}>
                <label className="joli-popover-checkbox-label" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    className="joli-checkbox"
                    checked={isChecked}
                    onChange={() => handleToggleItem(rawVal)}
                  />
                  <span className="joli-popover-text" title={meta.label}>
                    {meta.label}
                  </span>
                </label>
                <div className="d-flex align-items-center gap-2 ms-auto">
                  <span className="joli-popover-count">({meta.count})</span>
                  <button
                    type="button"
                    className="joli-popover-only-btn"
                    onClick={(e) => handleSelectOnly(rawVal, e)}
                  >
                    Solo
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* 5. PIE DE ACCIONES */}
      <div className="joli-popover-footer">
        <button
          type="button"
          className="joli-popover-action-btn text-danger"
          onClick={handleClearFilter}
          title="Restablecer filtro en esta columna"
        >
          <FilterX size={14} className="me-1" />
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
};
```

---

## 3. Estilos CSS Canónicos (`variables.css`)

```css
.joli-excel-popover {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 280px;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  z-index: 1050;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: joliPopoverFadeIn var(--transition-fast) ease-out;
}

.joli-popover-sort-section {
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.joli-popover-sort-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 6px 10px;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.joli-popover-sort-btn:hover {
  background-color: var(--color-bg-card-hover);
  color: var(--color-text-primary);
}

.joli-popover-sort-btn.active {
  background-color: rgba(16, 185, 129, 0.12);
  color: var(--color-primary);
  font-weight: var(--weight-bold);
}

.joli-popover-divider {
  height: 1px;
  background-color: var(--color-border);
}

.joli-popover-search {
  position: relative;
  padding: 8px 10px;
  border-bottom: 1px solid var(--color-border);
}

.joli-popover-search-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
}

.joli-popover-search-input {
  width: 100%;
  height: 32px;
  padding: 0 24px 0 28px;
  background-color: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--text-xs);
  outline: none;
}

.joli-popover-search-input:focus {
  border-color: var(--color-primary);
}

.joli-popover-clear-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
}

.joli-popover-select-all {
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-base);
  font-size: var(--text-xs);
}

.joli-popover-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin: 0;
  flex: 1;
  min-width: 0;
}

.joli-checkbox {
  width: 15px;
  height: 15px;
  accent-color: var(--color-primary);
  cursor: pointer;
}

.joli-popover-list {
  max-height: 180px;
  overflow-y: auto;
  padding: 4px 0;
}

.joli-popover-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 12px;
  font-size: var(--text-xs);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.joli-popover-item:hover {
  background-color: var(--color-bg-card-hover);
}

.joli-popover-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.joli-popover-count {
  font-size: 10px;
  color: var(--color-text-muted);
}

.joli-popover-only-btn {
  display: none;
  padding: 1px 6px;
  font-size: 10px;
  font-weight: 700;
  color: var(--color-primary);
  background-color: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.joli-popover-item:hover .joli-popover-only-btn {
  display: inline-block;
}

.joli-popover-empty {
  padding: 16px;
  text-align: center;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.joli-popover-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-base);
}

.joli-popover-action-btn {
  background: transparent;
  border: none;
  font-size: var(--text-xs);
  cursor: pointer;
  display: flex;
  align-items: center;
}

.joli-popover-cancel-btn {
  padding: 4px 10px;
  font-size: var(--text-xs);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
}

.joli-popover-apply-btn {
  padding: 4px 12px;
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  background-color: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

@keyframes joliPopoverFadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}
```
