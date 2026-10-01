# Componente UI: Columnas Ajustables / Redimensionables (Column Resizer)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)
### Patrón Canónico de Referencia: Módulo BI Cartera (`useResizable` / `cartera-th-resizer`)

El **Column Resizer** permite a los usuarios ajustar interactivamente el ancho de cada columna de la tabla arrastrando su borde derecho. Además, incluye la capacidad de restablecer el ancho predeterminado mediante doble clic y persistir las preferencias del usuario en `localStorage`.

---

## 1. Características Técnicas

1. **Control de Arrastre Fluido (`col-resize`)**: Un manipulador visual transparente de 6px en el borde derecho de cada cabecera `<th>`, con cambio cromático a color acento al pasar el cursor o hacer clic.
2. **Ancho Mínimo de Seguridad**: Garantiza que ninguna columna pueda contraerse por debajo de `60px` para evitar colapsos visuales.
3. **Restablecimiento Inmediato por Doble Clic**: Un doble clic en el separador restaura inmediatamente el ancho de columna por defecto asignado en la configuración.
4. **Persistencia Local (`localStorage`)**: Los anchos personalizados se guardan automáticamente por clave de columna (`localStorage.setItem('<modulo>_col_widths', JSON.stringify(widths))`).
5. **Estructura de Tabla de Ancho Fijo**: Se aplica `tableLayout: 'fixed'` y anchos en píxeles tanto al `<th>` como al `<td>` correspondiente para evitar desalineaciones durante el scroll horizontal.

---

## 2. Implementación Canónica en React / TypeScript

### Hook `useResizable.ts` o Lógica en Componente de Tabla

```tsx
import React, { useState } from 'react';

export const DEFAULT_COL_WIDTHS: Record<string, number> = {
  codigo: 120,
  departamento: 160,
  municipio: 150,
  temperatura: 120,
  precipitacion: 140,
  humedad: 120,
  alerta: 130,
  estado: 110,
  opciones: 95
};

export const useColumnResize = (storageKey: string, defaultWidths: Record<string, number>) => {
  const [colWidths, setColWidths] = useState<Record<string, number>>(() => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      try {
        return { ...defaultWidths, ...JSON.parse(saved) };
      } catch {
        return { ...defaultWidths };
      }
    }
    return { ...defaultWidths };
  });

  const handleStartResize = (key: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const startX = e.clientX;
    const currentWidth = colWidths[key] || defaultWidths[key] || 120;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const diff = moveEvent.clientX - startX;
      const newWidth = Math.max(60, currentWidth + diff);
      setColWidths((prev) => {
        const next = { ...prev, [key]: newWidth };
        localStorage.setItem(storageKey, JSON.stringify(next));
        return next;
      });
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  const handleResetWidth = (key: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setColWidths((prev) => {
      const next = { ...prev, [key]: defaultWidths[key] || 120 };
      localStorage.setItem(storageKey, JSON.stringify(next));
      return next;
    });
  };

  return { colWidths, handleStartResize, handleResetWidth };
};
```

---

## 3. Renderizado del Marcador en el Encabezado `<th>`

```tsx
<th
  key={col.key}
  className="cartera-th"
  style={{
    width: `${colWidths[col.key]}px`,
    minWidth: `${colWidths[col.key]}px`,
    maxWidth: `${colWidths[col.key]}px`,
    position: 'relative'
  }}
>
  <div className="th-content">
    <span>{col.label}</span>
  </div>

  {/* Manipulador de Redimensionamiento */}
  <div
    className="cartera-th-resizer"
    onMouseDown={(e) => handleStartResize(col.key, e)}
    onDoubleClick={(e) => handleResetWidth(col.key, e)}
    title="Arrastra para redimensionar columna (Doble clic para restablecer)"
  />
</th>
```

---

## 4. Estilos CSS Corporativos

```css
/* Cabecera relativa para contener el separador */
.cartera-th {
  position: relative;
  overflow: visible;
  user-select: none;
}

/* Barra de agarre interactiva en el borde derecho */
.cartera-th-resizer {
  position: absolute;
  top: 0;
  right: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  user-select: none;
  z-index: 5;
  transition: background-color 0.15s ease;
}

.cartera-th-resizer:hover,
.cartera-th-resizer:active {
  background-color: var(--accent-color, #3b82f6);
  opacity: 0.8;
}
```

---

## 5. Implementación Autónoma en Vanilla JS (Mocks / HTML)

```javascript
let isResizing = false;
let currentResizingCol = null;
let startX = 0;
let startWidth = 0;

function handleStartColResize(colKey, event) {
  event.preventDefault();
  event.stopPropagation();
  isResizing = true;
  currentResizingCol = colKey;
  startX = event.clientX;
  
  const th = event.target.closest('th');
  startWidth = th.getBoundingClientRect().width;
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';

  function onMouseMove(e) {
    if (!isResizing) return;
    const diff = e.clientX - startX;
    const newWidth = Math.max(60, Math.round(startWidth + diff));
    applyColumnWidth(currentResizingCol, newWidth);
  }

  function onMouseUp() {
    isResizing = false;
    currentResizingCol = null;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  }

  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
}

function handleResetColWidth(colKey, event) {
  event.preventDefault();
  event.stopPropagation();
  const defaultW = DEFAULT_COL_WIDTHS[colKey] || 120;
  applyColumnWidth(colKey, defaultW);
}

function applyColumnWidth(colKey, width) {
  COL_WIDTHS[colKey] = width;
  const ths = document.querySelectorAll(`th[data-col="${colKey}"]`);
  const tds = document.querySelectorAll(`td[data-col="${colKey}"]`);
  ths.forEach(th => {
    th.style.width = width + 'px';
    th.style.minWidth = width + 'px';
    th.style.maxWidth = width + 'px';
  });
  tds.forEach(td => {
    td.style.width = width + 'px';
    td.style.minWidth = width + 'px';
    td.style.maxWidth = width + 'px';
  });
}
```
