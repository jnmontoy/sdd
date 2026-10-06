# Línea de Tiempo de Auditoría y Trazabilidad (`ActivityTimeline`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este componente renderiza cronológicamente la historia de eventos, cambios de estado en pedidos, registros de auditoría y novedades operativas, proporcionando trazabilidad visual inmediata con avatares de usuario y metadatos expandibles.

---

## 1. Contrato de Datos en TypeScript

```typescript
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
  status: 'success' | 'warning' | 'danger' | 'info';
  diffData?: {
    field: string;
    oldValue: string | number;
    newValue: string | number;
  }[];
  attachments?: {
    name: string;
    url: string;
  }[];
}

export interface ActivityTimelineProps {
  events: TimelineEvent[];
  isCollapsible?: boolean;
  filterCategories?: string[];
}
```

---

## 2. Estilos CSS Canónicos (`variables.css`)

```css
.activity-timeline {
  position: relative;
  padding: 16px 0 16px 32px;
  list-style: none;
}

/* Línea conectora vertical */
.activity-timeline::before {
  content: '';
  position: absolute;
  top: 24px;
  bottom: 24px;
  left: 11px;
  width: 2px;
  background: var(--color-border-subtle, rgba(255, 255, 255, 0.1));
}

.activity-timeline__item {
  position: relative;
  margin-bottom: 24px;
}

.activity-timeline__item:last-child {
  margin-bottom: 0;
}

/* Nodo circular en la línea */
.activity-timeline__node {
  position: absolute;
  left: -32px;
  top: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-bg-surface, #1e293b);
  border: 2px solid var(--color-primary, #10b981);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  z-index: 2;
}

.activity-timeline__content {
  background: var(--color-bg-surface, #1e293b);
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.06));
  border-radius: 8px;
  padding: 14px 18px;
}

.activity-timeline__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.activity-timeline__title {
  font-weight: 600;
  color: var(--color-text-main, #f8fafc);
  font-size: 0.95rem;
}

.activity-timeline__time {
  font-size: 0.78rem;
  color: var(--color-text-muted, #94a3b8);
}
```
