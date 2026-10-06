# Tutorial Interactivo Dividido y Onboarding Visual (`SplitTutorialWalkthrough`)
## Componente UI Canónico — Spec-Driven Development (SDD)
### Inspirado en la implementación de referencia del ecosistema BI / Datahub

Este componente proporciona una experiencia inmersiva de **tutorial paso a paso** para guiar a los usuarios en procesos complejos (como conexión a bases de datos, integración con Power BI/Excel, primer uso de un módulo o configuración de hardware).

---

## 1. Arquitectura y Anatomía Visual

El sistema se compone de dos modalidades de visualización:
1. **Modal de Selección Previa (`TutorialChooserModal`)**: Diálogo inicial donde el usuario selecciona la variante de guía que desea seguir (ej. "¿Cómo conectar desde Power BI?" vs. "¿Cómo conectar desde Excel?").
2. **Modal Dividido (`SplitTutorialModal`)**:
   - **Panel Izquierdo (Contexto Operativo)**: Muestra credenciales, parámetros del servidor, tokens o bloques de código con botón de copiado instantáneo.
   - **Panel Derecho (Carrusel de Pasos)**: Muestra el indicador de puntos (*dots*), capturas de pantalla con ampliación (*Lightbox Zoom*), textos explicativos con resaltado automático de botones entre comillas y controles de navegación Atrás / Siguiente.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [HEADER] Tutorial: Conexión de Datos               Paso 2 de 5                     [✕] │
├────────────────────────────────────────────────────┬───────────────────────────────────┤
│ [PANEL IZQUIERDO: Parámetros del Sistema]          │ [PANEL DERECHO: Carrusel Guiado]  │
│                                                    │   (●) ─── (○) ─── (○) ─── (○)     │
│  Servidor:                                         │ ┌───────────────────────────────┐ │
│  [ db.jolifoods.co               ] [📋 Copiar]     │ │  [Captura de Pantalla]        │ │
│                                                    │ │                               │ │
│  Base de Datos:                                    │ │                      [🔍 Zoom]│ │
│  [ datahub_bi                    ] [📋 Copiar]     │ └───────────────────────────────┘ │
│                                                    │                                   │
│  Código Power Query:                               │ En Power BI, haz clic en          │
│  ┌───────────────────────────────┐                 │ <mark>"Obtener datos"</mark> y    │
│  │ let Source = PostgreSQL...    │ [📋 Copiar]     │ selecciona "PostgreSQL".          │
│  └───────────────────────────────┘                 │                                   │
│                                                    │ [← Atrás]           [Siguiente →] │
└────────────────────────────────────────────────────┴───────────────────────────────────┘
```

---

## 2. Contratos de Datos y Tipos en TypeScript

```typescript
export interface TutorialStep {
  id?: string;
  image?: string; // URL o asset importado de la captura
  text: string;   // Texto del paso; las palabras entre "comillas" se resaltan automáticamente
}

export interface SplitTutorialModalProps {
  title: string;
  leftTitle: string;
  leftContent: React.ReactNode; // Parámetros, credenciales o código copiable
  steps: TutorialStep[];
  onClose: () => void;
  onFinish?: () => void;
}

export interface TutorialChooserOption {
  key: string;
  title: string;
  description: string;
  icon: React.ReactNode;
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

## 3. Hook Controlador de Navegación (`useTutorialSteps.ts`)

```typescript
import { useState, useCallback, useEffect } from 'react';
import type { TutorialStep } from './tutorialSteps';

export function useTutorialSteps(steps: TutorialStep[], onFinish: () => void) {
  const [currentStep, setCurrentStep] = useState(0);

  const isFirst = currentStep === 0;
  const isLast = currentStep === steps.length - 1;

  const goNext = useCallback(() => {
    if (isLast) {
      onFinish();
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  }, [isLast, onFinish]);

  const goPrev = useCallback(() => {
    if (!isFirst) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [isFirst]);

  const goTo = useCallback((idx: number) => {
    if (idx >= 0 && idx < steps.length) {
      setCurrentStep(idx);
    }
  }, [steps.length]);

  // Soporte de navegación por teclado (Flechas izquierda / derecha y Escape)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') goNext();
      if (e.key === 'ArrowLeft') goPrev();
      if (e.key === 'Escape') onFinish();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goNext, goPrev, onFinish]);

  return {
    step: steps[currentStep],
    currentStep,
    isFirst,
    isLast,
    goNext,
    goPrev,
    goTo,
  };
}
```

---

## 4. Componente de Renderizado de Texto con Resaltado Inteligente

El texto del paso resalta automáticamente las opciones de la interfaz marcadas entre comillas con el token esmeralda corporativo:

```tsx
export const HighlightedStepText: React.FC<{ text: string }> = ({ text }) => {
  const parts = text.split(/("[^"]+")/g);
  return (
    <p className="tutorial-modal-text">
      {parts.map((part, index) => {
        const match = part.match(/^"([^"]+)"$/);
        return match ? (
          <mark key={index} className="tutorial-modal-highlight">
            {match[1]}
          </mark>
        ) : (
          part
        );
      })}
    </p>
  );
};
```

---

## 5. Estilos CSS Canónicos (`DatahubTutorial.css` / `variables.css`)

```css
/* Fondo difuminado modal */
.tutorial-modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 20px;
}

/* Contenedor Split */
.tutorial-split-modal {
  width: 95vw;
  max-width: 1100px;
  max-height: 90vh;
  background: var(--color-bg-surface, #1e293b);
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.1));
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.tutorial-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.08));
  background: rgba(255, 255, 255, 0.02);
}

.tutorial-modal-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text-main, #f8fafc);
}

.tutorial-modal-step-label {
  font-size: 0.8rem;
  color: var(--color-text-muted, #94a3b8);
}

/* Cuerpo Dividido */
.tutorial-split-body {
  display: grid;
  grid-template-columns: 360px 1fr;
  flex: 1;
  overflow: hidden;
}

.tutorial-split-left {
  padding: 24px;
  background: var(--color-bg-surface-elevated, #0f172a);
  border-right: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.08));
  overflow-y: auto;
}

.tutorial-split-right {
  padding: 24px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

/* Indicador de progreso (Dots) */
.tutorial-modal-progress {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 18px;
}

.tutorial-modal-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-border-subtle, #475569);
  cursor: pointer;
  transition: all 0.25s ease;
}

.tutorial-modal-dot.active {
  background: var(--color-primary, #10b981);
  transform: scale(1.3);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

.tutorial-modal-dot.done {
  background: rgba(16, 185, 129, 0.4);
}

/* Contenedor de Imagen con Botón Zoom */
.tutorial-image-wrap {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.1));
  margin-bottom: 16px;
  background: #000;
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
  background: rgba(15, 23, 42, 0.7);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: background 0.2s ease;
}

.tutorial-image-zoom-btn:hover {
  background: var(--color-primary, #10b981);
  color: #0f172a;
}

/* Resaltador de botones */
.tutorial-modal-highlight {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-primary, #10b981);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

/* Botones de navegación Footer */
.tutorial-modal-footer {
  display: flex;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 18px;
}
```
