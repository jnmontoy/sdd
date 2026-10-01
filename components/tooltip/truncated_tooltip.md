# Especificación de Componente: Tooltip Truncado Inteligente (`TruncatedTooltip`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

El componente `TruncatedTooltip` resuelve el problema común en tablas y listados donde los textos largos (nombres de colaboradores, descripciones, motivos de novedades) se recortan con elipsis (`text-overflow: ellipsis`). Detecta la interacción del usuario y muestra el texto completo de forma flotante y no invasiva, con soporte completo para navegación accesible por teclado (`Enter`, `Space`, `Escape`) y dispositivos táctiles (clic para fijar/desplegar).

> **Origen y validación en producción**: Extraído y unificado a partir de `tiendita` (`TruncatedTooltip`) y `app_tic` (`HoverInfoTooltip`).

---

### 1. Requisitos Técnicos y de Negocio

1. **Cero Tooltips Huérfanos**: Despliegue anclado al elemento sin descuadrar el layout de la tabla (`position: relative`).
2. **Soporte Táctil y Teclado**: Clic/tap para expandir y cierre automático al hacer clic afuera (`mousedown` listener).
3. **Alto Rendimiento en Tablas**: No sobrecarga el DOM con portales pesados en tablas con cientos de filas.

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/TruncatedTooltip.tsx
import React, { useEffect, useRef, useState } from 'react';
import './TruncatedTooltip.css';

export interface TruncatedTooltipProps {
  text: string;
  className?: string;
  forceExpanded?: boolean;
}

export const TruncatedTooltip: React.FC<TruncatedTooltipProps> = ({
  text,
  className = '',
  forceExpanded = false,
}) => {
  const [pressed, setPressed] = useState(false);
  const wrapperRef = useRef<HTMLSpanElement>(null);
  const expanded = forceExpanded || pressed;

  useEffect(() => {
    if (!pressed) return;

    const handleOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setPressed(false);
      }
    };

    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, [pressed]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setPressed((prev) => !prev);
    }
    if (e.key === 'Escape') {
      setPressed(false);
    }
  };

  return (
    <span
      ref={wrapperRef}
      className={`tt-wrapper ${className}`}
      role="button"
      tabIndex={0}
      aria-expanded={expanded}
      title={expanded ? undefined : text}
      onClick={(e) => {
        e.stopPropagation();
        setPressed((prev) => !prev);
      }}
      onKeyDown={handleKeyDown}
    >
      <span className={`tt-text ${expanded ? 'tt-text-expanded' : ''}`}>
        {text}
      </span>
    </span>
  );
};
```

---

### 3. Estilos CSS (`TruncatedTooltip.css`)

```css
.tt-wrapper {
  display: inline-block;
  max-width: 100%;
  cursor: pointer;
  outline: none;
  border-radius: 4px;
  vertical-align: middle;
}

.tt-wrapper:focus-visible {
  box-shadow: 0 0 0 2px var(--color-primary, #10B981);
}

.tt-text {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: inherit;
  color: inherit;
  transition: all 0.15s ease;
}

.tt-text-expanded {
  white-space: normal;
  word-break: break-word;
  background: var(--bg-surface, #F8FAFC);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-subtle, #CBD5E1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 15;
}
```
