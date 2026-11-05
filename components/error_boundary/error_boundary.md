# Especificación de Componente: Límite Global de Errores (`GlobalErrorBoundary`)
## Recuperación de fallos y detección de nuevas versiones

`GlobalErrorBoundary` evita que un error inesperado de JavaScript en una vista deje la "pantalla en blanco". Detecta los errores de carga de módulos que aparecen tras desplegar una versión nueva y recarga una sola vez de forma controlada.

Se registra como `errorElement` de las rutas de React Router. Para errores fuera del enrutador (p. ej. en proveedores globales), se envuelve la app con un *error boundary* de clase que renderiza la misma tarjeta.

---

### 1. Requisitos

1. **Nueva versión desplegada (*ChunkLoadError*):** tras un build nuevo, los archivos con el hash anterior ya no existen. Se reconocen los mensajes de Chrome/Edge (`Failed to fetch dynamically imported module`), Firefox (`error loading dynamically imported module`) y Safari (`Importing a module script failed`). Se recarga automáticamente **una vez cada 60 s como máximo** (marca de tiempo en `sessionStorage`, con prefijo de app) para evitar bucles.
2. **Tarjeta de rescate:** ícono, título claro ("Algo salió mal" o "Actualización disponible"), descripción y botones "Recargar página" e "Ir al inicio".
3. **Detalles técnicos solo en desarrollo:** la traza se muestra únicamente si `import.meta.env.DEV`. En producción NO DEBE mostrarse (puede revelar rutas internas o datos); el error se envía al registro de errores del proyecto.
4. **Accesibilidad:** el título recibe el foco al montarse para que el lector de pantalla anuncie el error.

---

### 2. Implementación TypeScript de referencia (`GlobalErrorBoundary.tsx`)

```tsx
import React, { useEffect, useRef } from 'react';
import { isRouteErrorResponse, useRouteError } from 'react-router-dom';
import { AlertCircle, Home, RefreshCw } from 'lucide-react';

const APP = import.meta.env.VITE_APP_SLUG ?? 'app';
const RELOAD_KEY = `${APP}:chunk_reload_at`;
const RELOAD_COOLDOWN_MS = 60_000;
const CHUNK_ERROR_PATTERNS = [
  'Failed to fetch dynamically imported module',
  'error loading dynamically imported module',
  'Importing a module script failed',
];

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  return '';
}

function isChunkLoadError(error: unknown): boolean {
  const message = getErrorMessage(error);
  return CHUNK_ERROR_PATTERNS.some((pattern) => message.includes(pattern));
}

function describeError(error: unknown): string {
  if (isRouteErrorResponse(error)) return `${error.status} ${error.statusText}`;
  if (error instanceof Error) return error.stack ?? error.message;
  try {
    return JSON.stringify(error, null, 2);
  } catch {
    return String(error);
  }
}

export const GlobalErrorBoundary: React.FC = () => {
  const error: unknown = useRouteError();
  const titleRef = useRef<HTMLHeadingElement>(null);
  const chunkError = isChunkLoadError(error);

  useEffect(() => {
    titleRef.current?.focus();
    if (!chunkError) {
      // Punto de integración con el registro de errores del proyecto (Sentry u otro)
      console.error('Error no controlado en la vista:', error);
      return;
    }
    try {
      const last = Number(sessionStorage.getItem(RELOAD_KEY) ?? 0);
      if (Date.now() - last > RELOAD_COOLDOWN_MS) {
        sessionStorage.setItem(RELOAD_KEY, String(Date.now()));
        window.location.reload();
      }
    } catch {
      /* storage bloqueado: el usuario recarga con el botón */
    }
  }, [chunkError, error]);

  return (
    <div className="joli-error-boundary-overlay">
      <div className="joli-error-boundary-card" role="alert">
        <div className="error-icon-box" aria-hidden="true">
          <AlertCircle size={44} />
        </div>

        <h1 ref={titleRef} tabIndex={-1} className="error-card-title">
          {chunkError ? 'Actualización disponible' : 'Algo salió mal'}
        </h1>

        <p className="error-card-desc">
          {chunkError
            ? 'Se publicó una versión nueva del sistema. Recarga para continuar con la versión actualizada.'
            : 'Ocurrió un error inesperado al mostrar este módulo. Puedes recargar la página o volver al inicio.'}
        </p>

        <div className="error-card-actions">
          <button type="button" className="joli-btn-primary" onClick={() => window.location.reload()}>
            <RefreshCw size={16} aria-hidden="true" />
            <span>{chunkError ? 'Actualizar ahora' : 'Recargar página'}</span>
          </button>
          {/* Navegación completa a propósito: reinicia el estado de una app que falló */}
          <a className="joli-btn-secondary" href={import.meta.env.BASE_URL}>
            <Home size={16} aria-hidden="true" />
            <span>Ir al inicio</span>
          </a>
        </div>

        {import.meta.env.DEV && !chunkError && (
          <details className="error-technical-details">
            <summary>Ver detalles técnicos (solo desarrollo)</summary>
            <pre className="error-trace">{describeError(error)}</pre>
          </details>
        )}
      </div>
    </div>
  );
};
```

Los botones `.joli-btn-primary` / `.joli-btn-secondary` se definen en [`icon_action_group.md`](../button/icon_action_group.md) §5.

---

### 3. Estilos CSS (`error_boundary.css`)

```css
.joli-error-boundary-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background-color: var(--bg-viewport);
  color: var(--text-primary);
}

.joli-error-boundary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 480px;
  padding: 36px 28px;
  text-align: center;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-modal);
}

.error-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  margin-bottom: 20px;
  border-radius: var(--radius-full);
  background: var(--status-error-bg);
  color: var(--status-error);
}

.error-card-title {
  margin: 0 0 8px;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}

.error-card-title:focus {
  outline: none;
}

.error-card-desc {
  margin: 0 0 24px;
  font-size: var(--font-size-sm);
  line-height: var(--line-height-normal);
  color: var(--text-secondary);
}

.error-card-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.error-card-actions a {
  text-decoration: none;
}

.error-technical-details {
  width: 100%;
  margin-top: 16px;
  padding-top: 14px;
  text-align: left;
  border-top: 1px solid var(--border-subtle);
}

.error-technical-details summary {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  cursor: pointer;
}

.error-trace {
  margin-top: 10px;
  padding: 12px;
  overflow-x: auto;
  font-family: var(--font-family-mono);
  font-size: var(--font-size-2xs);
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--alert-error-text);
  background: var(--bg-viewport);
  border: 1px solid var(--alert-error-border);
  border-radius: var(--radius-sm);
}
```
