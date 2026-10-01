# Componente UI: Badges de Estado y Roles (Status Badges)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Las **Badges de Estado** son indicadores visuales atómicos utilizados para comunicar rápidamente el estado de entidades (usuarios activos, bloqueados), el rol corporativo asignado y los estados de procesos operativos.

---

## 1. Matriz de Variantes y Estados

| Tipo | Variante | Color / Fondo | Texto Típico |
| :--- | :--- | :--- | :--- |
| **Activo / Éxito** | `.joli-badge-success` | Verde Esmeralda (`rgba(16, 185, 129, 0.15)`) | `Activo`, `Completado`, `Aprobado` |
| **Peligro / Bloqueado** | `.joli-badge-danger` | Rojo Carmesí (`rgba(239, 68, 68, 0.15)`) | `Inactivo`, `Bloqueado`, `Rechazado` |
| **Advertencia** | `.joli-badge-warning` | Ámbar (`rgba(245, 158, 11, 0.15)`) | `Pendiente`, `En Revisión`, `Expirado` |
| **Informativo / Neutro** | `.joli-badge-info` | Azul Acero (`rgba(59, 130, 246, 0.15)`) | `Borrador`, `Sincronizando` |
| **Rol Administrador** | `.joli-badge-role-admin` | Púrpura / Esmeralda con halo | `ADMIN`, `SUPERUSER` |
| **Rol Operador** | `.joli-badge-role-op` | Esmeralda suave | `OPERADOR` |
| **Rol Consulta** | `.joli-badge-role-ro` | Slate / Gris neutro | `CONSULTA`, `AUDITOR` |

---

## 2. Código JSX / React 19 Canónico (`Badge.tsx`)

```tsx
import React from 'react';
import '../../styles/variables.css';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'danger' | 'warning' | 'info' | 'admin' | 'operator' | 'neutral';
  dot?: boolean;
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  dot = false,
  size = 'md'
}) => {
  return (
    <span className={`joli-badge joli-badge-${variant} joli-badge-${size}`}>
      {dot && <span className="joli-badge-dot" />}
      {children}
    </span>
  );
};
```

---

## 3. Estilos CSS Canónicos (`variables.css`)

```css
.joli-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: var(--weight-bold);
  border-radius: var(--radius-full);
  line-height: 1;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  white-space: nowrap;
}

.joli-badge-md {
  padding: 4px 10px;
  font-size: 11px;
}

.joli-badge-sm {
  padding: 2px 8px;
  font-size: 10px;
}

.joli-badge-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background-color: currentColor;
}

/* VARIANTES */
.joli-badge-success {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.joli-badge-danger {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.joli-badge-warning {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.joli-badge-info {
  background-color: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.joli-badge-admin {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(99, 102, 241, 0.2));
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.4);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
}

.joli-badge-operator {
  background-color: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.joli-badge-neutral {
  background-color: var(--color-bg-input);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}
```
