# Asistente por Etapas (`StepperWizard`)
## SDD Joli Foods — Spec-Driven Development

Organiza flujos de captura largos en pasos secuenciales con un indicador visual. La validación de cada paso la hace el formulario contenedor (por ejemplo con un esquema Zod por paso); el stepper solo muestra el estado y decide a qué pasos se puede saltar.

---

## 1. Contrato de props (TypeScript)

```typescript
import type { ReactNode } from 'react';

export interface StepItem {
  id: string;
  label: string;
  description?: string;
  icon?: ReactNode;
  isOptional?: boolean;
}

export interface StepperWizardProps {
  steps: StepItem[];
  activeStepIndex: number;
  completedStepIndices: number[];
  onStepClick?: (stepIndex: number) => void;
  orientation?: 'horizontal' | 'vertical';
  /** Si es false, solo se puede ir a pasos completados o al siguiente al último completado. */
  allowJumpingAhead?: boolean;
}
```

---

## 2. Implementación de referencia (`StepperWizard.tsx`)

```tsx
import React from 'react';
import { Check } from 'lucide-react';
import type { StepperWizardProps } from './stepper.types';
import './StepperWizard.css';

export const StepperWizard: React.FC<StepperWizardProps> = ({
  steps,
  activeStepIndex,
  completedStepIndices,
  onStepClick,
  orientation = 'horizontal',
  allowJumpingAhead = false,
}) => {
  const completed = new Set(completedStepIndices);
  const furthestReachable = Math.max(-1, ...completedStepIndices) + 1;

  return (
    <nav aria-label="Progreso del formulario">
      <ol className={`stepper-container stepper--${orientation}`}>
        {steps.map((step, idx) => {
          const isActive = idx === activeStepIndex;
          const isCompleted = completed.has(idx);
          const canJump = Boolean(onStepClick) && !isActive && (allowJumpingAhead || idx <= furthestReachable);
          const stateLabel = isCompleted ? 'completado' : isActive ? 'paso actual' : 'pendiente';

          return (
            <li
              key={step.id}
              className={`stepper-item ${isActive ? 'stepper-item--active' : ''} ${isCompleted ? 'stepper-item--completed' : ''}`}
            >
              <button
                type="button"
                className="stepper-trigger"
                onClick={() => onStepClick?.(idx)}
                disabled={!canJump}
                aria-current={isActive ? 'step' : undefined}
                aria-label={`Paso ${idx + 1}: ${step.label} (${stateLabel}${step.isOptional ? ', opcional' : ''})`}
              >
                <span className="stepper-circle" aria-hidden="true">
                  {isCompleted ? <Check size={16} /> : step.icon ?? idx + 1}
                </span>
                <span className="stepper-text">
                  <span className="stepper-label">{step.label}</span>
                  {step.description && <span className="stepper-description">{step.description}</span>}
                </span>
              </button>
              {idx < steps.length - 1 && <span className="stepper-connector" aria-hidden="true" />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
```

---

## 3. Estilos (`StepperWizard.css`)

```css
.stepper-container {
  display: flex;
  align-items: flex-start;
  width: 100%;
  list-style: none;
  margin: 0 0 24px;
  padding: 16px 0;
}

.stepper--vertical {
  flex-direction: column;
  gap: 16px;
}

.stepper-item {
  display: flex;
  align-items: center;
  position: relative;
  flex: 1;
}

.stepper-item:last-child {
  flex: 0 0 auto;
}

.stepper-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  border: none;
  padding: 0;
  text-align: left;
  color: inherit;
  cursor: pointer;
  z-index: 2;
}

.stepper-trigger:disabled {
  cursor: default;
}

.stepper-trigger:focus-visible .stepper-circle {
  box-shadow: var(--shadow-input-focus);
}

/* Círculo indicador */
.stepper-circle {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: var(--radius-full);
  background: var(--bg-elevated);
  border: 2px solid var(--border-strong);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-semibold);
  font-size: 0.85rem;
  transition: background var(--transition-base), border-color var(--transition-base), color var(--transition-base);
}

.stepper-item--active .stepper-circle {
  border-color: var(--brand-primary);
  background: var(--brand-primary);
  color: var(--text-on-brand);
  box-shadow: 0 0 12px var(--brand-glow);
}

.stepper-item--completed .stepper-circle {
  border-color: var(--brand-primary);
  background: var(--status-success-bg);
  color: var(--brand-primary);
}

.stepper-text {
  display: flex;
  flex-direction: column;
}

.stepper-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.stepper-description {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

/* Línea conectora entre pasos */
.stepper-connector {
  flex: 1;
  height: 2px;
  margin: 0 12px;
  background: var(--border-subtle);
}

.stepper-item--completed .stepper-connector {
  background: var(--brand-primary);
}

.stepper--vertical .stepper-connector {
  display: none;
}
```
