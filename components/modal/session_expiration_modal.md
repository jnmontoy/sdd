# Especificación de Componente: Modal de Sesión Expirada (`SessionExpirationModal.tsx`)
## Aviso desacoplado de sesión vencida

> **Origen:** patrón tomado de tiendita (detección doble de vencimiento de sesión). Aquí se describe de forma genérica.

El componente `SessionExpirationModal` avisa que la sesión ya no se puede renovar y ofrece volver a iniciar sesión, sin pantallas en blanco ni redirecciones abruptas. Es la pieza visual de la cadena de autenticación descrita en [`context/auth_context.md`](../context/auth_context.md) (BP-20).

---

### 1. Requisitos

1. **Detección doble (la implementan otras piezas, el modal solo reacciona):**
   - **Reactiva:** el interceptor de [`api_client.md`](../services/api_client.md) recibe un 401, intenta **un único** refresh y, si falla, emite el evento global `session-expired`.
   - **Proactiva:** `AuthContext` lee `exp` del access token **en memoria** y lo renueva 60 s antes de que venza; si la renovación falla, emite el mismo evento. Así el usuario se entera antes de intentar guardar.
2. **Un solo dueño del estado:** solo `AuthContext` escucha `session-expired` y abre el modal. El modal no lee tokens ni storage (el access token nunca está en `localStorage`).
3. **Salida limpia:** "Volver a iniciar sesión" llama a `logout()` de `AuthContext` (revoca la cookie de refresh en servidor y limpia la memoria). `ProtectedRoute` redirige a `/login` conservando la ruta de origen en `state.from`.
4. **Accesibilidad:** `role="alertdialog"`, `aria-modal="true"`, título y descripción enlazados, foco inicial en el botón, foco atrapado dentro del diálogo y fondo inerte.
   - **Excepción a "cerrar con Escape":** este diálogo NO se cierra con Escape ni clic en el fondo. **Por qué:** la sesión ya no es válida; cerrarlo dejaría al usuario operando una pantalla cuyas peticiones fallarán.

---

### 2. Implementación TypeScript de referencia (`src/components/modal/SessionExpirationModal.tsx`)

```tsx
import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Clock, LogOut } from 'lucide-react';

export interface SessionExpirationModalProps {
  isOpen: boolean;
  /** Normalmente `() => logout()` de AuthContext. */
  onConfirm: () => void;
}

export const SessionExpirationModal: React.FC<SessionExpirationModalProps> = ({ isOpen, onConfirm }) => {
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const appRoot = document.getElementById('root');
    appRoot?.setAttribute('inert', ''); // el fondo no recibe foco ni clics
    buttonRef.current?.focus();

    // Único elemento enfocable: Tab y Shift+Tab permanecen en el botón. Escape no cierra (ver §1.4).
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        event.preventDefault();
        buttonRef.current?.focus();
      }
    };
    document.addEventListener('keydown', onKeyDown);

    return () => {
      document.removeEventListener('keydown', onKeyDown);
      appRoot?.removeAttribute('inert');
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div className="joli-session-modal-overlay">
      <div
        className="joli-session-modal-card"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="session-expired-title"
        aria-describedby="session-expired-desc"
        data-testid="session-expiration-modal"
      >
        <div className="joli-session-icon-halo" aria-hidden="true">
          <Clock size={38} />
        </div>

        <h2 id="session-expired-title" className="joli-session-title">
          Tu sesión ha expirado
        </h2>

        <p id="session-expired-desc" className="joli-session-text">
          Por seguridad, tu sesión ya no está activa. Inicia sesión nuevamente para continuar.
        </p>

        <button ref={buttonRef} type="button" className="joli-session-relogin-btn" onClick={onConfirm}>
          <LogOut size={16} aria-hidden="true" />
          <span>Volver a iniciar sesión</span>
        </button>
      </div>
    </div>,
    document.body,
  );
};
```

---

### 3. Integración

- **En `AuthContext`** (ver código completo en [`auth_context.md`](../context/auth_context.md) §3): listener de `session-expired` con limpieza en el `return` del efecto, temporizador proactivo cancelado al desmontar, y render de `<SessionExpirationModal isOpen={isSessionExpired && user !== null} onConfirm={() => void logout()} />`.
- **En el cliente HTTP** (ver [`api_client.md`](../services/api_client.md) §2): el evento se emite solo cuando falla el refresh, nunca en el primer 401, y nunca para las rutas `/auth/login/`, `/auth/refresh/` y `/auth/logout/`.
- El layout maestro NO DEBE montar una segunda instancia del modal: el dueño es `AuthContext`.

---

### 4. Estilos CSS (`session_expiration_modal.css`)

```css
.joli-session-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: color-mix(in srgb, var(--bg-viewport) 75%, transparent);
  backdrop-filter: blur(6px);
  animation: joli-session-fade-in 0.2s ease-out;
}

.joli-session-modal-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 420px;
  padding: 32px 24px;
  text-align: center;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  animation: joli-session-scale-in 0.2s ease-out;
}

.joli-session-icon-halo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 68px;
  height: 68px;
  margin-bottom: 16px;
  border-radius: var(--radius-full);
  background: var(--status-warning-bg);
  color: var(--status-warning);
}

.joli-session-title {
  margin: 0 0 8px;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.joli-session-text {
  margin: 0 0 24px;
  font-size: var(--font-size-sm);
  line-height: var(--line-height-normal);
  color: var(--text-secondary);
}

.joli-session-relogin-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 42px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-on-brand);
  background-color: var(--brand-primary);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.joli-session-relogin-btn:hover {
  background-color: var(--brand-primary-hover);
}

.joli-session-relogin-btn:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

@keyframes joli-session-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes joli-session-scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@media (prefers-reduced-motion: reduce) {
  .joli-session-modal-overlay,
  .joli-session-modal-card { animation: none; }
}
```
