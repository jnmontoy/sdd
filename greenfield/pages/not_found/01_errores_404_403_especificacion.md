# 01. Especificación de Páginas de Error Corporativas (404 No Encontrado & 403 Prohibido)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Esta especificación describe el diseño y comportamiento de las pantallas de error de navegación y control de acceso en las aplicaciones de Jolifoods.

Garantiza que el colaborador nunca quede desorientado, proporcionando explicaciones claras en español neutro, enlaces directos de retorno al Tablero Principal y preservación del tema visual (Noche / Día) de [`variables.css`](../../../components/variables.css).

---

## 1. Código JSX / React 19 Canónico (`ErrorPage.tsx`)

```tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, FileQuestion, ArrowLeft, Home } from 'lucide-react';
import '../../../styles/variables.css';

export interface ErrorPageProps {
  type?: '404' | '403' | '500';
}

export const ErrorPage: React.FC<ErrorPageProps> = ({ type = '404' }) => {
  const navigate = useNavigate();

  const config = {
    '404': {
      code: '404',
      title: 'Página no encontrada',
      subtitle: 'La ruta o recurso al que intenta acceder no existe o fue reubicado.',
      icon: <FileQuestion size={64} className="text-warning mb-3" />
    },
    '403': {
      code: '403',
      title: 'Acceso Denegado / No Autorizado',
      subtitle: 'Su rol actual no posee los privilegios requeridos para ver este módulo.',
      icon: <ShieldAlert size={64} className="text-danger mb-3" />
    },
    '500': {
      code: '500',
      title: 'Incidencia en el Servidor',
      subtitle: 'El servicio está experimentando dificultades. Nuestro equipo ha sido notificado.',
      icon: <ShieldAlert size={64} className="text-danger mb-3" />
    }
  }[type];

  return (
    <div className="joli-error-container">
      <div className="joli-error-card">
        {config.icon}
        <h1 className="joli-error-code">{config.code}</h1>
        <h2 className="joli-error-title">{config.title}</h2>
        <p className="joli-error-subtitle">{config.subtitle}</p>

        <div className="joli-error-actions">
          <button 
            type="button" 
            className="btn btn-outline-secondary d-inline-flex align-items-center gap-2"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft size={16} />
            <span>Regresar</span>
          </button>
          <button 
            type="button" 
            className="btn btn-primary d-inline-flex align-items-center gap-2"
            onClick={() => navigate('/dashboard')}
          >
            <Home size={16} />
            <span>Ir al Tablero Principal</span>
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

## 2. Estilos CSS Canónicos (`variables.css`)

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
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-8) var(--space-6);
  box-shadow: var(--shadow-xl);
}

.joli-error-code {
  font-size: 72px;
  font-weight: var(--weight-extrabold);
  line-height: 1;
  color: var(--color-primary);
  margin-bottom: var(--space-2);
  letter-spacing: -2px;
}

.joli-error-title {
  font-size: var(--text-xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.joli-error-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
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
