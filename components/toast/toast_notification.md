# Especificación de Componente: Notificaciones Flotantes (`ToastNotification`)
## Guía de implementación SDD

`ToastNotification` da retroalimentación breve y no bloqueante tras acciones asíncronas (crear, editar, eliminar, sincronizar, errores de red). Se apoya en la librería `sonner` y usa los tokens de [`variables.css`](../variables.css).

---

### 1. Requisitos

1. **No bloqueante:** no interrumpe la navegación ni roba el foco.
2. **Duración por tipo:** `success` 3500 ms · `info` 4000 ms · `warning` 5000 ms · `error` 7000 ms (con botón de cierre; PUEDE fijarse `duration: Infinity` si el usuario debe leer un detalle).
3. **Acción opcional** (Deshacer / Reintentar) en cualquier tipo.
4. **Posición:** inferior derecha en escritorio; superior centrada en pantallas angostas (< 640px).
5. **Sin diálogos nativos:** el código NO DEBE usar `window.alert()`; para confirmar acciones se usa [`ConfirmModal`](../modal/confirm_modal.md). **Por qué:** los diálogos nativos bloquean el hilo, no respetan el tema y no se pueden probar con E2E.
6. **Accesibilidad:** `sonner` anuncia los toasts en una región `aria-live`; los errores usan prioridad `assertive`. Los botones tienen texto o `aria-label`. Un toast nunca es el único lugar donde se informa un error de formulario: el error también se muestra junto al campo.

---

### 2. Implementación TypeScript / React (`src/components/ui/ToastNotification.tsx`)

```tsx
import React, { useEffect, useState } from 'react';
import { toast, Toaster } from 'sonner';
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X, type LucideIcon } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastOptions {
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  duration?: number;
}

const CONFIG: Record<ToastType, { icon: LucideIcon; duration: number; role: 'status' | 'alert' }> = {
  success: { icon: CheckCircle2, duration: 3500, role: 'status' },
  info: { icon: Info, duration: 4000, role: 'status' },
  warning: { icon: AlertTriangle, duration: 5000, role: 'status' },
  error: { icon: AlertCircle, duration: 7000, role: 'alert' },
};

function show(type: ToastType, title: string, options: ToastOptions = {}) {
  const { icon: Icon, duration, role } = CONFIG[type];
  return toast.custom(
    (id) => (
      <div className={`joli-toast toast-${type}`} role={role}>
        <div className="toast-icon-box" aria-hidden="true">
          <Icon size={18} />
        </div>
        <div className="toast-content">
          <div className="toast-title">{title}</div>
          {options.description && <div className="toast-desc">{options.description}</div>}
        </div>
        {options.actionLabel && options.onAction && (
          <button
            type="button"
            className="toast-action-btn"
            onClick={() => {
              options.onAction?.();
              toast.dismiss(id);
            }}
          >
            {options.actionLabel}
          </button>
        )}
        <button type="button" className="toast-close-btn" onClick={() => toast.dismiss(id)} aria-label="Cerrar notificación">
          <X size={14} aria-hidden="true" />
        </button>
      </div>
    ),
    { duration: options.duration ?? duration },
  );
}

export const showToast = {
  success: (title: string, options?: ToastOptions) => show('success', title, options),
  error: (title: string, options?: ToastOptions) => show('error', title, options),
  warning: (title: string, options?: ToastOptions) => show('warning', title, options),
  info: (title: string, options?: ToastOptions) => show('info', title, options),
};

/** Montar una sola vez en la raíz de la app. */
export const CorporateToaster: React.FC = () => {
  const query = '(max-width: 640px)';
  const [isNarrow, setIsNarrow] = useState(() => window.matchMedia(query).matches);

  useEffect(() => {
    const mql = window.matchMedia(query);
    const onChange = (e: MediaQueryListEvent) => setIsNarrow(e.matches);
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  return (
    <Toaster
      position={isNarrow ? 'top-center' : 'bottom-right'}
      // Mismo ancho que la tarjeta (.joli-toast); sonner trae 356 px por defecto (BUG-012)
      style={{ '--width': '440px' } as React.CSSProperties}
      toastOptions={{ unstyled: true, className: 'joli-toaster-item' }}
    />
  );
};
```

---

### 3. Estilos CSS (`toast.css`)

```css
.joli-toast {
  --toast-accent: var(--status-info);
  --toast-accent-bg: var(--status-info-bg);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%; /* El ancho lo fija el Toaster con --width */
  padding: 12px 16px;
  font-family: inherit;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-left: 4px solid var(--toast-accent);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-popover);
  animation: toastSlideIn 0.25s ease-out;
}

/* Apilados: con unstyled, sonner da al aviso de atrás la altura del de adelante pero no oculta su contenido.
   Se recorta para que todos se vean del mismo tamaño; al pasar el mouse se despliegan completos (BUG-012). */
.joli-toaster-item[data-expanded='false'][data-front='false'] {
  overflow: hidden;
  border-radius: var(--radius-md);
}
.joli-toaster-item[data-expanded='false'][data-front='false'] > .joli-toast {
  height: 100%;
}
.joli-toaster-item[data-expanded='false'][data-front='false'] > .joli-toast > * {
  opacity: 0;
}

.toast-success { --toast-accent: var(--status-success); --toast-accent-bg: var(--status-success-bg); }
.toast-error   { --toast-accent: var(--status-error);   --toast-accent-bg: var(--status-error-bg); }
.toast-warning { --toast-accent: var(--status-warning); --toast-accent-bg: var(--status-warning-bg); }
.toast-info    { --toast-accent: var(--status-info);    --toast-accent-bg: var(--status-info-bg); }

.toast-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  margin-top: 1px;
  border-radius: var(--radius-full);
  background: var(--toast-accent-bg);
  color: var(--toast-accent);
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  line-height: 1.35;
  color: var(--text-primary);
}

.toast-desc {
  margin-top: 2px;
  font-size: var(--font-size-xs);
  line-height: 1.4;
  word-break: break-word;
  color: var(--text-secondary);
}

.toast-action-btn,
.toast-close-btn {
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.toast-action-btn {
  padding: 4px 8px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  text-decoration: underline;
}

.toast-action-btn:hover,
.toast-close-btn:hover {
  background: var(--bg-hover);
}

.toast-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  color: var(--text-muted);
}

.toast-close-btn:hover {
  color: var(--text-primary);
}

.toast-action-btn:focus-visible,
.toast-close-btn:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

@keyframes toastSlideIn {
  from { opacity: 0; transform: translateY(12px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

@media (prefers-reduced-motion: reduce) {
  .joli-toast { animation: none; }
}
```

---

### 4. Instalación y casos de uso

#### 4.1. Dependencias
```bash
npm install sonner lucide-react
```

#### 4.2. Montaje
`<CorporateToaster />` se monta **una sola vez** en la raíz (`App.tsx`), fuera de las rutas.

```tsx
export const App: React.FC = () => (
  <>
    <CorporateToaster />
    <AppRoutes />
  </>
);
```

#### 4.3. Login
Ver la matriz completa en [`login/feedback_alerts.md`](../login/feedback_alerts.md) §3. Los mensajes de error de credenciales son genéricos (no revelan si el documento existe).

#### 4.4. CRUD con "Deshacer"
```tsx
showToast.success('Registro guardado', { description: 'Los cambios quedaron guardados.' });

showToast.info('Registro desactivado', {
  description: 'Puedes revertir la acción durante unos segundos.',
  actionLabel: 'Deshacer',
  onAction: () => reactivarRegistro(id),
  duration: 6000,
});
```

#### 4.5. Errores globales de red
Se agrega en `src/services/api.ts` **después** de los interceptores de autenticación de [`api_client.md`](../services/api_client.md), para no mostrar toasts por los 401 que se resuelven con refresh:

```tsx
import { AxiosError } from 'axios';

const notifyNetworkErrors = (error: AxiosError) => {
  if (!error.response) {
    showToast.error('Error de conectividad', {
      description: 'Verifica tu conexión o la disponibilidad del servicio.',
    });
  } else if (error.response.status >= 500) {
    showToast.error('Error del servidor', {
      description: 'Ocurrió un error inesperado. Intenta de nuevo en unos minutos.',
    });
  }
  return Promise.reject(error);
};

api.interceptors.response.use((r) => r, notifyNetworkErrors);
fastApi.interceptors.response.use((r) => r, notifyNetworkErrors);
```
