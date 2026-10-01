# Especificación de Componente: Modal de Sesión Expirada (`SessionExpirationModal.tsx`)
## Ecosistema Jolifoods — Manejo Desacoplado de Caducidad de Tokens

El componente `SessionExpirationModal` intercepta la pérdida o caducidad de la sesión de usuario y despliega un diálogo limpio y no bloqueante que notifica la situación e invita al usuario a reautenticarse sin perder su contexto de trabajo.

---

### 1. Requisitos de Negocio
1. **Desacoplado por Eventos**: Escucha el evento global `SESSION_EXPIRED_EVENT` emitido por el interceptor Axios cuando el backend responde con un código `401 Unauthorized`.
2. **Limpieza Controlada**: Al hacer clic en "Iniciar Sesión", purga el almacenamiento local y redirige al `/login` preservando la ruta previa (`?redirect=...`).
3. **Bloqueo Visual y Blur**: Impide que el usuario continúe interactuando con formularios protegidos tras expirar su token.

---

### 2. Implementación TypeScript Canónica (`SessionExpirationModal.tsx`)

```tsx
import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { LogOut, Clock, AlertCircle } from 'lucide-react';

export const SESSION_EXPIRED_EVENT = 'joli_session_expired';

export const dispatchSessionExpired = () => {
  window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
};

export const SessionExpirationModal: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleExpired = () => {
      setIsVisible(true);
    };

    window.addEventListener(SESSION_EXPIRED_EVENT, handleExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleExpired);
  }, []);

  const handleLoginRedirect = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');

    setIsVisible(false);
    const currentPath = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.href = `/login?redirect=${currentPath}`;
  };

  if (!isVisible) return null;

  return createPortal(
    <div className="joli-session-modal-overlay" role="alertdialog" aria-modal="true">
      <div className="joli-session-modal-card">
        <div className="session-icon-halo">
          <Clock size={40} className="session-icon text-warning" />
        </div>
        <h4 className="session-title">Sesión Caducada</h4>
        <p className="session-text">
          Su sesión ha expirado por inactividad o el token de seguridad ya no es válido. 
          Por favor, vuelva a identificarse para continuar trabajando con seguridad.
        </p>
        <button 
          type="button" 
          className="joli-btn-primary btn-session-relogin"
          onClick={handleLoginRedirect}
        >
          <LogOut size={16} className="me-2" />
          <span>Iniciar Sesión Nuevamente</span>
        </button>
      </div>
    </div>,
    document.body
  );
};
```

---

### 3. Estilos CSS (`session_expiration_modal.css`)

```css
.joli-session-modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(6px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: sessionFadeIn 0.2s ease-out;
}

.joli-session-modal-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 420px;
  width: 100%;
  padding: 32px 24px;
  background: var(--color-bg-card, #FFFFFF);
  border: 1px solid var(--color-border, #E5E7EB);
  border-radius: var(--radius-xl, 14px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: sessionScaleIn 0.2s ease-out;
}

[data-theme="dark"] .joli-session-modal-card {
  background: #1E293B;
  border-color: #334155;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
}

.session-icon-halo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: rgba(217, 119, 6, 0.12);
  margin-bottom: 16px;
}

.session-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  margin-bottom: 8px;
}

[data-theme="dark"] .session-title {
  color: #F8FAFC;
}

.session-text {
  font-size: 13.5px;
  color: var(--color-text-secondary, #6B7280);
  line-height: 1.5;
  margin-bottom: 24px;
}

[data-theme="dark"] .session-text {
  color: #94A3B8;
}

.btn-session-relogin {
  width: 100%;
  justify-content: center;
  height: 42px;
  font-size: 14px;
}

@keyframes sessionFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes sessionScaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```
