# Componente: Panel Desplegable de Multi-Notificaciones (`NotificationBellPopover`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de tiendita y vibra (campana del TopHeader). Aquí se describe de forma genérica.

El **NotificationBellPopover** es el panel que se despliega al presionar la campana (`Bell`) en el **TopHeader**. Agrupa alertas operativas, pedidos, solicitudes o alertas de inventario en **pestañas por categoría**, muestra contadores de no leídas y permite acciones rápidas en línea (ver detalle, aprobar, rechazar, marcar como leída).

---

## 1. Características

1. **Activador en TopHeader**: botón circular con icono `Bell` y badge (`.bell-badge-count`) con el total de no leídas. El botón DEBE tener `aria-label`, `aria-haspopup` y `aria-expanded`.
2. **Pestañas por categoría (`.joli-notif-tabs`)**: alternan entre tipos de notificación (ej. *Solicitudes*, *Stock crítico*, *Novedades*). Cada pestaña muestra su contador. La pestaña especial `todas` muestra todo.
3. **Lista con scroll propio (`.joli-notif-body`)**: altura máxima 360px; las no leídas llevan borde de acento; icono según severidad (crítico, advertencia, info, éxito); tiempo relativo (*"Hace 15 min"*).
4. **Acciones rápidas por notificación** (solo las que traiga `item.actions`): ver detalle en el **panel lateral derecho** (`Eye`), aprobar (`CheckCircle`), rechazar (`XCircle`). Se agrupan en un `btn-group` con `aria-label` por botón.
5. **Estado vacío**: icono `CheckCircle` y mensaje *"Todo está al día"*.
6. **Pie**: *"Marcar todas como leídas"* y *"Ver todas"* (navegación a la vista completa).
7. **Cierre**: tecla `Escape` (devuelve el foco a la campana) o clic fuera del panel.
8. **Origen de los datos**: el componente es de presentación. La carga y el refresco periódico los hace el contenedor con [`useSmartPolling`](../realtime/js_polling_architecture.md) y el cliente HTTP `api` (nunca `fetch` directo con tokens).

---

## 2. Contrato de datos (TypeScript)

```typescript
export type NotificationSeverity = 'critical' | 'warning' | 'info' | 'success';
export type NotificationActionType = 'approve' | 'deny' | 'view';

export interface NotificationItem {
  id: string | number;
  category: string;            // ej. 'stock', 'solicitudes', 'alertas'
  title: string;
  detail: string;
  timestamp: string;           // ISO-8601
  timeAgo: string;             // texto ya formateado ("Hace 15 min")
  severity: NotificationSeverity;
  isRead: boolean;
  actions?: NotificationActionType[]; // acciones permitidas para este ítem
  metadata?: Record<string, unknown>;
}

export interface NotificationCategoryTab {
  id: string;                  // 'todas' muestra todas las categorías
  label: string;
}

export interface NotificationBellPopoverProps {
  notifications: NotificationItem[];
  categories: NotificationCategoryTab[];
  onAction?: (item: NotificationItem, action: NotificationActionType) => void;
  onMarkAllAsRead?: () => void;
  onViewAll?: () => void;
}
```

---

## 3. Código React + TypeScript (`NotificationBellPopover.tsx`)

```tsx
import React, { useState, useEffect, useRef, useMemo, useId } from 'react';
import { Bell, CheckCircle, XCircle, Eye, AlertTriangle, Info, CheckCheck, PackageX } from 'lucide-react';
import type {
  NotificationBellPopoverProps,
  NotificationItem,
  NotificationActionType,
} from './notification.types';
import './NotificationBellPopover.css';

const SEVERITY_ICON = {
  critical: PackageX,
  warning: AlertTriangle,
  info: Info,
  success: CheckCircle,
} as const;

const ACTION_META: Record<NotificationActionType, { label: string; Icon: typeof Eye; className: string }> = {
  view: { label: 'Ver en detalle', Icon: Eye, className: 'btn-view' },
  approve: { label: 'Aprobar', Icon: CheckCircle, className: 'btn-approve' },
  deny: { label: 'Rechazar', Icon: XCircle, className: 'btn-deny' },
};

export const NotificationBellPopover: React.FC<NotificationBellPopoverProps> = ({
  notifications,
  categories,
  onAction,
  onMarkAllAsRead,
  onViewAll,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<string>(categories[0]?.id ?? 'todas');
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelId = useId();

  const unreadCount = useMemo(() => notifications.filter((n) => !n.isRead).length, [notifications]);

  // Conteo de no leídas por categoría en una sola pasada
  const unreadByCategory = useMemo(() => {
    const map = new Map<string, number>();
    for (const n of notifications) {
      if (!n.isRead) map.set(n.category, (map.get(n.category) ?? 0) + 1);
    }
    return map;
  }, [notifications]);

  const filtered = useMemo(
    () => (activeTab === 'todas' ? notifications : notifications.filter((n) => n.category === activeTab)),
    [notifications, activeTab]
  );

  const tabCount = (catId: string) => (catId === 'todas' ? unreadCount : unreadByCategory.get(catId) ?? 0);

  // Cierre por clic fuera y Escape (con limpieza de listeners)
  useEffect(() => {
    if (!isOpen) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setIsOpen(false);
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
        triggerRef.current?.focus();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleAction = (item: NotificationItem, action: NotificationActionType) => {
    onAction?.(item, action);
    if (action === 'view') setIsOpen(false); // el detalle se abre en el panel lateral derecho
  };

  return (
    <div className="joli-notification-wrapper" ref={containerRef}>
      <button
        ref={triggerRef}
        type="button"
        className={`joli-bell-btn ${isOpen ? 'active' : ''} ${unreadCount > 0 ? 'has-unread' : ''}`}
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label={unreadCount > 0 ? `Notificaciones: ${unreadCount} sin leer` : 'Notificaciones'}
        aria-haspopup="dialog"
        aria-expanded={isOpen}
        aria-controls={panelId}
        title="Centro de notificaciones"
      >
        <Bell size={18} aria-hidden="true" />
        {unreadCount > 0 && (
          <span className="bell-badge-count" aria-hidden="true">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </button>

      {isOpen && (
        <div id={panelId} className="joli-notification-popover" role="dialog" aria-label="Centro de notificaciones">
          <div className="joli-notif-header">
            <div className="joli-notif-title-row">
              <span className="joli-notif-title">Centro de notificaciones</span>
              {unreadCount > 0 && <span className="joli-notif-counter-pill">{unreadCount} pendientes</span>}
            </div>

            <div className="joli-notif-tabs" role="tablist" aria-label="Categorías de notificación">
              {categories.map((cat) => {
                const count = tabCount(cat.id);
                const selected = activeTab === cat.id;
                return (
                  <button
                    key={cat.id}
                    type="button"
                    role="tab"
                    aria-selected={selected}
                    className={`joli-notif-tab-btn ${selected ? 'active' : ''}`}
                    onClick={() => setActiveTab(cat.id)}
                  >
                    <span>{cat.label}</span>
                    {count > 0 && <span className="joli-tab-badge">{count}</span>}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="joli-notif-body" role="tabpanel">
            {filtered.length === 0 ? (
              <div className="joli-notif-empty-state">
                <CheckCircle size={32} className="joli-empty-icon-ok" aria-hidden="true" />
                <p className="joli-empty-title">Todo está al día</p>
                <span className="joli-empty-desc">No tienes notificaciones pendientes en esta categoría.</span>
              </div>
            ) : (
              <ul className="joli-notif-list">
                {filtered.map((item) => {
                  const SeverityIcon = SEVERITY_ICON[item.severity];
                  const actions = item.actions ?? ['view'];
                  return (
                    <li key={item.id} className={`joli-notif-item ${item.isRead ? 'read' : 'unread'}`}>
                      <div className={`joli-notif-icon-box severity-${item.severity}`} aria-hidden="true">
                        <SeverityIcon size={16} />
                      </div>

                      <div className="joli-notif-content">
                        <div className="joli-notif-topline">
                          <span className="joli-notif-item-title">{item.title}</span>
                          <time className="joli-notif-time" dateTime={item.timestamp}>{item.timeAgo}</time>
                        </div>
                        <p className="joli-notif-detail">{item.detail}</p>
                      </div>

                      <div className="btn-group btn-group-sm joli-notif-actions" role="group" aria-label="Acciones de la notificación">
                        {actions.map((action) => {
                          const { label, Icon, className } = ACTION_META[action];
                          return (
                            <button
                              key={action}
                              type="button"
                              className={`joli-notif-action-btn ${className}`}
                              title={label}
                              aria-label={`${label}: ${item.title}`}
                              onClick={() => handleAction(item, action)}
                            >
                              <Icon size={14} aria-hidden="true" />
                            </button>
                          );
                        })}
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div className="joli-notif-footer">
            <button type="button" className="joli-notif-link-btn" onClick={onMarkAllAsRead} disabled={unreadCount === 0}>
              <CheckCheck size={14} aria-hidden="true" />
              <span>Marcar todas como leídas</span>
            </button>
            {onViewAll && (
              <button type="button" className="joli-notif-link-btn" onClick={() => { setIsOpen(false); onViewAll(); }}>
                Ver todas
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 4. Estilos CSS (`NotificationBellPopover.css`)

Solo tokens de `variables.css`; los fondos translúcidos se derivan con `color-mix()`.

```css
.joli-notification-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

/* Botón circular de la campana */
.joli-bell-btn {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast), border-color var(--transition-fast);
  padding: 0;
}

.joli-bell-btn:hover,
.joli-bell-btn.active {
  background: var(--bg-active);
  color: var(--text-primary);
  border-color: color-mix(in srgb, var(--brand-primary) 50%, transparent);
}

.joli-bell-btn:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.joli-bell-btn.has-unread {
  color: var(--status-warning);
  border-color: color-mix(in srgb, var(--status-warning) 40%, transparent);
}

/* Insignia de no leídas */
.bell-badge-count {
  position: absolute;
  top: -3px;
  right: -3px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: var(--radius-full);
  background: var(--status-error);
  color: var(--text-on-brand);
  font-size: 10px;
  font-weight: var(--font-weight-extrabold);
  display: grid;
  place-items: center;
  border: 2px solid var(--bg-viewport);
  line-height: 1;
  animation: notifPulse 2.5s infinite ease-in-out;
}

@keyframes notifPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* Panel flotante */
.joli-notification-popover {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 380px;
  max-width: calc(100vw - 32px);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-popover);
  z-index: var(--z-popover);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: notifFadeSlide 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes notifFadeSlide {
  from { opacity: 0; transform: translateY(-8px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

@media (prefers-reduced-motion: reduce) {
  .bell-badge-count, .joli-notification-popover { animation: none; }
}

/* Cabecera y pestañas */
.joli-notif-header {
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
}

.joli-notif-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.joli-notif-title {
  font-size: 13.5px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.joli-notif-counter-pill {
  font-size: 10.5px;
  font-weight: var(--font-weight-bold);
  background: var(--status-error-bg);
  color: var(--status-error);
  border: 1px solid color-mix(in srgb, var(--status-error) 30%, transparent);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.joli-notif-tabs {
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 3px;
  gap: 3px;
}

.joli-notif-tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 6px 10px;
  border-radius: var(--radius-md);
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 11.5px;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.joli-notif-tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.joli-notif-tab-btn.active {
  background: var(--bg-active);
  color: var(--text-primary);
}

.joli-tab-badge {
  font-size: 9.5px;
  background: var(--status-error);
  color: var(--text-on-brand);
  padding: 1px 5px;
  border-radius: var(--radius-full);
  font-weight: var(--font-weight-extrabold);
}

/* Cuerpo y lista */
.joli-notif-body {
  max-height: 360px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.joli-notif-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.joli-notif-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
  border-left: 3px solid transparent;
  transition: background var(--transition-fast);
}

.joli-notif-item:hover {
  background: var(--bg-hover);
}

.joli-notif-item.unread {
  background: color-mix(in srgb, var(--accent-blue) 5%, transparent);
  border-left-color: var(--accent-blue);
}

/* Icono de severidad */
.joli-notif-icon-box {
  --sev: var(--accent-blue);
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--sev);
  background: color-mix(in srgb, var(--sev) 15%, transparent);
}

.severity-critical { --sev: var(--status-error); }
.severity-warning  { --sev: var(--status-warning); }
.severity-info     { --sev: var(--accent-blue); }
.severity-success  { --sev: var(--status-success); }

.joli-notif-content {
  flex: 1;
  min-width: 0;
}

.joli-notif-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin-bottom: 3px;
}

.joli-notif-item-title {
  font-size: 12.5px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.joli-notif-time {
  font-size: 10.5px;
  color: var(--text-muted);
  white-space: nowrap;
}

.joli-notif-detail {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Acciones rápidas (btn-group compacto de 26px) */
.joli-notif-actions {
  margin-top: 2px;
}

.joli-notif-action-btn {
  width: 26px;
  height: 26px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.joli-notif-action-btn.btn-view:hover    { color: var(--accent-blue);    background: color-mix(in srgb, var(--accent-blue) 20%, transparent); }
.joli-notif-action-btn.btn-approve:hover { color: var(--status-success); background: var(--status-success-bg); }
.joli-notif-action-btn.btn-deny:hover    { color: var(--status-error);   background: var(--status-error-bg); }

/* Estado vacío */
.joli-notif-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 36px 20px;
  text-align: center;
}

.joli-empty-icon-ok {
  color: var(--status-success);
  margin-bottom: 10px;
  background: var(--status-success-bg);
  padding: 6px;
  border-radius: var(--radius-full);
}

.joli-empty-title {
  font-size: 13.5px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0 0 4px;
}

.joli-empty-desc {
  font-size: 12px;
  color: var(--text-muted);
  max-width: 240px;
}

/* Pie */
.joli-notif-footer {
  padding: 10px 16px;
  background: var(--bg-elevated);
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.joli-notif-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.joli-notif-link-btn:hover:not(:disabled) {
  color: var(--text-primary);
}

.joli-notif-link-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```
