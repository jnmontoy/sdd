# Dashboard de Uso de Plataforma, Adopción y Opiniones (`PlatformUsageDashboard`)
## SDD Joli Foods — Spec-Driven Development

Panel para **monitorear la adopción** de una aplicación (qué módulos se usan, cuánto, por quién en términos agregados) y **recoger sugerencias** de los usuarios para planificar ciclos de mejora continua.

> **Privacidad (DEBE):** la telemetría de uso es tratamiento de datos personales (Ley 1581 de 2012). Se DEBE informar a los usuarios qué se mide y para qué (política de tratamiento), y el dashboard DEBERÍA mostrar métricas **agregadas** (por módulo o por rol), no la actividad individual de una persona. El nombre en una sugerencia es opcional.

---

## 1. Anatomía visual

La vista ocupa todo el ancho de la pantalla (sin contenedor centrado).

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [TOPHEADER] Telemetría y adopción de la plataforma           [Periodo: últimos 30 días] │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [FILA DE KPIs]                                                                          │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│ │ Usuarios/día │  │ Usuarios/mes │  │ Tiempo sesión│  │ Exportaciones│  │ Satisfacción│ │
│ │    142       │  │     890      │  │   18,4 min   │  │  1.240 Excel │  │  4,8 / 5,0 │ │
│ └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────┐  ┌──────────────────────────────────────┐ │
│ │ MÓDULOS MÁS UTILIZADOS (ranking)         │  │ SUGERENCIAS RECIENTES                │ │
│ │ 1. Cartera y facturación  ████████ 84%   │  │ • "Permitir subir fotos sin conexión"│ │
│ │ 2. Control de accesos     ██████   62%   │  │ • "El filtro de fecha en Excel falla"│ │
│ │ 3. Inventario de insumos  ████     41%   │  │ • "Alerta sonora al terminar pesaje" │ │
│ │ 4. Configuración          █         4%   │  │                                      │ │
│ └──────────────────────────────────────────┘  └──────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [MEJORA CONTINUA] Sugerencias programadas para el siguiente sprint   [+ Programar mejora]│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

*Cifras ilustrativas.* DAU/MAU (*Daily/Monthly Active Users*) = usuarios activos por día / por mes; CSAT (*Customer Satisfaction*) = satisfacción promedio de 1 a 5.

---

## 2. Contrato de datos (TypeScript)

```typescript
export interface ModuleUsageMetric {
  moduleKey: string;
  moduleName: string;
  totalVisits: number;
  uniqueUsers: number;
  averageTimeSpentSeconds: number;
  percentageOfTotalUsage: number;
  trendDeltaPercent: number; // ej. 8.4 = +8,4 % frente al periodo anterior
}

export interface UserFeedbackEntry {
  id: string;
  userRole: string;
  userName?: string;            // opcional: la sugerencia puede ser anónima
  mostUsedFeature: string;
  suggestedImprovement: string;
  ratingScore: 1 | 2 | 3 | 4 | 5;
  submittedAtIso: string;
  status: 'pending_review' | 'scheduled_for_sprint' | 'implemented' | 'discarded';
  assignedTo?: string;
}

export interface PlatformUsageDashboardProps {
  metrics: {
    dailyActiveUsers: number;
    monthlyActiveUsers: number;
    avgSessionDurationMinutes: number;
    totalExportsExcel: number;
    overallSatisfactionScore: number;
  };
  modulesRanking: ModuleUsageMetric[];
  feedbackEntries: UserFeedbackEntry[];
  onScheduleImprovement: (feedbackId: string, sprintName: string) => Promise<void>;
}
```

Las métricas se consultan con el cliente `fastApi`/`api` y rutas del catálogo (`ENDPOINTS.TELEMETRIA.METRICAS_USO`, `ENDPOINTS.FAST.TELEMETRIA`).

---

## 3. Widget de opinión del usuario (`InAppFeedbackWidget`)

Botón flotante que abre un pequeño panel para preguntar qué función se usa más y qué mejora ahorraría tiempo. Envía con el cliente `api` y la ruta `ENDPOINTS.TELEMETRIA.FEEDBACK`.

```tsx
import React, { useCallback, useEffect, useId, useRef, useState } from 'react';
import { Lightbulb, X } from 'lucide-react';
import { api } from '@services/api';
import { ENDPOINTS } from '@services/endpoints';
import { showToast } from '@/components/ui/ToastNotification';
import './InAppFeedbackWidget.css';

export const InAppFeedbackWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [mostUsed, setMostUsed] = useState('');
  const [suggestion, setSuggestion] = useState('');
  const [rating, setRating] = useState(5);
  const [sending, setSending] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const firstFieldRef = useRef<HTMLInputElement>(null);
  const titleId = useId();
  const mostUsedId = useId();
  const suggestionId = useId();
  const ratingId = useId();

  const close = useCallback(() => {
    setIsOpen(false);
    triggerRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!isOpen) return;
    firstFieldRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [isOpen, close]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    try {
      await api.post(ENDPOINTS.TELEMETRIA.FEEDBACK, {
        most_used: mostUsed.trim(),
        suggestion: suggestion.trim(),
        rating,
      });
      showToast.success('¡Gracias! Tu sugerencia fue enviada al equipo técnico.');
      setMostUsed('');
      setSuggestion('');
      setRating(5);
      close();
    } catch {
      showToast.error('No fue posible enviar la sugerencia. Intenta de nuevo.');
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        className="feedback-floating-btn"
        onClick={() => setIsOpen(true)}
        aria-haspopup="dialog"
        aria-expanded={isOpen}
      >
        <Lightbulb size={16} aria-hidden="true" />
        <span>¿Qué podemos mejorar?</span>
      </button>

      {isOpen && (
        <div className="feedback-popover-card" role="dialog" aria-labelledby={titleId}>
          <div className="feedback-popover-header">
            <h4 id={titleId}>Mejora continua de la plataforma</h4>
            <button type="button" className="feedback-close-btn" onClick={close} aria-label="Cerrar" title="Cerrar">
              <X size={16} aria-hidden="true" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="feedback-popover-form">
            <div className="form-field">
              <label className="form-label" htmlFor={mostUsedId}>¿Qué función o módulo usas más?</label>
              <div className="input-control">
                <input
                  ref={firstFieldRef}
                  id={mostUsedId}
                  type="text"
                  value={mostUsed}
                  onChange={(e) => setMostUsed(e.target.value)}
                  placeholder="Ej. Búsqueda de facturas en cartera"
                  maxLength={200}
                  required
                />
              </div>
            </div>

            <div className="form-field">
              <label className="form-label" htmlFor={suggestionId}>¿Qué mejora te ahorraría más tiempo?</label>
              <div className="input-control">
                <textarea
                  id={suggestionId}
                  rows={3}
                  value={suggestion}
                  onChange={(e) => setSuggestion(e.target.value)}
                  placeholder="Cuéntanos tu sugerencia…"
                  maxLength={1000}
                  required
                />
              </div>
            </div>

            <div className="form-field">
              <label className="form-label" htmlFor={ratingId}>
                Satisfacción general <span>{rating} / 5</span>
              </label>
              <input
                id={ratingId}
                type="range"
                className="form-range"
                min={1}
                max={5}
                step={1}
                value={rating}
                onChange={(e) => setRating(Number(e.target.value))}
              />
            </div>

            <button type="submit" className="btn btn-primary btn-sm w-100" disabled={sending}>
              {sending ? 'Enviando…' : 'Enviar sugerencia'}
            </button>
          </form>
        </div>
      )}
    </>
  );
};
```

---

## 4. Estilos del widget (`InAppFeedbackWidget.css`)

Los campos usan las clases de formulario de `variables.css` (`.form-field`, `.form-label`, `.input-control`).

```css
.feedback-floating-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--bg-elevated);
  color: var(--brand-primary);
  border: 1px solid var(--brand-primary);
  border-radius: var(--radius-full);
  padding: 10px 18px;
  font-size: 0.85rem;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  z-index: var(--z-drawer);
}

.feedback-floating-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px var(--brand-glow);
}

.feedback-floating-btn:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.feedback-popover-card {
  position: fixed;
  bottom: 80px;
  right: 24px;
  width: 380px;
  max-width: calc(100vw - 32px);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-popover);
  z-index: var(--z-popover);
}

.feedback-popover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.feedback-popover-header h4 {
  margin: 0;
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

.feedback-close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 4px;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.feedback-close-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}
```
