# Componente UI: Columnas Redimensionables (Column Resizer)
## Spec-Driven Development (SDD)

El **Column Resizer** permite ajustar el ancho de cada columna arrastrando su borde derecho (o con el teclado), restablecer el ancho por defecto con doble clic y recordar la preferencia del usuario en `localStorage`.

---

## 1. Características

1. **Manipulador de arrastre (`col-resize`)** de 6px en el borde derecho de cada `<th>`, resaltado con el color de marca al pasar el cursor o al enfocarlo.
2. **Ancho mínimo** de `60px` para evitar columnas colapsadas.
3. **Doble clic** sobre el separador restaura el ancho por defecto.
4. **Teclado:** el separador es enfocable (`role="separator"`); `←`/`→` ajustan 10px (`Shift` = 50px) y `Enter` restablece.
5. **Persistencia** con la clave `STORAGE_KEYS.columnWidths(modulo)` (prefijo de app, ver [`auth_context.md`](../context/auth_context.md) §2.1). Se guarda **al soltar** el arrastre, no en cada movimiento.
6. **Tabla de ancho fijo:** `table-layout: fixed` y anchos en píxeles en `<th>` para evitar desalineaciones con scroll horizontal.

---

## 2. Hook de referencia (`src/hooks/useColumnResize.ts`)

```tsx
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { STORAGE_KEYS, safeStorage } from '../config/storageKeys';

const MIN_WIDTH = 60;
const FALLBACK_WIDTH = 120;

function readSaved(key: string, defaults: Record<string, number>): Record<string, number> {
  const raw = safeStorage.get(key);
  if (!raw) return { ...defaults };
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const valid = Object.fromEntries(
      Object.entries(parsed).filter((entry): entry is [string, number] => typeof entry[1] === 'number'),
    );
    return { ...defaults, ...valid };
  } catch {
    return { ...defaults };
  }
}

export function useColumnResize(modulo: string, defaultWidths: Record<string, number>) {
  const storageKey = STORAGE_KEYS.columnWidths(modulo);
  const [colWidths, setColWidths] = useState<Record<string, number>>(() => readSaved(storageKey, defaultWidths));
  const widthsRef = useRef(colWidths);
  const draggingRef = useRef(false);
  const cleanupRef = useRef<(() => void) | null>(null);

  // Sincroniza la ref y persiste cuando no hay un arrastre en curso
  useEffect(() => {
    widthsRef.current = colWidths;
    if (!draggingRef.current) safeStorage.set(storageKey, JSON.stringify(colWidths));
  }, [colWidths, storageKey]);

  const setWidth = useCallback((key: string, width: number) => {
    setColWidths((prev) => ({ ...prev, [key]: Math.max(MIN_WIDTH, Math.round(width)) }));
  }, []);

  const handleStartResize = useCallback(
    (key: string, event: React.MouseEvent) => {
      event.preventDefault();
      event.stopPropagation();
      const startX = event.clientX;
      const startWidth = widthsRef.current[key] ?? defaultWidths[key] ?? FALLBACK_WIDTH;

      const onMouseMove = (moveEvent: MouseEvent) => setWidth(key, startWidth + moveEvent.clientX - startX);
      const stop = () => {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        draggingRef.current = false;
        cleanupRef.current = null;
      };
      const onMouseUp = () => {
        stop();
        safeStorage.set(storageKey, JSON.stringify(widthsRef.current)); // una sola escritura al soltar
      };

      draggingRef.current = true;

      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
      cleanupRef.current = stop;
    },
    [defaultWidths, setWidth, storageKey],
  );

  const handleResetWidth = useCallback(
    (key: string) => {
      setWidth(key, defaultWidths[key] ?? FALLBACK_WIDTH);
    },
    [defaultWidths, setWidth],
  );

  const handleKeyResize = useCallback(
    (key: string, event: React.KeyboardEvent) => {
      const step = event.shiftKey ? 50 : 10;
      const current = widthsRef.current[key] ?? defaultWidths[key] ?? FALLBACK_WIDTH;
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
        event.preventDefault();
        setWidth(key, current + (event.key === 'ArrowRight' ? step : -step));
      } else if (event.key === 'Enter') {
        event.preventDefault();
        handleResetWidth(key);
      }
    },
    [defaultWidths, handleResetWidth, setWidth],
  );

  // Si el componente se desmonta durante un arrastre, se retiran los listeners
  useEffect(() => () => cleanupRef.current?.(), []);

  return { colWidths, handleStartResize, handleResetWidth, handleKeyResize };
}
```

Ejemplo de anchos por defecto de un módulo:

```ts
export const DEFAULT_COL_WIDTHS: Record<string, number> = {
  codigo: 120,
  cliente: 220,
  fecha: 120,
  valor: 140,
  estado: 110,
  opciones: 95,
};
```

---

## 3. Separador en el encabezado `<th>`

```tsx
<th key={col.key} className="resizable-th" style={{ width: colWidths[col.key] }}>
  <div className="th-content">
    <span>{col.label}</span>
  </div>

  <div
    className="resizable-th-resizer"
    role="separator"
    aria-orientation="vertical"
    aria-label={`Ajustar ancho de ${col.label}`}
    aria-valuenow={colWidths[col.key]}
    aria-valuemin={60}
    tabIndex={0}
    onMouseDown={(e) => handleStartResize(col.key, e)}
    onDoubleClick={() => handleResetWidth(col.key)}
    onKeyDown={(e) => handleKeyResize(col.key, e)}
    title="Arrastra para ajustar el ancho (doble clic para restablecer)"
  />
</th>
```

---

## 4. Estilos CSS

```css
.resizable-th {
  position: relative;
  overflow: visible;
  user-select: none;
}

.resizable-th-resizer {
  position: absolute;
  top: 0;
  right: 0;
  z-index: var(--z-base);
  width: 6px;
  height: 100%;
  cursor: col-resize;
  user-select: none;
  transition: background-color var(--transition-fast);
}

.resizable-th-resizer:hover,
.resizable-th-resizer:active,
.resizable-th-resizer:focus-visible {
  background-color: var(--brand-primary);
  outline: none;
}
```

---

## 5. Implementación en Vanilla JS (mocks HTML)

```javascript
const MIN_WIDTH = 60;

function handleStartColResize(colKey, event) {
  event.preventDefault();
  event.stopPropagation();
  const startX = event.clientX;
  const startWidth = event.target.closest('th').getBoundingClientRect().width;
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';

  function onMouseMove(e) {
    applyColumnWidth(colKey, Math.max(MIN_WIDTH, Math.round(startWidth + e.clientX - startX)));
  }

  function onMouseUp() {
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
  applyColumnWidth(colKey, DEFAULT_COL_WIDTHS[colKey] || 120);
}

function applyColumnWidth(colKey, width) {
  COL_WIDTHS[colKey] = width;
  document.querySelectorAll(`th[data-col="${colKey}"]`).forEach((th) => {
    th.style.width = width + 'px';
  });
}
```

En los mocks, `COL_WIDTHS` y `DEFAULT_COL_WIDTHS` son objetos globales del archivo `[modulo].js`; con `table-layout: fixed` basta con fijar el ancho del `<th>`.
