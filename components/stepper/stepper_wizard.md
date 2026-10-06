# Asistente por Etapas (Stepper / Wizard) (`StepperWizard`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este componente organiza flujos de captura largos o configuraciones multi-pantalla en un indicador secuencial interactivo con validación de requisitos por cada paso.

---

## 1. Contrato de Props en TypeScript

```typescript
export interface StepItem {
  id: string;
  label: string;
  description?: string;
  icon?: React.ReactNode;
  isOptional?: boolean;
}

export interface StepperWizardProps {
  steps: StepItem[];
  activeStepIndex: number;
  completedStepIndices: number[];
  onStepClick?: (stepIndex: number) => void;
  orientation?: 'horizontal' | 'vertical';
  allowJumpingAhead?: boolean;
}
```

---

## 2. Anatomía y Estilos CSS Canónicos

```css
.stepper-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 16px 0;
  margin-bottom: 24px;
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

/* Círculo indicador de paso */
.stepper-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-bg-surface-elevated, #334155);
  border: 2px solid var(--color-border-subtle, #475569);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.85rem;
  z-index: 2;
  transition: all 0.3s ease;
}

.stepper-item--active .stepper-circle {
  border-color: var(--color-primary, #10b981);
  background: var(--color-primary, #10b981);
  color: #0f172a;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
}

.stepper-item--completed .stepper-circle {
  border-color: var(--color-primary, #10b981);
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-primary, #10b981);
}

/* Línea conectora entre círculos */
.stepper-connector {
  position: absolute;
  top: 16px;
  left: 32px;
  right: 0;
  height: 2px;
  background: var(--color-border-subtle, #334155);
  z-index: 1;
}

.stepper-item--completed .stepper-connector {
  background: var(--color-primary, #10b981);
}
```
