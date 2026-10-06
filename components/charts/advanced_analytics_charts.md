# Suite Completa de Gráficas Analíticas Avanzadas (`AdvancedAnalyticsCharts`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este catálogo complementa las gráficas estándar de área y barras con **visualizaciones analíticas de alta densidad y complejidad operativa**: Cronogramas Gantt, Radares Spider de evaluación 360°, Diagramas de Flujo Sankey, Mapas de Calor (Heatmaps) y Medidores de Aguja (Gauge SLA).

---

## 1. Catálogo de Tipologías Soportadas

| Tipo de Gráfica | Caso de Uso Principal | Tecnologías Recomendadas |
| :--- | :--- | :--- |
| **Gantt Interactivo** | Cronograma de proyectos TIC, paradas de planta, fases de despacho. | SVG interactivo / Frappe Gantt / Canvas |
| **Radar / Spider** | Evaluación de competencias, matrices de madurez de seguridad y pentesting. | Recharts `RadarChart` / Chart.js |
| **Diagrama Sankey** | Flujos de costos, dispersión de inventario de materias primas y presupuesto. | D3.js / Recharts Sankey |
| **Mapa de Calor (Heatmap)** | Ocupación de turnos, densidad de incidentes por hora/día de la semana. | Recharts Treemap / CSS Grid Heatmap |
| **Gauge / Tacómetro** | Porcentaje de cumplimiento de SLA, salud del servidor y nivel de batería/recurso. | SVG Circular con aguja reactiva |

---

## 2. Especificación: Gráfica Radar / Spider (Auditoría y Competencias)

```typescript
export interface RadarDimension {
  subject: string; // Ej: "Autenticación", "Criptografía", "Consultas N+1"
  score: number;   // 0 - 100
  fullMark: number;
}

export interface RadarChartProps {
  data: RadarDimension[];
  title: string;
  fillColor?: string; // Por defecto: var(--color-primary, #10b981)
  strokeColor?: string;
}
```

### Renderizado con SVG Puro / Recharts:
```tsx
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

export const SecurityRadar: React.FC<RadarChartProps> = ({ data, title }) => (
  <div className="analytics-card">
    <h4 className="analytics-card__title">{title}</h4>
    <div style={{ width: '100%', height: 320 }}>
      <ResponsiveContainer>
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis dataKey="subject" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
          <Radar name="Puntaje" dataKey="score" stroke="#10b981" fill="#10b981" fillOpacity={0.4} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  </div>
);
```

---

## 3. Especificación: Medidor Gauge / Tacómetro de SLA y Metas

```tsx
export interface GaugeProps {
  value: number; // 0 a 100%
  label: string;
  sublabel?: string;
  thresholds?: { warning: number; danger: number }; // Ej: warning: 80, danger: 60
}

export const MetricGauge: React.FC<GaugeProps> = ({ value, label, sublabel }) => {
  // Cálculo de rotación de aguja (-90deg a +90deg)
  const angle = -90 + (value / 100) * 180;
  const color = value >= 90 ? '#10b981' : value >= 75 ? '#f59e0b' : '#ef4444';

  return (
    <div className="gauge-widget">
      <svg viewBox="0 0 200 120" className="gauge-svg">
        {/* Arco de fondo */}
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="16" strokeLinecap="round" />
        {/* Arco activo */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray="251.2"
          strokeDashoffset={251.2 - (251.2 * value) / 100}
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="gauge-value" style={{ color }}>{value}%</div>
      <div className="gauge-label">{label}</div>
      {sublabel && <div className="gauge-sublabel">{sublabel}</div>}
    </div>
  );
};
```

---

## 4. Especificación: Cronograma Interactivo Gantt

```typescript
export interface GanttTask {
  id: string;
  title: string;
  startDate: string; // ISO AAAA-MM-DD
  endDate: string;
  progressPercent: number; // 0 - 100
  assignedTo?: string;
  status: 'planned' | 'in_progress' | 'completed' | 'delayed';
  dependencies?: string[]; // IDs de tareas predecesoras
}
```
- **Capacidades**: Arrastre interactivo de bordes para extender fechas, zoom por días/semanas/meses, coloración por estado de cumplimiento y barra vertical roja indicadora del día de hoy (*Today line*).
