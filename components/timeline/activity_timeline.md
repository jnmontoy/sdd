# Línea de Tiempo de Auditoría y Trazabilidad (`ActivityTimeline`)
## SDD Joli Foods — Spec-Driven Development

Muestra en orden cronológico la historia de un registro: cambios de estado, acciones de auditoría y novedades operativas, con quién lo hizo, cuándo y qué cambió.

---

## 1. Contrato de datos (TypeScript)

```typescript
export type TimelineStatus = 'success' | 'warning' | 'danger' | 'info';

export interface TimelineEvent {
  id: string;
  timestampIso: string;
  title: string;
  description?: string;
  operator: {
    name: string;
    avatarUrl?: string;
    role: string;
  };
  category: 'security' | 'operational' | 'financial' | 'system';
  status: TimelineStatus;
  diffData?: { field: string; oldValue: string | number | null; newValue: string | number | null }[];
  attachments?: { name: string; url: string }[]; // URL servida por el backend con control de acceso
}

export interface ActivityTimelineProps {
  events: TimelineEvent[];        // ya ordenados (más reciente primero)
  filterCategories?: TimelineEvent['category'][];
}
```

---

## 2. Implementación de referencia (`ActivityTimeline.tsx`)

Lista semántica (`<ol>`), fecha en `<time>` y textos como contenido de texto (nunca `dangerouslySetInnerHTML`: las descripciones pueden venir de usuarios).

```tsx
import React, { useMemo } from 'react';
import type { ActivityTimelineProps } from './timeline.types';
import './ActivityTimeline.css';

const dateFormatter = new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium', timeStyle: 'short' });

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ events, filterCategories }) => {
  const visible = useMemo(
    () => (filterCategories?.length ? events.filter((e) => filterCategories.includes(e.category)) : events),
    [events, filterCategories]
  );

  if (visible.length === 0) {
    return <p className="activity-timeline__empty">No hay actividad registrada.</p>;
  }

  return (
    <ol className="activity-timeline" aria-label="Historial de actividad">
      {visible.map((ev) => (
        <li key={ev.id} className={`activity-timeline__item is-${ev.status}`}>
          <span className="activity-timeline__node" aria-hidden="true" />
          <div className="activity-timeline__content">
            <div className="activity-timeline__header">
              <span className="activity-timeline__title">{ev.title}</span>
              <time className="activity-timeline__time" dateTime={ev.timestampIso}>
                {dateFormatter.format(new Date(ev.timestampIso))}
              </time>
            </div>
            <p className="activity-timeline__meta">
              {ev.operator.name} · {ev.operator.role}
            </p>
            {ev.description && <p className="activity-timeline__description">{ev.description}</p>}
            {ev.diffData && ev.diffData.length > 0 && (
              <dl className="activity-timeline__diff">
                {ev.diffData.map((d) => (
                  <div key={d.field} className="activity-timeline__diff-row">
                    <dt>{d.field}</dt>
                    <dd>
                      <del>{String(d.oldValue ?? '—')}</del> → <ins>{String(d.newValue ?? '—')}</ins>
                    </dd>
                  </div>
                ))}
              </dl>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
};
```

---

## 3. Estilos (`ActivityTimeline.css`)

```css
.activity-timeline {
  position: relative;
  padding: 16px 0 16px 32px;
  margin: 0;
  list-style: none;
}

/* Línea vertical */
.activity-timeline::before {
  content: '';
  position: absolute;
  top: 24px;
  bottom: 24px;
  left: 11px;
  width: 2px;
  background: var(--border-subtle);
}

.activity-timeline__item {
  --tl-accent: var(--brand-primary);
  position: relative;
  margin-bottom: 24px;
}

.activity-timeline__item:last-child { margin-bottom: 0; }

.activity-timeline__item.is-success { --tl-accent: var(--status-success); }
.activity-timeline__item.is-warning { --tl-accent: var(--status-warning); }
.activity-timeline__item.is-danger  { --tl-accent: var(--status-error); }
.activity-timeline__item.is-info    { --tl-accent: var(--accent-blue); }

/* Nodo sobre la línea */
.activity-timeline__node {
  position: absolute;
  left: -32px;
  top: 4px;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  background: var(--bg-card);
  border: 2px solid var(--tl-accent);
  z-index: 2;
}

.activity-timeline__content {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 14px 18px;
}

.activity-timeline__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: 6px;
}

.activity-timeline__title {
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  font-size: 0.95rem;
}

.activity-timeline__time,
.activity-timeline__meta {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0;
}

.activity-timeline__description {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 6px 0 0;
}

.activity-timeline__diff {
  margin: 8px 0 0;
  font-size: var(--font-size-xs);
}

.activity-timeline__diff-row {
  display: flex;
  gap: var(--space-2);
}

.activity-timeline__diff dt {
  font-weight: var(--font-weight-semibold);
  color: var(--text-secondary);
}

.activity-timeline__diff dd { margin: 0; color: var(--text-secondary); }
.activity-timeline__diff del { color: var(--status-error); }
.activity-timeline__diff ins { color: var(--status-success); text-decoration: none; }

.activity-timeline__empty {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}
```
