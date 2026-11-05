# 01. Especificación de Páginas de Error Corporativas (404 No Encontrado & 403 Prohibido)
## Joli Foods — Spec-Driven Development (SDD)

Esta especificación describe el diseño y comportamiento de las pantallas de error de navegación y control de acceso en las aplicaciones de Joli Foods. Son una excepción permitida a la regla de ancho completo: la tarjeta de error PUEDE centrarse.

Garantiza que el colaborador nunca quede desorientado, proporcionando explicaciones claras en español neutro, enlaces directos de retorno al Tablero Principal y preservación del tema visual (Noche / Día) de [`variables.css`](../../../components/variables.css).

---

## 1. Código JSX / React 19 Canónico (`ErrorPage.tsx`)

```tsx
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, FileQuestion, ArrowLeft, Home } from 'lucide-react';

export interface ErrorPageProps {
  type?: '404' | '403' | '500';
}

export function ErrorPage({ type = '404' }: ErrorPageProps) {
  const navigate = useNavigate();

  const config = {
    '404': {
      code: '404',
      title: 'Página no encontrada',
      subtitle: 'La ruta o recurso al que intenta acceder no existe o fue reubicado.',
      icon: <FileQuestion size={64} className="joli-error-icon is-warning" aria-hidden="true" />
    },
    '403': {
      code: '403',
      title: 'Acceso no autorizado',
      subtitle: 'No tienes el permiso necesario para ver este módulo. Si crees que es un error, solicítalo al administrador.',
      icon: <ShieldAlert size={64} className="joli-error-icon is-danger" aria-hidden="true" />
    },
    '500': {
      code: '500',
      title: 'Error del servidor',
      subtitle: 'Ocurrió un error inesperado. Intenta de nuevo en unos minutos; si persiste, reporta el código de referencia a soporte.',
      icon: <ShieldAlert size={64} className="joli-error-icon is-danger" aria-hidden="true" />
    }
  }[type];

  return (
    <main className="joli-error-container">
      <div className="joli-error-card">
        {config.icon}
        <p className="joli-error-code" aria-hidden="true">{config.code}</p>
        <h1 className="joli-error-title">{config.title} <span className="visually-hidden">(error {config.code})</span></h1>
        <p className="joli-error-subtitle">{config.subtitle}</p>

        <div className="joli-error-actions">
          <button 
            type="button" 
            className="btn btn-outline-secondary d-inline-flex align-items-center gap-2"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft size={16} aria-hidden="true" />
            <span>Regresar</span>
          </button>
          <button 
            type="button" 
            className="btn btn-primary d-inline-flex align-items-center gap-2"
            onClick={() => navigate('/dashboard')}
          >
            <Home size={16} aria-hidden="true" />
            <span>Ir al Tablero Principal</span>
          </button>
        </div>
      </div>
    </main>
  );
}
```

---

## 2. Estilos (`error_page.css`, solo tokens de `variables.css`)

```css
.joli-error-container {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}

.joli-error-card {
  max-width: 520px;
  width: 100%;
  text-align: center;
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-2xl);
  padding: var(--space-8) var(--space-6);
  box-shadow: var(--shadow-card);
}

.joli-error-icon { margin-bottom: var(--space-3); }
.joli-error-icon.is-warning { color: var(--status-warning); }
.joli-error-icon.is-danger { color: var(--status-error); }

.joli-error-code {
  font-size: 72px;
  font-weight: var(--font-weight-extrabold);
  line-height: 1;
  color: var(--brand-primary);
  margin-bottom: var(--space-2);
  letter-spacing: -2px;
}

.joli-error-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.joli-error-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-6);
}

.joli-error-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}
```
