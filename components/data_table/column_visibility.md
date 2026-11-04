# Componente UI: Selector de Visibilidad de Columnas (`ColumnVisibilityDropdown`)
## Spec-Driven Development (SDD)

El **Selector de Visibilidad de Columnas** permite mostrar u ocultar columnas de la tabla con un menú desplegable de casillas, mantiene al menos una columna visible y recuerda la configuración del usuario.

---

## 1. Características

1. **Botón disparador** con icono `Columns3`, etiqueta "Columnas", contador `{visibles}/{totales}` y flecha que rota al abrir. Expone `aria-expanded` y `aria-controls`.
2. **Encabezado del menú** con "Todas" (activa todas) y "Restablecer" (vuelve a las columnas por defecto).
3. **Una casilla por columna**, con su etiqueta asociada.
4. **Mínimo una columna visible:** si solo queda una, su casilla se deshabilita.
5. **Persistencia** con `STORAGE_KEYS.visibleColumns(modulo)` mediante el hook `useVisibleColumns`; el componente visual no toca `localStorage`.
6. **Cierre** con clic fuera o `Escape` (el foco vuelve al botón).

---

## 2. Hook de estado persistido (`src/hooks/useVisibleColumns.ts`)

```tsx
import { useCallback, useState } from 'react';
import { STORAGE_KEYS, safeStorage } from '../config/storageKeys';

export function useVisibleColumns(modulo: string, allKeys: string[], defaultKeys: string[] = allKeys) {
  const storageKey = STORAGE_KEYS.visibleColumns(modulo);

  const [visibleColumns, setVisibleState] = useState<string[]>(() => {
    try {
      const saved = JSON.parse(safeStorage.get(storageKey) ?? 'null') as unknown;
      if (Array.isArray(saved)) {
        const valid = saved.filter((k): k is string => typeof k === 'string' && allKeys.includes(k));
        if (valid.length > 0) return valid;
      }
    } catch {
      /* valor corrupto: se usan los valores por defecto */
    }
    return defaultKeys;
  });

  const setVisibleColumns = useCallback(
    (keys: string[]) => {
      setVisibleState(keys);
      safeStorage.set(storageKey, JSON.stringify(keys));
    },
    [storageKey],
  );

  const resetVisibleColumns = useCallback(() => setVisibleColumns(defaultKeys), [defaultKeys, setVisibleColumns]);

  return { visibleColumns, setVisibleColumns, resetVisibleColumns };
}
```

---

## 3. Componente de referencia (`ColumnVisibilityDropdown.tsx`)

```tsx
import React, { useEffect, useId, useRef, useState } from 'react';
import { ChevronDown, Columns3 } from 'lucide-react';

export interface ColumnDefinition {
  key: string;
  label: string;
}

export interface ColumnVisibilityProps {
  columns: ColumnDefinition[];
  visibleColumns: string[];
  onChange: (visibleKeys: string[]) => void;
  onResetDefault: () => void;
}

export const ColumnVisibilityDropdown: React.FC<ColumnVisibilityProps> = ({
  columns,
  visibleColumns,
  onChange,
  onResetDefault,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const menuId = useId();

  useEffect(() => {
    if (!isOpen) return;
    const onMouseDown = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setIsOpen(false);
    };
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
        triggerRef.current?.focus();
      }
    };
    document.addEventListener('mousedown', onMouseDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onMouseDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [isOpen]);

  const toggleColumn = (key: string) => {
    if (visibleColumns.includes(key)) {
      if (visibleColumns.length <= 1) return; // mínimo 1 visible
      onChange(visibleColumns.filter((k) => k !== key));
    } else {
      // Conserva el orden original de las columnas
      onChange(columns.map((c) => c.key).filter((k) => k === key || visibleColumns.includes(k)));
    }
  };

  return (
    <div className="col-visibility-wrapper" ref={containerRef}>
      <button
        ref={triggerRef}
        type="button"
        className={`col-visibility-btn ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-controls={menuId}
        title="Configurar columnas visibles"
      >
        <Columns3 size={14} aria-hidden="true" />
        <span>Columnas</span>
        <span className="col-btn-badge" aria-label={`${visibleColumns.length} de ${columns.length} visibles`}>
          {visibleColumns.length}/{columns.length}
        </span>
        <ChevronDown size={13} className={`col-btn-chevron ${isOpen ? 'is-rotated' : ''}`} aria-hidden="true" />
      </button>

      {isOpen && (
        <div id={menuId} className="col-visibility-popover" role="group" aria-label="Columnas visibles">
          <div className="col-visibility-header">
            <span>Columnas visibles</span>
            <div className="header-actions">
              <button type="button" className="link-btn" onClick={() => onChange(columns.map((c) => c.key))}>
                Todas
              </button>
              <span aria-hidden="true">•</span>
              <button type="button" className="link-btn" onClick={onResetDefault}>
                Restablecer
              </button>
            </div>
          </div>
          <div className="col-visibility-list">
            {columns.map((col) => {
              const isChecked = visibleColumns.includes(col.key);
              return (
                <label key={col.key} className="col-visibility-item">
                  <input
                    type="checkbox"
                    className="joli-checkbox"
                    checked={isChecked}
                    onChange={() => toggleColumn(col.key)}
                    disabled={isChecked && visibleColumns.length <= 1}
                  />
                  <span>{col.label}</span>
                </label>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
```

Uso:

```tsx
const { visibleColumns, setVisibleColumns, resetVisibleColumns } =
  useVisibleColumns('cartera', columns.map((c) => c.key));

<ColumnVisibilityDropdown
  columns={columns.map((c) => ({ key: c.key, label: c.header }))}
  visibleColumns={visibleColumns}
  onChange={setVisibleColumns}
  onResetDefault={resetVisibleColumns}
/>
```

---

## 4. Estilos CSS

```css
.col-visibility-wrapper {
  position: relative;
  display: inline-block;
}

.col-visibility-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 10px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
}

.col-visibility-btn:hover,
.col-visibility-btn.active {
  color: var(--text-primary);
  border-color: var(--brand-primary);
  background-color: var(--bg-hover);
}

.col-visibility-btn:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

.col-btn-badge {
  padding: 1px 5px;
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-semibold);
  background-color: var(--bg-active);
  border-radius: var(--radius-full);
}

.col-btn-chevron {
  transition: transform var(--transition-fast);
}

.col-btn-chevron.is-rotated {
  transform: rotate(180deg);
}

.col-visibility-popover {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  z-index: var(--z-popover);
  width: 220px;
  overflow: hidden;
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-popover);
}

.col-visibility-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.col-visibility-header .link-btn {
  padding: 0;
  background: none;
  border: none;
  color: var(--brand-primary);
  font-size: var(--font-size-2xs);
  cursor: pointer;
}

.col-visibility-list {
  max-height: 240px;
  overflow-y: auto;
  padding: 6px 0;
}

.col-visibility-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  font-size: var(--font-size-xs);
  color: var(--text-primary);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.col-visibility-item:hover,
.col-visibility-item:focus-within {
  background-color: var(--bg-hover);
}
```
