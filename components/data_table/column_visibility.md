# Componente UI: Selector de Visibilidad de Columnas (Column Visibility)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)
### Patrón Canónico de Referencia: Módulo BI Cartera (`cartera-col-visibility-wrapper` / `Columns3`)

El **Selector de Visibilidad de Columnas** permite a los usuarios mostrar u ocultar columnas de la tabla de datos mediante un menú emergente desplegable con casillas de verificación, protegiendo al menos una columna obligatoria activa y persistiendo la configuración del usuario.

---

## 1. Características Técnicas

1. **Botón Disparador con Badge de Conteo**: Icono `Columns3`, etiqueta "Columnas", badge numérico dinámico `{visibles}/{totales}` y flecha indicadora de apertura rotatoria (`ChevronDown`).
2. **Menú Desplegable con Encabezado Rápido**:
   - Enlace "Todas" para activar todas las columnas disponibles con un solo clic.
   - Enlace "Restablecer" para volver al subconjunto de columnas por defecto configurado.
3. **Casillas de Verificación por Columna**: Cada columna se presenta como un item interactivo con hover y checkbox.
4. **Protección Anti-Ocultamiento Total**: Si solo queda una columna visible, el checkbox de esa columna se desactiva (`disabled`) para evitar que el usuario deje la tabla completamente vacía.
5. **Persistencia en `localStorage`**: Las columnas seleccionadas se guardan automáticamente (`localStorage.setItem('<modulo>_visible_columns', JSON.stringify(cols))`).

---

## 2. Implementación Canónica en React / TypeScript

```tsx
import React, { useState, useRef, useEffect } from 'react';
import { Columns3, ChevronDown } from 'lucide-react';

export interface ColumnDefinition {
  key: string;
  label: string;
}

export interface ColumnVisibilityProps {
  columns: ColumnDefinition[];
  visibleColumns: string[];
  onChange: (visibleKeys: string[]) => void;
  onResetDefault: () => void;
  storageKey?: string;
}

export const ColumnVisibilityDropdown: React.FC<ColumnVisibilityProps> = ({
  columns,
  visibleColumns,
  onChange,
  onResetDefault,
  storageKey
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const toggleColumn = (key: string) => {
    let next: string[];
    if (visibleColumns.includes(key)) {
      if (visibleColumns.length <= 1) return; // Protección: mínimo 1 visible
      next = visibleColumns.filter((k) => k !== key);
    } else {
      next = [...visibleColumns, key];
    }
    onChange(next);
    if (storageKey) localStorage.setItem(storageKey, JSON.stringify(next));
  };

  const showAll = () => {
    const all = columns.map((c) => c.key);
    onChange(all);
    if (storageKey) localStorage.setItem(storageKey, JSON.stringify(all));
  };

  return (
    <div className="cartera-col-visibility-wrapper" ref={containerRef}>
      <button
        type="button"
        className={`cartera-col-visibility-btn ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen((prev) => !prev)}
        title="Configurar columnas visibles de la tabla"
      >
        <Columns3 size={14} className="col-btn-icon" />
        <span className="col-btn-text">Columnas</span>
        <span className="col-btn-badge">
          {visibleColumns.length}/{columns.length}
        </span>
        <ChevronDown size={13} className={`col-btn-chevron ${isOpen ? 'is-rotated' : ''}`} />
      </button>

      {isOpen && (
        <div className="cartera-col-visibility-popover">
          <div className="cartera-col-visibility-header">
            <span className="title">Columnas visibles</span>
            <div className="header-actions">
              <button type="button" className="link-btn" onClick={showAll}>
                Todas
              </button>
              <span className="divider">•</span>
              <button type="button" className="link-btn" onClick={onResetDefault}>
                Restablecer
              </button>
            </div>
          </div>
          <div className="cartera-col-visibility-list">
            {columns.map((col) => {
              const isChecked = visibleColumns.includes(col.key);
              return (
                <label key={col.key} className="cartera-col-visibility-item">
                  <input
                    type="checkbox"
                    className="col-checkbox"
                    checked={isChecked}
                    onChange={() => toggleColumn(col.key)}
                    disabled={isChecked && visibleColumns.length <= 1}
                  />
                  <span className="col-name">{col.label}</span>
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

---

## 3. Estilos CSS Corporativos

```css
.cartera-col-visibility-wrapper {
  position: relative;
  display: inline-block;
}

.cartera-col-visibility-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 10px;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.cartera-col-visibility-btn:hover,
.cartera-col-visibility-btn.active {
  color: var(--text-primary);
  border-color: var(--accent-color, #3b82f6);
  background-color: var(--bg-hover);
}

.col-btn-badge {
  padding: 1px 5px;
  font-size: 0.68rem;
  font-weight: 600;
  background-color: var(--bg-tertiary);
  border-radius: 10px;
}

.col-btn-chevron.is-rotated {
  transform: rotate(180deg);
}

.cartera-col-visibility-popover {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  width: 220px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  z-index: 50;
  overflow: hidden;
}

.cartera-col-visibility-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.75rem;
  font-weight: 600;
}

.cartera-col-visibility-header .link-btn {
  background: none;
  border: none;
  color: var(--accent-color, #3b82f6);
  font-size: 0.7rem;
  cursor: pointer;
  padding: 0;
}

.cartera-col-visibility-list {
  max-height: 240px;
  overflow-y: auto;
  padding: 6px 0;
}

.cartera-col-visibility-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  font-size: 0.75rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: background-color 0.1s ease;
}

.cartera-col-visibility-item:hover {
  background-color: var(--bg-hover);
}
```
