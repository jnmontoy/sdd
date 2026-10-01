# Componente UI: Selector Desplegable y Filtros (Select Filter)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

El **Select Filter** es el componente de selección y filtrado institucional utilizado en barras de herramientas, formularios y tablas de datos. 

Sustituye a los `<select>` nativos del navegador por un menú estéticamente coherente con el modo noche/día de [`variables.css`](../variables.css), con soporte de búsqueda interna para catálogos extensos (sedes, roles, clientes).

---

## 1. Código JSX / React 19 Canónico (`SelectFilter.tsx`)

```tsx
import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, Search } from 'lucide-react';
import '../../styles/variables.css';

export interface SelectOption {
  value: string;
  label: string;
  badge?: string;
}

export interface SelectFilterProps {
  label?: string;
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  withSearch?: boolean;
}

export const SelectFilter: React.FC<SelectFilterProps> = ({
  label,
  options,
  value,
  onChange,
  placeholder = 'Seleccione una opción...',
  withSearch = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((o) => o.value === value);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredOptions = withSearch
    ? options.filter((o) => o.label.toLowerCase().includes(search.toLowerCase()))
    : options;

  return (
    <div className="joli-select-container" ref={containerRef}>
      {label && <label className="joli-select-label">{label}</label>}
      <button
        type="button"
        className="joli-select-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <span className={selectedOption ? 'text-primary-emphasis' : 'text-muted'}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown size={16} className={`joli-chevron ${isOpen ? 'rotated' : ''}`} />
      </button>

      {isOpen && (
        <div className="joli-select-dropdown">
          {withSearch && (
            <div className="joli-select-search-box">
              <Search size={14} className="text-muted" />
              <input
                type="text"
                className="joli-select-search-input"
                placeholder="Filtrar..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                autoFocus
              />
            </div>
          )}
          <ul className="joli-select-menu">
            {filteredOptions.length === 0 ? (
              <li className="joli-select-empty">No hay resultados</li>
            ) : (
              filteredOptions.map((opt) => (
                <li
                  key={opt.value}
                  className={`joli-select-item ${opt.value === value ? 'selected' : ''}`}
                  onClick={() => {
                    onChange(opt.value);
                    setIsOpen(false);
                  }}
                >
                  <span>{opt.label}</span>
                  {opt.value === value && <Check size={14} className="text-primary ms-auto" />}
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
};
```

---

## 2. Estilos CSS Canónicos (`variables.css`)

```css
.joli-select-container {
  position: relative;
  min-width: 180px;
}

.joli-select-label {
  display: block;
  font-size: 11px;
  font-weight: var(--weight-bold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.joli-select-trigger {
  width: 100%;
  height: 40px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  outline: none;
  transition: all var(--transition-fast);
}

.joli-select-trigger:focus,
.joli-select-trigger[aria-expanded='true'] {
  border-color: var(--color-primary);
  box-shadow: var(--focus-ring);
}

.joli-chevron {
  color: var(--color-text-muted);
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
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  z-index: 1000;
  max-height: 240px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.joli-select-search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border);
}

.joli-select-search-input {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: var(--text-xs);
  outline: none;
}

.joli-select-menu {
  list-style: none;
  margin: 0;
  padding: 4px 0;
  overflow-y: auto;
}

.joli-select-item {
  display: flex;
  align-items: center;
  padding: 8px 14px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.joli-select-item:hover {
  background-color: var(--color-bg-card-hover);
  color: var(--color-text-primary);
}

.joli-select-item.selected {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-primary);
  font-weight: var(--weight-semibold);
}

.joli-select-empty {
  padding: 12px;
  text-align: center;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
```
