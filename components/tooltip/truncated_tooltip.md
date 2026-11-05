# Especificación de Componente: Tooltip de Texto Truncado (`TruncatedTooltip`)
## Spec-Driven Development (SDD)

> **Origen:** patrón tomado de tiendita (`TruncatedTooltip`) y app_tic (`HoverInfoTooltip`). Aquí se describe de forma genérica.

`TruncatedTooltip` muestra el texto completo de celdas o etiquetas recortadas con elipsis (`text-overflow: ellipsis`): nombres largos, descripciones, motivos. Funciona con ratón, teclado (`Enter`, `Space`, `Escape`) y pantallas táctiles (tocar para abrir).

---

### 1. Requisitos

1. **Solo cuando hace falta:** el componente mide si el texto está recortado (`scrollWidth > clientWidth`, recalculado con `ResizeObserver`). Si no lo está, se comporta como texto normal: sin tabulación ni rol de botón (evita cientos de paradas de tabulación inútiles en una tabla).
2. **Flotante:** el texto completo aparece en una burbuja posicionada sobre la celda, sin cambiar la altura de la fila.
3. **Accesibilidad:** cuando está recortado, el disparador es enfocable (`role="button"`, `aria-expanded`, `aria-describedby` a la burbuja); `Escape` cierra; clic fuera cierra.
4. **Rendimiento:** sin portales ni librerías; un `ResizeObserver` por instancia con limpieza al desmontar.

---

### 2. Implementación TypeScript / React (`src/components/ui/TruncatedTooltip.tsx`)

```tsx
import React, { useEffect, useId, useRef, useState } from 'react';
import './TruncatedTooltip.css';

export interface TruncatedTooltipProps {
  text: string;
  className?: string;
}

export const TruncatedTooltip: React.FC<TruncatedTooltipProps> = ({ text, className = '' }) => {
  const [isTruncated, setIsTruncated] = useState(false);
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLSpanElement>(null);
  const textRef = useRef<HTMLSpanElement>(null);
  const bubbleId = useId();

  // Detectar recorte y volver a medir cuando cambia el ancho de la columna
  useEffect(() => {
    const el = textRef.current;
    if (!el) return;
    const measure = () => setIsTruncated(el.scrollWidth > el.clientWidth);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, [text]);

  useEffect(() => {
    if (!open) return;
    const onMouseDown = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', onMouseDown);
    return () => document.removeEventListener('mousedown', onMouseDown);
  }, [open]);

  if (!isTruncated) {
    return (
      <span className={`tt-wrapper ${className}`}>
        <span ref={textRef} className="tt-text">{text}</span>
      </span>
    );
  }

  return (
    <span
      ref={wrapperRef}
      className={`tt-wrapper is-interactive ${className}`}
      role="button"
      tabIndex={0}
      aria-expanded={open}
      aria-describedby={open ? bubbleId : undefined}
      onClick={(e) => {
        e.stopPropagation(); // no dispara el clic de la fila
        setOpen((prev) => !prev);
      }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          e.stopPropagation();
          setOpen((prev) => !prev);
        } else if (e.key === 'Escape') {
          setOpen(false);
        }
      }}
    >
      <span ref={textRef} className="tt-text">{text}</span>
      {open && (
        <span id={bubbleId} role="tooltip" className="tt-bubble">{text}</span>
      )}
    </span>
  );
};
```

---

### 3. Estilos CSS (`TruncatedTooltip.css`)

```css
.tt-wrapper {
  position: relative;
  display: inline-block;
  max-width: 100%;
  vertical-align: middle;
}

.tt-wrapper.is-interactive {
  cursor: help;
  border-radius: var(--radius-sm);
}

.tt-wrapper.is-interactive:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

.tt-text {
  display: block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.tt-bubble {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: var(--z-popover);
  width: max-content;
  max-width: min(360px, 80vw);
  padding: 6px 10px;
  font-size: var(--font-size-xs);
  line-height: var(--line-height-normal);
  white-space: normal;
  word-break: break-word;
  color: var(--text-primary);
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-popover);
}
```

En tablas con `overflow: hidden` en celdas, la burbuja puede recortarse; en ese caso la celda DEBERÍA usar `overflow: visible` o la tabla mostrar el texto completo en el drawer de detalle.
