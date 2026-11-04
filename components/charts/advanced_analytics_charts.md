# Gráficas Analíticas Avanzadas (`AdvancedAnalyticsCharts`)
## SDD Joli Foods — Spec-Driven Development

Complementa las gráficas básicas de [`analytics_charts.md`](./analytics_charts.md) con visualizaciones de mayor densidad: cronogramas Gantt, radar (araña) para evaluaciones, diagramas Sankey (flujos), mapas de calor y medidores tipo velocímetro (*gauge*) para metas o SLA (*Service Level Agreement*: nivel de servicio acordado).

Todas DEBEN usar los tokens de color de `variables.css` (`--chart-*`, `--status-*`) y cumplir las reglas de accesibilidad de la suite básica (`role="img"`, `aria-label`, leyenda con texto).

---

## 1. Catálogo de tipos

| Tipo | Caso de uso | Tecnología sugerida |
| :--- | :--- | :--- |
| **Gantt** | Cronograma de proyectos, paradas de planta, fases de despacho. | SVG propio o Frappe Gantt |
| **Radar / araña** | Evaluación de competencias, matrices de madurez. | Recharts `RadarChart` |
| **Sankey** | Flujos de costos, consumo de materias primas, presupuesto. | Recharts `Sankey` o D3 |
| **Mapa de calor** | Ocupación de turnos, incidentes por hora y día. | Rejilla CSS (`display: grid`) |
| **Gauge** | Cumplimiento de metas o SLA, uso de un recurso. | SVG con arco |

---

## 2. Radar / araña (evaluaciones)

```typescript
export interface RadarDimension {
  subject: string; // ej. "Autenticación", "Criptografía", "Consultas N+1"
  score: number;   // 0 - 100
}

export interface RadarChartProps {
  data: RadarDimension[];
  title: string;
  color?: string; // por defecto 'var(--chart-primary)'
}
```

```tsx
import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

export const ScoreRadar: React.FC<RadarChartProps> = ({ data, title, color = 'var(--chart-primary)' }) => (
  <figure className="joli-chart-card">
    <figcaption className="joli-chart-title">{title}</figcaption>
    <div style={{ width: '100%', height: 320 }} role="img" aria-label={`${title}: ${data.map((d) => `${d.subject} ${d.score}`).join(', ')}`}>
      <ResponsiveContainer>
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="var(--chart-grid)" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--chart-text)', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="var(--chart-grid)" tick={{ fill: 'var(--chart-text)', fontSize: 10 }} />
          <Radar name="Puntaje" dataKey="score" stroke={color} fill={color} fillOpacity={0.35} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  </figure>
);
```

---

## 3. Gauge para metas y SLA

Los umbrales son configurables (antes estaban fijos en el código e ignoraban la prop). El valor se limita a 0–100.

```tsx
import React from 'react';

export interface GaugeProps {
  value: number;  // 0 a 100 (%)
  label: string;
  sublabel?: string;
  /** Desde qué % el valor es "aceptable" (ámbar) y "bueno" (verde). */
  thresholds?: { warning: number; good: number };
}

// Longitud del semicírculo de radio 80: π × 80
const ARC_LENGTH = Math.PI * 80;

export const MetricGauge: React.FC<GaugeProps> = ({
  value,
  label,
  sublabel,
  thresholds = { warning: 75, good: 90 },
}) => {
  const pct = Math.min(Math.max(value, 0), 100);
  const color =
    pct >= thresholds.good ? 'var(--status-success)' : pct >= thresholds.warning ? 'var(--status-warning)' : 'var(--status-error)';

  return (
    <div className="gauge-widget" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={pct} aria-label={label}>
      <svg viewBox="0 0 200 120" className="gauge-svg" aria-hidden="true">
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="var(--border-subtle)" strokeWidth="16" strokeLinecap="round" />
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={ARC_LENGTH}
          strokeDashoffset={ARC_LENGTH * (1 - pct / 100)}
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="gauge-value" style={{ color }}>{pct.toLocaleString('es-CO', { maximumFractionDigits: 1 })}%</div>
      <div className="gauge-label">{label}</div>
      {sublabel && <div className="gauge-sublabel">{sublabel}</div>}
    </div>
  );
};
```

```css
.gauge-widget { display: flex; flex-direction: column; align-items: center; }
.gauge-svg { width: 100%; max-width: 220px; }
.gauge-value { font-size: var(--font-size-2xl); font-weight: var(--font-weight-extrabold); margin-top: -1.5rem; }
.gauge-label { font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); color: var(--text-primary); }
.gauge-sublabel { font-size: var(--font-size-xs); color: var(--text-muted); }
```

---

## 4. Cronograma Gantt (contrato)

```typescript
export interface GanttTask {
  id: string;
  title: string;
  startDate: string;        // AAAA-MM-DD
  endDate: string;          // AAAA-MM-DD, >= startDate
  progressPercent: number;  // 0 - 100
  assignedTo?: string;
  status: 'planned' | 'in_progress' | 'completed' | 'delayed';
  dependencies?: string[];  // ids de tareas predecesoras
}
```

- **Capacidades esperadas**: zoom por días/semanas/meses, color por estado (tokens `--status-*`), línea vertical del día de hoy y, opcionalmente, arrastre de bordes para cambiar fechas.
- Si se permite arrastrar, el cambio DEBE confirmarse con el backend (que valida dependencias y permisos) y la acción DEBE tener alternativa con teclado (editar fechas desde el panel lateral derecho).
