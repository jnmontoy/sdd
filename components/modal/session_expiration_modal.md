# Especificación de Componente: Modal de Sesión Expirada (`SessionExpirationModal.tsx`)
## Ecosistema Jolifoods — Manejo Desacoplado de Caducidad de Tokens
### Basado en la Arquitectura de Doble Detección de `tiendita`

El componente `SessionExpirationModal` intercepta la pérdida o caducidad de la sesión de usuario y despliega un diálogo limpio y no bloqueante que notifica la situación e invita al usuario a reautenticarse sin perder su contexto de trabajo.

---

### 1. Requisitos de Negocio y Arquitectura
1. **Doble Detección de Caducidad (Dual Detection Engine)**:
   - **Detección Reactiva (Backend HTTP 401)**: Intercepta cualquier respuesta `401 Unauthorized` desde la API (token vencido o revocado en servidor) y emite el evento global `window.dispatchEvent(new CustomEvent('session-expired'))`.
   - **Detección Proactiva (Cliente JWT `exp`)**: Valida en el cliente la marca temporal de expiración (`exp`) del Access Token JWT. Si `Date.now() >= payload.exp * 1000`, activa de inmediato el modal sin esperar a que el usuario dispare una petición fallida.
2. **Prevención de Pérdida de Contexto y Bucles**: Despliega un diálogo amigable con fondo difuminado (`backdrop-filter: blur(6px)`) en lugar de provocar redirecciones abruptas en blanco o bucles infinitos de reintento.
3. **Purga Idempotente de Almacenamiento**: Al confirmar la salida, limpia todos los tokens (`access_token`, `refresh_token`), credenciales cacheadas (`auth_user`) y redirige limpiamente a la ruta de inicio `/login` preservando el destino previo.

---

### 2. Implementación TypeScript Canónica (`SessionExpirationModal.tsx`)

```tsx
import React from 'react';
import { createPortal } from 'react-dom';
import { LogOut, Clock } from 'lucide-react';

export const SESSION_EXPIRED_EVENT = 'session-expired';

/** Disparador global utilizable desde interceptores de Axios / Fetch */
export const dispatchSessionExpired = () => {
  window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
};

export interface SessionExpiredModalProps {
  isOpen: boolean;
  onConfirm: () => void;
}

export const SessionExpiredModal: React.FC<SessionExpiredModalProps> = ({
  isOpen,
  onConfirm,
}) => {
  if (!isOpen) return null;

  return createPortal(
    <div 
      className="joli-session-modal-overlay" 
      role="alertdialog" 
      aria-modal="true"
      aria-labelledby="session-expired-title"
      aria-describedby="session-expired-desc"
    >
      <div className="joli-session-modal-card">
        {/* Halo luminoso de advertencia */}
        <div className="session-icon-halo">
          <Clock size={38} className="session-icon text-warning" />
        </div>

        <h4 id="session-expired-title" className="session-title">
          Tu Sesión ha Expirado
        </h4>

        <p id="session-expired-desc" className="session-text">
          Por políticas de seguridad corporativa, tu token de acceso ha caducado. 
          Para continuar operando de forma segura, por favor inicia sesión nuevamente.
        </p>

        <button 
          type="button" 
          className="btn-session-relogin"
          onClick={onConfirm}
          autoFocus
        >
          <LogOut size={16} />
          <span>Volver a Iniciar Sesión</span>
        </button>
      </div>
    </div>,
    document.body
  );
};
```

---

### 3. Integración en `AuthContext.tsx` (Doble Detección Proactiva y Reactiva)

```tsx
// src/context/AuthContext.tsx

// 1. Escuchar eventos globales de 401 Unauthorized y validar expiración de token JWT
useEffect(() => {
  const handleExpiredEvent = () => {
    setIsSessionExpired(true);
  };

  window.addEventListener('session-expired', handleExpiredEvent);

  // Verificación proactiva al montar la app
  const token = localStorage.getItem('access_token');
  if (token) {
    try {
      const payloadBase64 = token.split('.')[1];
      if (payloadBase64) {
        const base64 = payloadBase64.replace(/-/g, '+').replace(/_/g, '/');
        const pad = base64.length % 4;
        const paddedBase64 = pad ? base64 + '='.repeat(4 - pad) : base64;

        const payload = JSON.parse(atob(paddedBase64));
        if (payload.exp && Date.now() >= payload.exp * 1000) {
          setIsSessionExpired(true);
        }
      }
    } catch (e) {
      console.error('Error al validar la expiración del token:', e);
    }
  }

  return () => {
    window.removeEventListener('session-expired', handleExpiredEvent);
  };
}, []);

const handleConfirmExpiredSession = () => {
  setIsSessionExpired(false);
  logout();
  window.location.href = import.meta.env.BASE_URL || '/login';
};
```

---

### 4. Interceptor de Red API (`apiClient.ts` / Fetch Wrapper)

```typescript
// Interceptor en llamadas fetch o axios ante respuestas 401
if (response.status === 401) {
  // Notificar al sistema global que la sesión ha vencido
  window.dispatchEvent(new CustomEvent('session-expired'));
}
```

---

### 5. Estilos CSS (`session_expiration_modal.css`)

```css
.joli-session-modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.75);
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
  background: var(--color-bg-surface, #1E293B);
  border: 1px solid var(--color-border-subtle, #334155);
  border-radius: var(--border-radius-lg, 14px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
  animation: sessionScaleIn 0.2s ease-out;
}

.session-icon-halo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: rgba(217, 119, 6, 0.15);
  margin-bottom: 16px;
}

.session-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary, #F8FAFC);
  margin-bottom: 8px;
}

.session-text {
  font-size: 13.5px;
  color: var(--color-text-secondary, #94A3B8);
  line-height: 1.5;
  margin-bottom: 24px;
}

.btn-session-relogin {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 42px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  background-color: var(--color-primary, #2D6A4F);
  border: none;
  border-radius: var(--border-radius-sm, 6px);
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-session-relogin:hover {
  background-color: var(--color-primary-dark, #1B4332);
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
