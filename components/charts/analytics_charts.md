# Especificación de Componente: Suite de Gráficas y Analítica Visual (`AnalyticsCharts`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

La suite `AnalyticsCharts` proporciona un conjunto de componentes de visualización de datos de alto impacto estético, totalmente alineados con la identidad visual corporativa de Jolifoods y gobernados por los tokens de color de `variables.css`.

Implementa renderizado SVG vectorial ultraligero y receptivo, compatible con cualquier framework moderno (React con SVG nativo o integración con `recharts`), soporte nativo para **Modo Noche y Modo Día**, tooltips interactivos con efecto glassmorphism, y curvaturas suaves con gradientes de desvanecimiento vertical.

---

### 1. Paleta de Tokens Cromáticos para Gráficas

Las gráficas utilizan exclusivamente los acentos semánticos corporativos para garantizar armonía visual y máxima legibilidad:

```css
:root {
  --chart-primary: #10B981;    /* Verde Esmeralda Institucional */
  --chart-secondary: #3B82F6;  /* Azul Tecnológico */
  --chart-warning: #F59E0B;    /* Ámbar Alerta */
  --chart-danger: #F43F5E;     /* Rosa / Rubí Crítico */
  --chart-accent: #06B6D4;     /* Cian Innovación */
  --chart-purple: #8B5CF6;     /* Violeta Analítica */
  --chart-grid: rgba(226, 232, 240, 0.8);
  --chart-text: #64748B;
  --chart-tooltip-bg: rgba(15, 23, 42, 0.92);
  --chart-tooltip-border: rgba(255, 255, 255, 0.15);
}

[data-theme="dark"] {
  --chart-grid: rgba(51, 65, 85, 0.5);
  --chart-text: #94A3B8;
  --chart-tooltip-bg: rgba(30, 41, 59, 0.95);
  --chart-tooltip-border: rgba(255, 255, 255, 0.1);
}
```

---

### 2. Variantes de Visualización Disponibles

1. **`AreaGradientChart` (Tendencias y Series Temporales)**:
   - Curva Bézier suavizada (`stroke-width="2.5"`).
   - Área rellena con `<linearGradient>` de opacidad decreciente (0.35 superior a 0.02 base).
   - Eje X e Y adaptativos con rejilla punteada sutil.
   - Crosshair vertical interactivo en hover con tooltip flotante.
2. **`RoundedBarChart` (Comparativa Categórica / Mensual)**:
   - Barras verticales con bordes superiores redondeados (`rx="6"`).
   - Efecto hover de iluminación y tooltip informativo.
3. **`DonutDistributionChart` (Distribución Porcentual / Mix de Cartera)**:
   - Anillo concéntrico con grosor optimizado (`stroke-width="22"`).
   - Métrica total y etiqueta descriptiva en el centro del hueco.
   - Leyenda lateral interactiva con bullets cromáticos y porcentajes.
4. **`MiniSparkline` (Micro-gráfica de Tendencia)**:
   - Gráfica compacta (100px × 32px) sin ejes ni ruido visual.
   - Diseñada para incrustarse dentro de tarjetas KPI (`KPICards`) o filas de `DataTable`.

---

### 3. Implementación TypeScript / React

```tsx
// src/components/charts/AnalyticsCharts.tsx
import React, { useState, useId } from 'react';
import './AnalyticsCharts.css';

// ==============================================================================
// 1. Gráfica de Área con Gradiente Suave (AreaGradientChart)
// ==============================================================================
export interface DataPoint {
  label: string;
  value: number;
}

export interface AreaGradientChartProps {
  data: DataPoint[];
  height?: number;
  color?: string;
  title?: string;
  subtitle?: string;
  valuePrefix?: string;
  valueSuffix?: string;
}

export const AreaGradientChart: React.FC<AreaGradientChartProps> = ({
  data,
  height = 240,
  color = 'var(--chart-primary, #10B981)',
  title,
  subtitle,
  valuePrefix = '',
  valueSuffix = '',
}) => {
  const gradientId = useId();
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!data || data.length === 0) return null;

  const width = 600;
  const padding = { top: 20, right: 20, bottom: 35, left: 45 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const values = data.map((d) => d.value);
  const minVal = Math.min(...values) * 0.9;
  const maxVal = Math.max(...values) * 1.05 || 1;

  const getX = (index: number) => padding.left + (index / (data.length - 1)) * innerWidth;
  const getY = (val: number) => padding.top + innerHeight - ((val - minVal) / (maxVal - minVal)) * innerHeight;

  // Generar curva Bézier continua (Catmull-Rom simplificado)
  const points = data.map((d, i) => `${getX(i)},${getY(d.value)}`);
  const pathD = points.reduce((acc, curr, i, arr) => {
    if (i === 0) return `M ${curr}`;
    const prev = arr[i - 1].split(',').map(Number);
    const [currX, currY] = curr.split(',').map(Number);
    const cpX1 = prev[0] + (currX - prev[0]) / 2;
    const cpX2 = currX - (currX - prev[0]) / 2;
    return `${acc} C ${cpX1} ${prev[1]}, ${cpX2} ${currY}, ${currX} ${currY}`;
  }, '');

  const areaD = `${pathD} L ${getX(data.length - 1)},${padding.top + innerHeight} L ${padding.left},${padding.top + innerHeight} Z`;

  return (
    <div className="joli-chart-card">
      {(title || subtitle) && (
        <div className="joli-chart-header">
          {title && <h3 className="joli-chart-title">{title}</h3>}
          {subtitle && <p className="joli-chart-subtitle">{subtitle}</p>}
        </div>
      )}

      <div className="joli-chart-viewport" style={{ height }}>
        <svg viewBox={`0 0 ${width} ${height}`} className="joli-chart-svg" preserveAspectRatio="none">
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.35" />
              <stop offset="90%" stopColor={color} stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {/* Rejilla de Fondo */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
            const y = padding.top + innerHeight * pct;
            return (
              <line
                key={i}
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                className="joli-chart-grid-line"
              />
            );
          })}

          {/* Área con Gradiente y Línea de Contorno */}
          <path d={areaD} fill={`url(#${gradientId})`} />
          <path d={pathD} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" />

          {/* Ejes y Etiquetas */}
          {data.map((d, i) => {
            const x = getX(i);
            const isHovered = hoverIndex === i;
            return (
              <g key={i}>
                <text
                  x={x}
                  y={height - 10}
                  className={`joli-chart-axis-text ${isHovered ? 'is-active' : ''}`}
                  textAnchor="middle"
                >
                  {d.label}
                </text>
                {/* Zona de interacción invisible */}
                <rect
                  x={x - innerWidth / (data.length * 2)}
                  y={padding.top}
                  width={innerWidth / data.length}
                  height={innerHeight}
                  fill="transparent"
                  onMouseEnter={() => setHoverIndex(i)}
                  onMouseLeave={() => setHoverIndex(null)}
                  className="joli-chart-hitbox"
                />
                {isHovered && (
                  <>
                    <line
                      x1={x}
                      y1={padding.top}
                      x2={x}
                      y2={padding.top + innerHeight}
                      stroke={color}
                      strokeWidth="1.5"
                      strokeDasharray="4 3"
                    />
                    <circle cx={x} cy={getY(d.value)} r="5" fill="#FFFFFF" stroke={color} strokeWidth="2.5" />
                  </>
                )}
              </g>
            );
          })}
        </svg>

        {/* Tooltip Flotante */}
        {hoverIndex !== null && (
          <div
            className="joli-chart-tooltip"
            style={{
              left: `${(getX(hoverIndex) / width) * 100}%`,
              top: `${(getY(data[hoverIndex].value) / height) * 100}%`,
            }}
          >
            <div className="joli-tooltip-label">{data[hoverIndex].label}</div>
            <div className="joli-tooltip-value">
              {valuePrefix}{data[hoverIndex].value.toLocaleString('es-CO')}{valueSuffix}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ==============================================================================
// 2. Gráfica de Barras Redondeadas (RoundedBarChart)
// ==============================================================================
export interface RoundedBarChartProps {
  data: DataPoint[];
  height?: number;
  color?: string;
  title?: string;
  subtitle?: string;
  valuePrefix?: string;
  valueSuffix?: string;
}

export const RoundedBarChart: React.FC<RoundedBarChartProps> = ({
  data,
  height = 240,
  color = 'var(--chart-secondary, #3B82F6)',
  title,
  subtitle,
  valuePrefix = '',
  valueSuffix = '',
}) => {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!data || data.length === 0) return null;

  const width = 600;
  const padding = { top: 20, right: 20, bottom: 35, left: 40 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;

  const maxVal = Math.max(...data.map((d) => d.value)) * 1.1 || 1;
  const barWidth = Math.min(innerWidth / data.length - 12, 42);

  return (
    <div className="joli-chart-card">
      {(title || subtitle) && (
        <div className="joli-chart-header">
          {title && <h3 className="joli-chart-title">{title}</h3>}
          {subtitle && <p className="joli-chart-subtitle">{subtitle}</p>}
        </div>
      )}

      <div className="joli-chart-viewport" style={{ height }}>
        <svg viewBox={`0 0 ${width} ${height}`} className="joli-chart-svg" preserveAspectRatio="none">
          {[0, 0.33, 0.66, 1].map((pct, i) => {
            const y = padding.top + innerHeight * pct;
            return <line key={i} x1={padding.left} y1={y} x2={width - padding.right} y2={y} className="joli-chart-grid-line" />;
          })}

          {data.map((d, i) => {
            const x = padding.left + (i + 0.5) * (innerWidth / data.length) - barWidth / 2;
            const barHeight = (d.value / maxVal) * innerHeight;
            const y = padding.top + innerHeight - barHeight;
            const isHovered = hoverIndex === i;

            return (
              <g
                key={i}
                onMouseEnter={() => setHoverIndex(i)}
                onMouseLeave={() => setHoverIndex(null)}
                className="joli-bar-group"
              >
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  rx="6"
                  fill={color}
                  className={`joli-bar-rect ${isHovered ? 'is-active' : ''}`}
                />
                <text
                  x={x + barWidth / 2}
                  y={height - 10}
                  className={`joli-chart-axis-text ${isHovered ? 'is-active' : ''}`}
                  textAnchor="middle"
                >
                  {d.label}
                </text>
              </g>
            );
          })}
        </svg>

        {hoverIndex !== null && (
          <div
            className="joli-chart-tooltip"
            style={{
              left: `${((padding.left + (hoverIndex + 0.5) * (innerWidth / data.length)) / width) * 100}%`,
              top: `${((padding.top + innerHeight - (data[hoverIndex].value / maxVal) * innerHeight) / height) * 100}%`,
            }}
          >
            <div className="joli-tooltip-label">{data[hoverIndex].label}</div>
            <div className="joli-tooltip-value">
              {valuePrefix}{data[hoverIndex].value.toLocaleString('es-CO')}{valueSuffix}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ==============================================================================
// 3. Gráfica Donut de Distribución (DonutDistributionChart)
// ==============================================================================
export interface DonutSegment {
  label: string;
  value: number;
  color: string;
}

export interface DonutDistributionChartProps {
  data: DonutSegment[];
  size?: number;
  title?: string;
  subtitle?: string;
  centerLabel?: string;
}

export const DonutDistributionChart: React.FC<DonutDistributionChartProps> = ({
  data,
  size = 200,
  title,
  subtitle,
  centerLabel = 'Total',
}) => {
  const total = data.reduce((acc, curr) => acc + curr.value, 0) || 1;
  const strokeWidth = 22;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  let accumulatedPercent = 0;

  return (
    <div className="joli-chart-card">
      {(title || subtitle) && (
        <div className="joli-chart-header">
          {title && <h3 className="joli-chart-title">{title}</h3>}
          {subtitle && <p className="joli-chart-subtitle">{subtitle}</p>}
        </div>
      )}

      <div className="joli-donut-container">
        <div className="joli-donut-circle-box" style={{ width: size, height: size }}>
          <svg width={size} height={size} className="joli-donut-svg">
            {data.map((item, idx) => {
              const percent = item.value / total;
              const strokeDasharray = `${circumference * percent} ${circumference * (1 - percent)}`;
              const strokeDashoffset = -circumference * accumulatedPercent;
              accumulatedPercent += percent;

              return (
                <circle
                  key={idx}
                  cx={size / 2}
                  cy={size / 2}
                  r={radius}
                  fill="transparent"
                  stroke={item.color}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDasharray}
                  strokeDashoffset={strokeDashoffset}
                  className="joli-donut-segment"
                />
              );
            })}
          </svg>
          <div className="joli-donut-center-badge">
            <span className="joli-donut-total">{total.toLocaleString('es-CO')}</span>
            <span className="joli-donut-center-sub">{centerLabel}</span>
          </div>
        </div>

        {/* Leyenda Lateral */}
        <div className="joli-donut-legend">
          {data.map((item, idx) => {
            const pct = Math.round((item.value / total) * 100);
            return (
              <div key={idx} className="joli-donut-legend-item">
                <span className="joli-legend-dot" style={{ backgroundColor: item.color }} />
                <span className="joli-legend-label">{item.label}</span>
                <span className="joli-legend-value">{pct}%</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// ==============================================================================
// 4. Mini-Sparkline de Tendencia (MiniSparkline)
// ==============================================================================
export interface MiniSparklineProps {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
}

export const MiniSparkline: React.FC<MiniSparklineProps> = ({
  data,
  color = 'var(--chart-primary, #10B981)',
  width = 90,
  height = 28,
}) => {
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data) || 1;
  const padding = 2;

  const points = data
    .map((val, i) => {
      const x = padding + (i / (data.length - 1)) * (width - padding * 2);
      const y = height - padding - ((val - min) / (max - min || 1)) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg width={width} height={height} className="joli-sparkline-svg">
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};
```

---

### 4. Estilos CSS (`AnalyticsCharts.css`)

```css
.joli-chart-card {
  background: var(--bg-card, #FFFFFF);
  border: 1px solid var(--border-subtle, #E2E8F0);
  border-radius: var(--radius-xl, 14px);
  padding: 1.25rem 1.5rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

[data-theme="dark"] .joli-chart-card {
  background: var(--bg-card, #1E293B);
  border-color: var(--border-subtle, #334155);
}

.joli-chart-header {
  margin-bottom: 1.25rem;
}

.joli-chart-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  letter-spacing: -0.01em;
}

.joli-chart-subtitle {
  margin: 4px 0 0 0;
  font-size: 0.8rem;
  color: var(--text-muted, #64748B);
}

.joli-chart-viewport {
  position: relative;
  width: 100%;
}

.joli-chart-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.joli-chart-grid-line {
  stroke: var(--chart-grid, rgba(226, 232, 240, 0.8));
  stroke-dasharray: 4 4;
}

.joli-chart-axis-text {
  font-size: 11px;
  fill: var(--chart-text, #64748B);
  transition: fill 0.15s ease;
}

.joli-chart-axis-text.is-active {
  fill: var(--text-primary, #0F172A);
  font-weight: 600;
}

.joli-chart-hitbox {
  cursor: crosshair;
}

.joli-bar-rect {
  transition: opacity 0.15s, transform 0.15s;
  cursor: pointer;
}

.joli-bar-rect:hover,
.joli-bar-rect.is-active {
  opacity: 0.85;
}

/* Tooltip Flotante Estilo Jolifoods */
.joli-chart-tooltip {
  position: absolute;
  transform: translate(-50%, -125%);
  background: var(--chart-tooltip-bg, rgba(15, 23, 42, 0.94));
  border: 1px solid var(--chart-tooltip-border, rgba(255, 255, 255, 0.15));
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #FFFFFF;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 12px;
  pointer-events: none;
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.4);
  white-space: nowrap;
  z-index: 50;
  animation: tooltipFade 0.15s ease-out;
}

@keyframes tooltipFade {
  from { opacity: 0; transform: translate(-50%, -115%); }
  to { opacity: 1; transform: translate(-50%, -125%); }
}

.joli-tooltip-label {
  font-size: 10.5px;
  color: #94A3B8;
  margin-bottom: 2px;
}

.joli-tooltip-value {
  font-size: 13px;
  font-weight: 700;
  color: #F8FAFC;
}

/* Donut Chart Layout */
.joli-donut-container {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 1.5rem;
  padding: 0.5rem 0;
}

.joli-donut-circle-box {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.joli-donut-svg {
  transform: rotate(-90deg);
}

.joli-donut-segment {
  transition: stroke-width 0.2s ease, opacity 0.2s ease;
  cursor: pointer;
}

.joli-donut-segment:hover {
  stroke-width: 25;
  opacity: 0.9;
}

.joli-donut-center-badge {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.joli-donut-total {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary, #0F172A);
  line-height: 1;
}

.joli-donut-center-sub {
  font-size: 0.75rem;
  color: var(--text-muted, #64748B);
  margin-top: 4px;
}

.joli-donut-legend {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.joli-donut-legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.joli-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.joli-legend-label {
  color: var(--text-secondary, #475569);
  flex: 1;
}

.joli-legend-value {
  font-weight: 600;
  color: var(--text-primary, #0F172A);
}

.joli-sparkline-svg {
  overflow: visible;
  display: inline-block;
  vertical-align: middle;
}
```
