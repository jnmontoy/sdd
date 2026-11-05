# Tutorial Interactivo Dividido (`SplitTutorialWalkthrough`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de bi (tutorial de conexión a DataHub). Aquí se describe de forma genérica.

Guía paso a paso para procesos complejos (conectar una herramienta a una base de datos, integrar Power BI o Excel, primer uso de un módulo, configurar un equipo). Es un diálogo de ayuda, no un formulario CRUD, por eso puede ser un modal centrado.

> **Seguridad (DEBE):** el panel izquierdo NO DEBE mostrar contraseñas, tokens ni cadenas de conexión con credenciales. Muestra solo parámetros no secretos (servidor, base de datos, puerto) y explica cómo obtener la credencial por el canal oficial (gestor de secretos o solicitud a TI). Los nombres de servidor de los ejemplos son ficticios.

---

## 1. Arquitectura y anatomía visual

1. **Selector previo (`TutorialChooserModal`)**: el usuario elige la variante de guía (ej. "¿Cómo conectar desde Power BI?" o "desde Excel").
2. **Modal dividido (`SplitTutorialModal`)**:
   - **Panel izquierdo (contexto)**: parámetros no secretos o bloques de código con botón "Copiar".
   - **Panel derecho (pasos)**: indicador de puntos, captura de pantalla ampliable, texto del paso con resaltado de los nombres de botones entre comillas y navegación Atrás / Siguiente.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Tutorial: conexión de datos                          Paso 2 de 5                   [✕] │
├────────────────────────────────────────────────────┬───────────────────────────────────┤
│ PARÁMETROS                                         │   (●) ─── (○) ─── (○) ─── (○)     │
│  Servidor:      [ db.ejemplo.local     ] [Copiar]  │ ┌───────────────────────────────┐ │
│  Base de datos: [ analitica            ] [Copiar]  │ │  [Captura de pantalla]  [Zoom]│ │
│  Usuario: el asignado por TI (no se muestra aquí)  │ └───────────────────────────────┘ │
│  Consulta Power Query:                             │ En Power BI, haz clic en          │
│  ┌───────────────────────────────┐                 │ "Obtener datos" y elige           │
│  │ let Source = PostgreSQL...    │ [Copiar]        │ "PostgreSQL".                     │
│  └───────────────────────────────┘                 │ [← Atrás]           [Siguiente →] │
└────────────────────────────────────────────────────┴───────────────────────────────────┘
```

---

## 2. Contratos de datos (TypeScript)

```typescript
import type { ReactNode } from 'react';

export interface TutorialStep {
  id: string;
  image?: string;    // URL o asset importado de la captura
  imageAlt?: string; // descripción de la captura (accesibilidad)
  text: string;      // las palabras entre "comillas" se resaltan
}

export interface SplitTutorialModalProps {
  title: string;
  leftTitle: string;
  leftContent: ReactNode; // parámetros no secretos o código copiable
  steps: TutorialStep[];
  onClose: () => void;
  onFinish?: () => void;
}

export interface TutorialChooserOption {
  key: string;
  title: string;
  description: string;
  icon: ReactNode;
  disabled?: boolean;
}

export interface TutorialChooserModalProps {
  title?: string;
  options: TutorialChooserOption[];
  onSelect: (optionKey: string) => void;
  onClose: () => void;
}
```

---

## 3. Hook de navegación (`useTutorialSteps.ts`)

Separa "terminar" (último paso) de "cerrar" (Escape). Las flechas no se interceptan mientras el foco está en un campo de texto.

```typescript
import { useCallback, useEffect, useRef, useState } from 'react';
import type { TutorialStep } from './tutorial.types';

export function useTutorialSteps(steps: TutorialStep[], onFinish: () => void, onClose: () => void) {
  const [currentStep, setCurrentStep] = useState(0);
  const lastIndex = Math.max(steps.length - 1, 0);
  const isFirst = currentStep === 0;
  const isLast = currentStep >= lastIndex;

  // Callbacks en ref: el listener de teclado no se re-registra en cada render.
  const handlersRef = useRef({ onFinish, onClose });
  useEffect(() => {
    handlersRef.current = { onFinish, onClose };
  }, [onFinish, onClose]);

  const goNext = useCallback(() => {
    if (currentStep >= lastIndex) handlersRef.current.onFinish();
    else setCurrentStep((prev) => prev + 1);
  }, [currentStep, lastIndex]);

  const goPrev = useCallback(() => setCurrentStep((prev) => Math.max(prev - 1, 0)), []);

  const goTo = useCallback(
    (idx: number) => {
      if (idx >= 0 && idx <= lastIndex) setCurrentStep(idx);
    },
    [lastIndex]
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const typing = target?.closest('input, textarea, select, [contenteditable="true"]');
      if (e.key === 'Escape') handlersRef.current.onClose();
      else if (!typing && e.key === 'ArrowRight') goNext();
      else if (!typing && e.key === 'ArrowLeft') goPrev();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goNext, goPrev]);

  return { step: steps[currentStep], currentStep, isFirst, isLast, goNext, goPrev, goTo };
}
```

---

## 4. Texto con resaltado

Resalta las opciones de la interfaz escritas entre comillas. Se construye con nodos de React (sin `dangerouslySetInnerHTML`).

```tsx
import React from 'react';

export const HighlightedStepText: React.FC<{ text: string }> = ({ text }) => {
  const parts = text.split(/("[^"]+")/g);
  return (
    <p className="tutorial-modal-text">
      {parts.map((part, index) => {
        const match = part.match(/^"([^"]+)"$/);
        return match ? (
          <mark key={index} className="tutorial-modal-highlight">{match[1]}</mark>
        ) : (
          <React.Fragment key={index}>{part}</React.Fragment>
        );
      })}
    </p>
  );
};
```

**Accesibilidad del modal:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` apuntando al título, foco atrapado dentro y devuelto al botón que lo abrió; los puntos de progreso son botones con `aria-label="Ir al paso N"` y `aria-current="step"` en el activo; la captura lleva `alt` descriptivo.

---

## 5. Estilos (`SplitTutorial.css`)

```css
/* Fondo del modal */
.tutorial-modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: var(--overlay-scrim);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: 20px;
}

/* Contenedor dividido */
.tutorial-split-modal {
  width: 95vw;
  max-width: 1100px;
  max-height: 90vh;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-modal);
}

.tutorial-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
}

.tutorial-modal-title {
  font-size: 1.15rem;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.tutorial-modal-step-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* Cuerpo dividido */
.tutorial-split-body {
  display: grid;
  grid-template-columns: 360px 1fr;
  flex: 1;
  overflow: hidden;
}

@media (max-width: 768px) {
  .tutorial-split-body { grid-template-columns: 1fr; overflow-y: auto; }
}

.tutorial-split-left {
  padding: 24px;
  background: var(--bg-elevated);
  border-right: 1px solid var(--border-subtle);
  overflow-y: auto;
}

.tutorial-split-right {
  padding: 24px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

/* Progreso (puntos) */
.tutorial-modal-progress {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 18px;
}

.tutorial-modal-dot {
  width: 10px;
  height: 10px;
  padding: 0;
  border: none;
  border-radius: var(--radius-full);
  background: var(--border-strong);
  cursor: pointer;
  transition: transform var(--transition-base), background var(--transition-base);
}

.tutorial-modal-dot:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.tutorial-modal-dot.active {
  background: var(--brand-primary);
  transform: scale(1.3);
  box-shadow: 0 0 10px var(--brand-glow);
}

.tutorial-modal-dot.done {
  background: color-mix(in srgb, var(--brand-primary) 45%, transparent);
}

/* Imagen con botón de zoom */
.tutorial-image-wrap {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  margin-bottom: 16px;
  background: var(--bg-viewport);
}

.tutorial-modal-image {
  width: 100%;
  max-height: 380px;
  object-fit: contain;
  display: block;
}

.tutorial-image-zoom-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: var(--overlay-surface);
  color: var(--text-on-overlay);
  border: none;
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: background var(--transition-base), color var(--transition-base);
}

.tutorial-image-zoom-btn:hover {
  background: var(--brand-primary);
  color: var(--text-on-brand);
}

/* Resaltado de nombres de botones */
.tutorial-modal-highlight {
  background: var(--status-success-bg);
  color: var(--text-primary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-weight: var(--font-weight-semibold);
  border: 1px solid var(--border-card-accent);
}

/* Navegación */
.tutorial-modal-footer {
  display: flex;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 18px;
}
```
