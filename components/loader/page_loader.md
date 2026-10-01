# Especificación de Componente: Cargadores y Skeletons (`PageLoader` / `TableSkeleton`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

Este documento especifica la familia de cargadores y estados de espera visuales (*Skeleton Loaders* y *PageLoader*) que mantienen la ergonomía y reducen la percepción de latencia durante las transiciones asíncronas de datos.

> **Origen y validación en producción**: Extraído y unificado a partir de `contenedores` (`PageLoader`), `app_tic` (`AppLoader`), `tiendita` (`UserTableSkeleton`) y `vibra` (`UserSkeletons`).

---

### 1. Variantes Disponibles

1. **`PageLoader` (Carga de Página Completa / Transición de Rutas)**:
   - Pantalla translúcida o centrada con el logo animado de Jolifoods, spinner esmeralda y mensaje de estado.
2. **`TableSkeleton` (Placeholder Esquelético para Tablas de Datos)**:
   - Fila de cabecera y N filas con barras pulsantes de ancho variable que simulan columnas de texto, badges numéricos y botones de acción.
3. **`CardSkeleton` (Placeholder Esquelético para Tarjetas / Grid)**:
   - Simula avatar o icono superior, líneas de texto y pie de tarjeta.

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/PageLoader.tsx
import React from 'react';
import './PageLoader.css';

export interface PageLoaderProps {
  message?: string;
  subMessage?: string;
  isOverlay?: boolean;
}

export const PageLoader: React.FC<PageLoaderProps> = ({
  message = 'Cargando información corporativa...',
  subMessage = 'Por favor espera un momento',
  isOverlay = false,
}) => {
  return (
    <div className={`joli-loader-container ${isOverlay ? 'joli-loader-overlay' : ''}`} role="status">
      <div className="joli-loader-box">
        {/* Isotipo Jolifoods con animación de pulso */}
        <div className="joli-loader-logo-ring">
          <svg className="joli-loader-svg" viewBox="0 0 48 48" fill="none">
            <circle cx="24" cy="24" r="20" stroke="#10B981" strokeWidth="2.5" strokeDasharray="30 10" />
            <path d="M24 12C17 12 14 18 14 24C14 30 19 36 24 36C29 36 34 30 34 24C34 16 27 12 24 12Z" fill="#10B981" />
            <path d="M24 18V30M18 24H30" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </div>
        <p className="joli-loader-title">{message}</p>
        {subMessage && <p className="joli-loader-subtitle">{subMessage}</p>}
      </div>
    </div>
  );
};

export interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

export const TableSkeleton: React.FC<TableSkeletonProps> = ({ rows = 5, columns = 6 }) => {
  return (
    <div className="joli-table-skeleton" aria-hidden="true">
      <div className="joli-skeleton-header-row">
        {Array.from({ length: columns }).map((_, c) => (
          <div key={c} className="joli-skeleton-bone skeleton-th" />
        ))}
      </div>
      <div className="joli-skeleton-body">
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} className="joli-skeleton-tr">
            {Array.from({ length: columns }).map((_, c) => (
              <div
                key={c}
                className="joli-skeleton-bone skeleton-td"
                style={{ width: `${60 + ((c * 17) % 35)}%` }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

### 3. Estilos CSS (`PageLoader.css`)

```css
.joli-loader-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 360px;
  width: 100%;
}

.joli-loader-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: 1050;
  min-height: 100vh;
}

.joli-loader-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem;
}

.joli-loader-logo-ring {
  width: 56px;
  height: 56px;
  margin-bottom: 1rem;
}

.joli-loader-svg {
  width: 100%;
  height: 100%;
  animation: joliSpin 2.2s linear infinite;
}

@keyframes joliSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.joli-loader-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  margin: 0;
}

.joli-loader-subtitle {
  font-size: 0.8rem;
  color: var(--text-muted, #64748B);
  margin: 4px 0 0 0;
}

/* Skeletons */
.joli-table-skeleton {
  width: 100%;
  background: var(--bg-card, #FFFFFF);
  border-radius: 8px;
  border: 1px solid var(--border-subtle, #E2E8F0);
  overflow: hidden;
}

.joli-skeleton-header-row {
  display: flex;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  background: var(--bg-surface, #F8FAFC);
  border-bottom: 1px solid var(--border-subtle, #E2E8F0);
}

.joli-skeleton-bone {
  height: 16px;
  background: linear-gradient(90deg, #F1F5F9 25%, #E2E8F0 50%, #F1F5F9 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  animation: joliShimmer 1.5s infinite;
}

@keyframes joliShimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-th {
  flex: 1;
  height: 14px;
}

.joli-skeleton-tr {
  display: flex;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle, #F1F5F9);
}

.skeleton-td {
  height: 14px;
  flex: 1;
}
```
