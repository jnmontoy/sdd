# Componente UI: Selector Desplegable con Búsqueda (`SelectFilter`)
## Spec-Driven Development (SDD)

`SelectFilter` es el selector de las barras de herramientas, formularios y filtros. Reemplaza al `<select>` nativo cuando se necesita búsqueda interna en catálogos extensos (sedes, roles, clientes) y un aspecto coherente con el tema Noche/Día de [`variables.css`](../variables.css).

- **Etiqueta flotante en formularios:** dentro de un formulario de captura (crear o editar), `SelectFilter` DEBE recibir `label` y la prop `flotante`: la etiqueta hace de placeholder y sube al borde, igual que los demás campos ([`../form/floating_field.md`](../form/floating_field.md) §5.4). En **filtros y barras de herramientas NO** se usa `flotante`: conservan la etiqueta encima o el placeholder.
- **Regla:** los selectores de catálogo en formularios y filtros DEBERÍAN usar `SelectFilter`. Un `<select>` nativo PUEDE usarse en controles muy simples (p. ej. filas por página del paginador) siempre que tenga estilos con tokens y etiqueta asociada.
- **Por qué:** búsqueda en listas largas, misma apariencia en todos los navegadores y en ambos temas.

Accesibilidad: patrón *combobox* de WAI-ARIA con `listbox`; navegación con `↑`/`↓`, `Home`/`End`, `Enter` para elegir y `Escape` para cerrar devolviendo el foco al disparador.

### Buscador interno

- **Umbral (DEBE):** con **10 opciones o más** (`MIN_OPCIONES_CON_BUSCADOR`) la lista lleva un campo de búsqueda arriba; con menos, no. Es el valor por defecto (`withSearch="auto"`). `withSearch={true|false}` fuerza el comportamiento solo con una razón registrada.
- Al abrir, el foco pasa al campo, con el texto guía «Buscar en (etiqueta)…». Escribir una letra con el disparador enfocado y la lista cerrada la abre con esa letra ya escrita.
- **Filtra** por cualquier parte de la etiqueta, **sin distinguir mayúsculas ni tildes** («calidad» encuentra «Calidad», «garcia» encuentra «García», «pena» encuentra «Peña»). Las opciones conservan su orden original.
- **Sin coincidencias:** «Ninguna opción contiene «texto».», anunciado al lector de pantalla (`role="status"`).

### Teclado

| Tecla | Lista sin buscador | Lista con buscador (foco en el campo) |
| :--- | :--- | :--- |
| `↑` / `↓` | Recorren las opciones, sin dar la vuelta | Recorren solo las filtradas |
| `Home` / `End` | Primera / última opción | Mueven el cursor del texto |
| `Enter` | Elige la activa | Elige la activa |
| `Escape` | Cierra | Limpia la búsqueda; si ya está vacía, cierra |
| `Tab` | Cierra y sigue al siguiente control | Cierra y sigue al siguiente control |

Al elegir o cerrar con teclado, el foco vuelve al disparador. `Escape` no debe cerrar también el modal o panel que contiene el selector.

### Celular (hasta 768 px)

- **Sin buscador:** PUEDE usarse el `<select>` nativo del teléfono, con estilos de tokens.
- **Con buscador:** panel a lo ancho, arriba del área visible. Su alto sigue al área que de verdad se ve (`window.visualViewport`), para que el teclado virtual no tape las opciones. No se cierra al desplazar ni al cambiar el tamaño (el teclado provoca las dos cosas); se cierra al elegir, con `Escape` o al tocar fuera.
- **El campo de búsqueda NUNCA mide menos de 16 px** de letra: con menos, el teléfono hace zoom al enfocarlo.

### Colores

Solo tokens de [`variables.css`](../variables.css). La opción elegida se marca con fondo neutro (`--bg-active`) y el ícono de check con el color de marca (`--brand-primary`): así hereda la marca de cada proyecto. **No** usar colores de estado (`--status-success-*`, `--status-error-*`) para marcar la selección: elegir una opción no es un éxito ni un error.

**Procedencia:** comportamiento probado en Fichas técnicas de materias primas (noviembre de 2026).

---

## 1. Código JSX / React de referencia (`SelectFilter.tsx`)

```tsx
import React, { useEffect, useId, useMemo, useRef, useState } from 'react';
import { Check, ChevronDown, Search } from 'lucide-react';

/** Con esta cantidad de opciones o más, la lista lleva buscador. */
export const MIN_OPCIONES_CON_BUSCADOR = 10;

/** Minúsculas y sin tildes: «García» -> «garcia», «Peña» -> «pena». */
const normalizar = (texto: string) =>
  texto.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

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
  /** 'auto' (por defecto): buscador con MIN_OPCIONES_CON_BUSCADOR opciones o más. */
  withSearch?: boolean | 'auto';
  disabled?: boolean;
}

export const SelectFilter: React.FC<SelectFilterProps> = ({
  label,
  options,
  value,
  onChange,
  placeholder = 'Seleccione una opción...',
  withSearch = 'auto',
  disabled = false,
}) => {
  const conBuscador = withSearch === 'auto' ? options.length >= MIN_OPCIONES_CON_BUSCADOR : withSearch;
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
    const q = normalizar(search.trim());
    return conBuscador && q ? options.filter((o) => normalizar(o.label).includes(q)) : options;
  }, [options, search, conBuscador]);

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
    (conBuscador ? searchRef.current : listRef.current)?.focus();

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
        e.stopPropagation(); // no cerrar el modal o panel de fondo
        if (conBuscador && search) {
          setSearch('');
          setActiveIndex(0);
        } else {
          close();
        }
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
          if (isOpen) return;
          if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            setIsOpen(true);
          } else if (conBuscador && e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
            // Escribir sobre el disparador abre la lista con esa letra ya escrita
            e.preventDefault();
            setSearch(e.key);
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
          {conBuscador && (
            <div className="joli-select-search-box">
              <Search size={14} aria-hidden="true" />
              <input
                ref={searchRef}
                type="text"
                role="combobox"
                className="joli-select-search-input"
                placeholder={label ? `Buscar en ${label.toLowerCase()}…` : 'Buscar…'}
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
            aria-activedescendant={conBuscador ? undefined : activeDescendant}
            tabIndex={conBuscador ? -1 : 0}
            onKeyDown={conBuscador ? undefined : onListKeyDown}
          >
            {filteredOptions.length === 0 ? (
              <li className="joli-select-empty" role="presentation">
                <span role="status">Ninguna opción contiene «{search.trim()}».</span>
              </li>
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

/* Selección con fondo neutro; la marca la pone el check (no usar colores de estado) */
.joli-select-item.selected {
  background-color: var(--bg-active);
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

@media (max-width: 768px) {
  /* Con menos de 16 px el teléfono hace zoom al enfocar el campo */
  .joli-select-search-input {
    font-size: var(--font-size-base);
  }
}
```
