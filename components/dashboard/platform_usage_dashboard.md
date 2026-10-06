# Dashboard de Uso de Plataforma, Adopción y Feedback (`PlatformUsageDashboard`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este componente proporciona un **panel de control para el monitoreo de adopción de la plataforma**, rastreo del comportamiento de los usuarios (qué módulos se visitan más, qué acciones se repiten) y recolección activa de sugerencias para programar **ciclos de mejora continua**.

---

## 1. Anatomía Visual y Secciones del Dashboard

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [TOPHEADER] Telemetría y Adopción de Plataforma                   [Periodo: Últimos 30d] │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [KPI ROW]                                                                              │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│ │ DAU Activos  │  │ MAU Mensual  │  │ Tiempo Sesión│  │ Exportaciones│  │ Nivel CSAT │ │
│ │  142 usuarios│  │  890 usuarios│  │   18.4 min   │  │  1,240 Excel │  │ 4.8 / 5.0  │ │
│ └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────┐  ┌──────────────────────────────────────┐ │
│ │ 📊 MÓDULOS MÁS UTILIZADOS (Ranking)      │  │ 💬 RESULTADOS DE ENCUESTAS & MEJORAS │ │
│ │ 1. Cartera & Facturación  ████████ 84%   │  │ • "Facilitar subida de fotos offline"│ │
│ │ 2. Despacho & Porterías   ██████   62%   │  │ • "El filtro de fecha en Excel vuela"│ │
│ │ 3. Inventario Fruta       ████     41%   │  │ • "Agregar alerta sonora en pesaje"  │ │
│ │ 4. Configuración Sistema  █         4%   │  │                                      │ │
│ └──────────────────────────────────────────┘  └──────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [ROADMAPPING] Ciclo de Mejora Programado: Sprint #14 (Planificación Técnica / Senior)  │
│ [📅 Próximo Despliegue de Mejoras: 15 de Noviembre]   [+ Programar Tarea de Mejora]   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Contrato de Datos de Telemetría (TypeScript)

```typescript
export interface ModuleUsageMetric {
  moduleKey: string;
  moduleName: string;
  totalVisits: number;
  uniqueUsers: number;
  averageTimeSpentSeconds: number;
  percentageOfTotalUsage: number;
  trendDeltaPercent: number; // Ej. +8.4%
}

export interface UserFeedbackEntry {
  id: string;
  userRole: string;
  userName?: string;
  mostUsedFeature: string;
  suggestedImprovement: string;
  ratingScore: number; // 1 a 5
  submittedAtIso: string;
  status: 'pending_review' | 'scheduled_for_sprint' | 'implemented' | 'discarded';
  assignedSenior?: string;
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

---

## 3. Widget Flotante de Escucha Activa al Usuario (`InAppFeedbackWidget`)

Este subcomponente se inyecta en el pie de página de la aplicación o en el menú de perfil para consultar de forma no invasiva qué funciones usa más la persona:

```tsx
import React, { useState } from 'react';

export const InAppFeedbackWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [mostUsed, setMostUsed] = useState('');
  const [suggestion, setSuggestion] = useState('');
  const [rating, setRating] = useState(5);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Envío del feedback al backend
    await fetch('/api/v1/telemetria/feedback/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mostUsed, suggestion, rating }),
    });
    setIsOpen(false);
  };

  return (
    <>
      <button
        type="button"
        className="feedback-floating-btn"
        onClick={() => setIsOpen(true)}
        title="Danos tu opinión para mejorar la plataforma"
      >
        💡 ¿Qué podemos mejorar?
      </button>

      {isOpen && (
        <div className="feedback-popover-card">
          <div className="feedback-popover-header">
            <h4>Mejora Continua de la Plataforma</h4>
            <button type="button" onClick={() => setIsOpen(false)}>✕</button>
          </div>
          <form onSubmit={handleSubmit} className="feedback-popover-form">
            <label>¿Qué funcionalidad o módulo es el que más utilizas?</label>
            <input
              type="text"
              className="joli-input"
              value={mostUsed}
              onChange={(e) => setMostUsed(e.target.value)}
              placeholder="Ej. Búsqueda de facturas en cartera"
              required
            />

            <label>¿Qué cambio o mejora te ahorraría más tiempo de trabajo?</label>
            <textarea
              className="joli-input"
              rows={3}
              value={suggestion}
              onChange={(e) => setSuggestion(e.target.value)}
              placeholder="Cuéntanos tu sugerencia..."
              required
            />

            <button type="submit" className="btn btn--primary btn--sm">
              Enviar sugerencia al equipo técnico
            </button>
          </form>
        </div>
      )}
    </>
  );
};
```

---

## 4. Estilos CSS Canónicos (`variables.css`)

```css
.feedback-floating-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: var(--color-bg-surface-elevated, #1e293b);
  color: var(--color-primary, #10b981);
  border: 1px solid var(--color-primary, #10b981);
  border-radius: 30px;
  padding: 10px 18px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  z-index: 1000;
}

.feedback-floating-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.feedback-popover-card {
  position: fixed;
  bottom: 80px;
  right: 24px;
  width: 380px;
  background: var(--color-bg-surface, #0f172a);
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.12));
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 1001;
}
```
