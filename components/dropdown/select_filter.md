# Componente UI: Selector Desplegable con Búsqueda (`SelectFilter`)
## Spec-Driven Development (SDD)

`SelectFilter` es el selector de las barras de herramientas, formularios y filtros. Reemplaza al `<select>` nativo cuando se necesita búsqueda interna en catálogos extensos (sedes, roles, clientes) y un aspecto coherente con el tema Noche/Día de [`variables.css`](../variables.css).

- **Etiqueta flotante en formularios:** dentro de un formulario de captura (crear o editar), `SelectFilter` DEBE recibir `label` y la prop `flotante`: la etiqueta hace de placeholder y sube al borde, igual que los demás campos ([`../form/floating_field.md`](../form/floating_field.md) §5.4). En **filtros y barras de herramientas NO** se usa `flotante`: conservan la etiqueta encima o el placeholder.
- **Regla:** los selectores de catálogo en formularios y filtros DEBERÍAN usar `SelectFilter`. Un `<select>` nativo PUEDE usarse en controles muy simples (p. ej. filas por página del paginador) siempre que tenga estilos con tokens y etiqueta asociada.
- **Por qué:** búsqueda en listas largas, misma apariencia en todos los navegadores y en ambos temas.

Accesibilidad: patrón *combobox* de WAI-ARIA con `listbox`; navegación con `↑`/`↓`, `Home`/`End`, `Enter` para elegir y `Escape` para cerrar devolviendo el foco al disparador.

---

## 1. Código JSX / React de referencia (`SelectFilter.tsx`)

```tsx
import React, { useEffect, useId, useMemo, useRef, useState } from 'react';
import { Check, ChevronDown, Search } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  badge?: string;
}

export interface SelectFilterProps {
  label?: string;
  /** Formularios de captura: la etiqueta va dentro y sube al borde (form/floating_field.md §5.4). No usar en filtros. */
  flotante?: boolean;
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  withSearch?: boolean;
  disabled?: boolean;
}

export const SelectFilter: React.FC<SelectFilterProps> = ({
  label,
  options,
  value,
  onChange,
  placeholder = 'Seleccione una opción...',
  withSearch = false,
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const baseId = useId();
  const labelId = `${baseId}-label`;
  const listId = `${baseId}-list`;
  const optionId = (index: number) => `${baseId}-opt-${index}`;

  const selectedOption = options.find((o) => o.value === value);

  const filteredOptions = useMemo(() => {
    const q = search.trim().toLowerCase();
    return withSearch && q ? options.filter((o) => o.label.toLowerCase().includes(q)) : options;
  }, [options, search, withSearch]);

  const close = (returnFocus = true) => {
    setIsOpen(false);
    setSearch('');
    if (returnFocus) triggerRef.current?.focus();
  };

  const select = (option: SelectOption) => {
    onChange(option.value);
    close();
  };

  // Al abrir: foco en el buscador (o en la lista) y opción activa = la seleccionada
  useEffect(() => {
    if (!isOpen) return;
    const selectedIndex = filteredOptions.findIndex((o) => o.value === value);
    setActiveIndex(selectedIndex >= 0 ? selectedIndex : 0);
    (withSearch ? searchRef.current : listRef.current)?.focus();

    const onMouseDown = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) close(false);
    };
    document.addEventListener('mousedown', onMouseDown);
    return () => document.removeEventListener('mousedown', onMouseDown);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  // Mantener la opción activa visible
  useEffect(() => {
    if (isOpen && activeIndex >= 0) {
      document.getElementById(optionId(activeIndex))?.scrollIntoView({ block: 'nearest' });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeIndex, isOpen]);

  const onListKeyDown = (e: React.KeyboardEvent) => {
    const last = filteredOptions.length - 1;
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setActiveIndex((i) => Math.min(i + 1, last));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex((i) => Math.max(i - 1, 0));
        break;
      case 'Home':
        e.preventDefault();
        setActiveIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setActiveIndex(last);
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredOptions[activeIndex]) select(filteredOptions[activeIndex]);
        break;
      case 'Escape':
        e.preventDefault();
        close();
        break;
      case 'Tab':
        close(false);
        break;
    }
  };

  const activeDescendant = isOpen && filteredOptions[activeIndex] ? optionId(activeIndex) : undefined;

  return (
    <div className="joli-select-container" ref={containerRef}>
      {label && <span id={labelId} className="joli-select-label">{label}</span>}
      <button
        ref={triggerRef}
        type="button"
        className="joli-select-trigger"
        onClick={() => (isOpen ? close() : setIsOpen(true))}
        onKeyDown={(e) => {
          if (!isOpen && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
            e.preventDefault();
            setIsOpen(true);
          }
        }}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls={isOpen ? listId : undefined}
        aria-labelledby={label ? `${labelId} ${baseId}-value` : undefined}
      >
        <span id={`${baseId}-value`} className={selectedOption ? 'joli-select-value' : 'joli-select-placeholder'}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown size={16} className={`joli-chevron ${isOpen ? 'rotated' : ''}`} aria-hidden="true" />
      </button>

      {isOpen && (
        <div className="joli-select-dropdown">
          {withSearch && (
            <div className="joli-select-search-box">
              <Search size={14} aria-hidden="true" />
              <input
                ref={searchRef}
                type="text"
                role="combobox"
                className="joli-select-search-input"
                placeholder="Filtrar..."
                aria-label={label ? `Filtrar ${label}` : 'Filtrar opciones'}
                aria-controls={listId}
                aria-expanded="true"
                aria-autocomplete="list"
                aria-activedescendant={activeDescendant}
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setActiveIndex(0);
                }}
                onKeyDown={onListKeyDown}
              />
            </div>
          )}
          <ul
            ref={listRef}
            id={listId}
            role="listbox"
            className="joli-select-menu"
            aria-labelledby={label ? labelId : undefined}
            aria-activedescendant={withSearch ? undefined : activeDescendant}
            tabIndex={withSearch ? -1 : 0}
            onKeyDown={withSearch ? undefined : onListKeyDown}
          >
            {filteredOptions.length === 0 ? (
              <li className="joli-select-empty" role="presentation">No hay resultados</li>
            ) : (
              filteredOptions.map((opt, index) => {
                const isSelected = opt.value === value;
                return (
                  <li
                    key={opt.value}
                    id={optionId(index)}
                    role="option"
                    aria-selected={isSelected}
                    className={`joli-select-item ${isSelected ? 'selected' : ''} ${index === activeIndex ? 'active' : ''}`}
                    onMouseEnter={() => setActiveIndex(index)}
                    onMouseDown={(e) => e.preventDefault()} // conserva el foco en el buscador
                    onClick={() => select(opt)}
                  >
                    <span>{opt.label}</span>
                    {opt.badge && <span className="joli-select-badge">{opt.badge}</span>}
                    {isSelected && <Check size={14} className="joli-select-check" aria-hidden="true" />}
                  </li>
                );
              })
            )}
          </ul>
        </div>
      )}
    </div>
  );
};
```

---

## 2. Estilos CSS (`select_filter.css`)

```css
.joli-select-container {
  position: relative;
  min-width: 180px;
}

.joli-select-label {
  display: block;
  margin-bottom: 4px;
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  color: var(--label-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.joli-select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: var(--input-height);
  padding: 0 14px;
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--radius-md);
  color: var(--input-text);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.joli-select-trigger:hover:not(:disabled) {
  border-color: var(--input-border-hover);
}

.joli-select-trigger:focus-visible,
.joli-select-trigger[aria-expanded='true'] {
  outline: none;
  border-color: var(--input-focus-border);
  box-shadow: var(--shadow-input-focus);
}

.joli-select-trigger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.joli-select-value { color: var(--input-text); }
.joli-select-placeholder { color: var(--input-placeholder); }

.joli-chevron {
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

.joli-chevron.rotated {
  transform: rotate(180deg);
}

.joli-select-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: var(--z-popover);
  display: flex;
  flex-direction: column;
  max-height: 260px;
  overflow: hidden;
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-popover);
}

.joli-select-search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-muted);
}

.joli-select-search-input {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: var(--font-size-xs);
}

.joli-select-menu {
  margin: 0;
  padding: 4px 0;
  overflow-y: auto;
  list-style: none;
}

.joli-select-menu:focus {
  outline: none;
}

.joli-select-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  cursor: pointer;
}

.joli-select-item.active {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  box-shadow: inset 2px 0 0 var(--border-focus);
}

.joli-select-item.selected {
  background-color: var(--status-success-bg);
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
}

.joli-select-badge {
  padding: 1px 6px;
  font-size: var(--font-size-2xs);
  color: var(--text-muted);
  background: var(--bg-active);
  border-radius: var(--radius-full);
}

.joli-select-check {
  margin-left: auto;
  color: var(--brand-primary);
}

.joli-select-empty {
  padding: 12px;
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}
```
