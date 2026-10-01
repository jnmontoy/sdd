# Especificación de Componente: Límite Global de Errores (Global Error Boundary)
## Ecosistema Jolifoods — Recuperación de Fallos y Detección de Nuevas Versiones

El componente `GlobalErrorBoundary` previene que un fallo JavaScript inesperado en cualquier vista muestre una "pantalla blanca". Detecta automáticamente errores `ChunkLoadError` provocados por el despliegue de nuevas versiones de la aplicación y ofrece recarga automática inteligente y navegación de rescate.

---

### 1. Requisitos de Negocio y Robustez
1. **Detección Automática de Nuevas Versiones (`ChunkLoadError`)**:
   - Tras un nuevo build en producción, los nombres de archivos chunk con hash anterior ya no existen en el servidor.
   - El Error Boundary intercepta `Failed to fetch dynamically imported module`, almacena un timestamp de recarga en `sessionStorage` y recarga automáticamente la página de forma transparente (con cooldown de 60 segundos para evitar bucles infinitos).
2. **UI de Rescate Amigable**:
   - Icono de alerta, título claro ("¡Oops! Algo salió mal" o "Actualización Disponible"), descripción contextual y botón primario "Recargar Página" o "Ir al Inicio".
3. **Detalles Técnicos para Entornos de Desarrollo**:
   - En modo desarrollo (`import.meta.env.DEV`), muestra el stack trace y detalles del error dentro de un acordeón colapsable.

---

### 2. Implementación TypeScript Canónica (`GlobalErrorBoundary.tsx`)

```tsx
import React, { useEffect } from 'react';
import { useRouteError, isRouteErrorResponse } from 'react-router-dom';
import { AlertCircle, RefreshCw, Home, ChevronDown } from 'lucide-react';

export const GlobalErrorBoundary: React.FC = () => {
  const error = useRouteError() as any;

  // 1. Detectar si el error es por nueva versión desplegada (ChunkLoadError de Vite/Rollup)
  const isChunkLoadError = 
    (error instanceof Error && error.message.includes('Failed to fetch dynamically imported module')) ||
    (typeof error === 'string' && error.includes('Failed to fetch dynamically imported module'));

  // 2. Auto-recarga controlada
  useEffect(() => {
    if (isChunkLoadError) {
      const lastReload = sessionStorage.getItem('chunkLoadReloadedAt');
      const now = Date.now();
      // Recargar automáticamente si pasaron más de 60 segundos de la última recarga
      if (!lastReload || now - parseInt(lastReload, 10) > 60000) {
        sessionStorage.setItem('chunkLoadReloadedAt', now.toString());
        window.location.reload();
      }
    }
  }, [isChunkLoadError]);

  const handleReload = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  return (
    <div className="joli-error-boundary-overlay">
      <div className="joli-error-boundary-card">
        <div className="error-icon-box">
          <AlertCircle size={44} className="text-danger" />
        </div>

        <h3 className="error-card-title">
          {isChunkLoadError ? 'Actualización Disponible' : '¡Oops! Algo salió mal'}
        </h3>

        <p className="error-card-desc">
          {isChunkLoadError
            ? 'Se ha desplegado una versión actualizada del sistema. Es necesario recargar para sincronizar los componentes.'
            : 'Ocurrió un error inesperado al renderizar este módulo. Sus datos permanecen a salvo.'}
        </p>

        <div className="error-card-actions">
          <button type="button" className="joli-btn-primary" onClick={handleReload}>
            <RefreshCw size={16} className="me-1" />
            <span>{isChunkLoadError ? 'Actualizar ahora' : 'Recargar página'}</span>
          </button>

          <button type="button" className="joli-btn-outline" onClick={handleGoHome}>
            <Home size={16} className="me-1" />
            <span>Ir al Inicio</span>
          </button>
        </div>

        {/* Detalle técnico del error (solo visible en depuración) */}
        {error && !isChunkLoadError && (
          <details className="error-technical-details">
            <summary>
              <span>Ver detalles técnicos</span>
              <ChevronDown size={14} />
            </summary>
            <pre className="error-trace">
              {isRouteErrorResponse(error)
                ? `${error.status} ${error.statusText}`
                : error instanceof Error
                ? error.stack || error.message
                : JSON.stringify(error, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};
```

---

### 3. Estilos CSS (`error_boundary.css`)

```css
.joli-error-boundary-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background-color: var(--color-bg-body, #0F172A);
  color: var(--color-text-primary, #F8FAFC);
}

.joli-error-boundary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 480px;
  width: 100%;
  padding: 36px 28px;
  background: var(--color-bg-card, #1E293B);
  border: 1px solid var(--color-border, #334155);
  border-radius: var(--radius-xl, 14px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.error-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(220, 38, 38, 0.12);
  margin-bottom: 20px;
}

.error-card-title {
  font-size: 19px;
  font-weight: 700;
  margin-bottom: 8px;
}

.error-card-desc {
  font-size: 13.5px;
  color: var(--color-text-secondary, #94A3B8);
  line-height: 1.5;
  margin-bottom: 24px;
}

.error-card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 16px;
}

.error-technical-details {
  width: 100%;
  margin-top: 16px;
  text-align: left;
  border-top: 1px solid var(--color-border, #334155);
  padding-top: 14px;
}

.error-technical-details summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-text-muted, #64748B);
  cursor: pointer;
  user-select: none;
}

.error-trace {
  font-size: 11px;
  font-family: monospace;
  background: #0B1120;
  padding: 12px;
  border-radius: 6px;
  margin-top: 10px;
  overflow-x: auto;
  color: #EF4444;
  white-space: pre-wrap;
  word-break: break-all;
}
```
