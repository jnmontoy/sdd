# Componente: Formulario Ensamblado de Login (`UI-COMP-LOGIN-FORM`)
## Ubicación SDD: `.sdd/components/login/login_form.md`

Este documento especifica el componente orquestador que ensambla todos los componentes atómicos del Login (`logo`, `card`, `input_field`, `button_primary`, `button_microsoft`, `feedback_alerts`) utilizando **CSS puro** gobernado por `variables.css` con soporte nativo para **Modo Noche y Modo Día**.

---

## 1. Estructura HTML / JSX Completa

```html
<main class="joli-login-viewport">
  <!-- Halos de luz de fondo reactivos al tema -->
  <div class="joli-login-orb joli-login-orb-top" aria-hidden="true"></div>
  <div class="joli-login-orb joli-login-orb-bottom" aria-hidden="true"></div>

  <!-- Tarjeta Contenedora Principal -->
  <section class="joli-login-card" aria-labelledby="joli-login-title">
    <div class="joli-login-card-inner">
      
      <!-- 1. Encabezado / Logo -->
      <header class="joli-login-logo-wrapper">
        <div class="joli-login-logo-badge">
          <img src="./assets/Jolifoods.svg" alt="Joli Foods" class="joli-login-logo-img"
               onerror="this.onerror=null; this.src='./assets/logoJoli.png';" />
        </div>
        <h1 id="joli-login-title" class="joli-login-logo-title">[Nombre del Proyecto]</h1>
        <p class="joli-login-logo-subtitle">Joli Foods • Acceso seguro</p>
      </header>

      <!-- 2. Formulario de Credenciales -->
      <form id="form-login" class="joli-login-form-body" novalidate>
        
        <!-- Campo: Número de Documento -->
        <div class="joli-login-input-group">
          <div class="joli-login-input-box campo-flotante">
            <span class="joli-login-input-prefix-icon" aria-hidden="true">
              <svg class="joli-login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="3" y="4" width="18" height="16" rx="2" stroke-width="2" />
                <circle cx="9" cy="10" r="2" stroke-width="2" />
                <path d="M15 8h2M15 12h2M7 16h10" stroke-width="2" stroke-linecap="round" />
              </svg>
            </span>
            <input 
              id="input-doc" 
              name="numero_documento"
              type="text" 
              inputmode="numeric" 
              placeholder="Ej. 1000000001"
              class="joli-login-input-control" 
              required 
              autocomplete="username"
              aria-describedby="input-doc-error"
              data-testid="input-username"
            />
            <label for="input-doc" class="campo-flotante-label">Número de documento</label>
          </div>
          <span id="input-doc-error" class="joli-login-input-error" hidden>Documento inválido</span>
        </div>

        <!-- Campo: Contraseña con Toggle Ojo -->
        <div class="joli-login-input-group">
          <div class="joli-login-input-box campo-flotante">
            <span class="joli-login-input-prefix-icon" aria-hidden="true">
              <svg class="joli-login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="5" y="11" width="14" height="10" rx="2" stroke-width="2" />
                <path d="M8 11V7a4 4 0 118 0v4" stroke-width="2" stroke-linecap="round" />
              </svg>
            </span>
            <input 
              id="input-pass" 
              name="password" 
              type="password" 
              placeholder="••••••••••••" 
              class="joli-login-input-control joli-login-has-suffix" 
              required 
              autocomplete="current-password"
              aria-describedby="input-pass-error"
              data-testid="input-password"
            />
            <label for="input-pass" class="campo-flotante-label">Contraseña</label>
            <button type="button" class="joli-login-input-toggle-btn" aria-label="Mostrar contraseña" aria-controls="input-pass" aria-pressed="false">
              <svg class="joli-login-input-svg" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" stroke-width="2"/>
              </svg>
            </button>
          </div>
          <span id="input-pass-error" class="joli-login-input-error" hidden>Contraseña requerida</span>
        </div>

        <!-- Barra de Opciones: Recordar & Olvido -->
        <div class="joli-login-options-bar">
          <label class="joli-login-checkbox-label">
            <input type="checkbox" id="chk-remember" class="joli-login-checkbox-control" />
            <span class="joli-login-checkbox-text">Recordar mi documento</span>
          </label>
          <a href="/recuperar" class="joli-login-forgot-link">¿Olvidaste tu contraseña?</a>
        </div>

        <!-- Banner de Error Condicional -->
        <div id="joli-login-alert-banner" class="joli-login-alert-box" role="alert" hidden>
          <svg class="joli-login-alert-icon" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke-width="2" />
            <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round" />
            <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="joli-login-alert-message">Credenciales incorrectas.</span>
        </div>

        <!-- Botón Submit Principal -->
        <button type="submit" class="joli-login-btn-primary" data-testid="btn-login-submit">
          <svg class="joli-login-btn-icon" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="joli-login-btn-text">Ingresar al Sistema</span>
        </button>
      </form>

      <!-- 3. Divisor "o también" -->
      <div class="joli-login-divider" aria-hidden="true">
        <span class="joli-login-divider-line"></span>
        <span class="joli-login-divider-text">o continúa con</span>
        <span class="joli-login-divider-line"></span>
      </div>

      <!-- 4. Botón Microsoft SSO -->
      <button type="button" class="joli-login-btn-microsoft">
        <svg class="joli-login-btn-microsoft-icon" viewBox="0 0 21 21" aria-hidden="true">
          <path fill="#f25022" d="M1 1h9v9H1z" />
          <path fill="#00a4ef" d="M1 11h9v9H1z" />
          <path fill="#7fba00" d="M11 1h9v9h-9z" />
          <path fill="#ffb900" d="M11 11h9v9h-9z" />
        </svg>
        <span>Iniciar sesión con Microsoft 365</span>
      </button>

      <!-- 5. Pie institucional -->
      <footer class="joli-login-footer">
        <p>[Nombre del Proyecto] • Joli Foods</p>
      </footer>

    </div>
  </section>
</main>
```

---

## 1.1. Envío del formulario en React (integración con `AuthContext`)

El formulario NO llama a la API ni maneja tokens directamente: delega en `login()` de [`context/auth_context.md`](../context/auth_context.md), que guarda el access token en memoria y deja que el backend fije la cookie `HttpOnly` de refresh. "Recordar mi documento" solo guarda el número de documento (nunca la contraseña ni tokens) con `STORAGE_KEYS.rememberedDoc`.

```tsx
import React, { useState } from 'react';
import { isAxiosError } from 'axios';
import { useLocation, useNavigate, type Location } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { STORAGE_KEYS, safeStorage } from '../../config/storageKeys';

export const LoginForm: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const remembered = safeStorage.get(STORAGE_KEYS.rememberedDoc);

  const [documento, setDocumento] = useState(remembered ?? '');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(remembered !== null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isSubmitting) return;
    setError(null);
    setIsSubmitting(true);
    try {
      const user = await login({ numero_documento: documento.trim(), password });
      if (remember) safeStorage.set(STORAGE_KEYS.rememberedDoc, documento.trim());
      else safeStorage.remove(STORAGE_KEYS.rememberedDoc);
      const from = (location.state as { from?: Location } | null)?.from?.pathname ?? '/home';
      navigate(user.debe_cambiar_clave ? '/primer-ingreso' : from, { replace: true });
    } catch (err) {
      const status = isAxiosError(err) ? err.response?.status : undefined;
      const code = isAxiosError<{ error_code?: string }>(err) ? err.response?.data?.error_code : undefined;
      // Mensajes genéricos: no revelar si el documento existe (ver contrato greenfield/pages/login/03)
      setError(
        status === 400 || status === 401 ? 'Documento o contraseña incorrectos.'
        : code === 'SSO_REQUIRED' ? 'Tu cuenta debe ingresar con Microsoft 365.'
        : code === 'USER_INACTIVE' ? 'Tu cuenta está inactiva. Contacta al administrador.'
        : status === 429 ? 'Demasiados intentos. Espera un momento antes de reintentar.'
        : 'No fue posible conectar. Intenta de nuevo.',
      );
      setPassword('');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Se omiten los íconos SVG decorativos de §1 para centrar el ejemplo en el comportamiento.
  return (
    <form className="joli-login-form-body" onSubmit={handleSubmit} noValidate>
      <div className="joli-login-input-group">
        <div className="joli-login-input-box campo-flotante">
          <input
            id="input-doc" name="numero_documento" type="text" inputMode="numeric"
            className="joli-login-input-control" autoComplete="username" required
            placeholder="Ej. 1000000001" data-testid="input-username"
            value={documento} onChange={(e) => setDocumento(e.target.value)}
          />
          <label htmlFor="input-doc" className="campo-flotante-label">Número de documento</label>
        </div>
      </div>

      <div className="joli-login-input-group">
        <div className="joli-login-input-box campo-flotante">
          <input
            id="input-pass" placeholder=" " name="password" type="password"
            className="joli-login-input-control" autoComplete="current-password" required
            data-testid="input-password"
            value={password} onChange={(e) => setPassword(e.target.value)}
          />
          <label htmlFor="input-pass" className="campo-flotante-label">Contraseña</label>
        </div>
      </div>

      <div className="joli-login-options-bar">
        <label className="joli-login-checkbox-label">
          <input
            type="checkbox" className="joli-login-checkbox-control"
            checked={remember} onChange={(e) => setRemember(e.target.checked)}
          />
          <span className="joli-login-checkbox-text">Recordar mi documento</span>
        </label>
        <a href="/recuperar" className="joli-login-forgot-link">¿Olvidaste tu contraseña?</a>
      </div>

      {error && (
        <div className="joli-login-alert-box" role="alert">
          <span className="joli-login-alert-message">{error}</span>
        </div>
      )}

      <button
        type="submit" className="joli-login-btn-primary" data-testid="btn-login-submit"
        disabled={isSubmitting} aria-busy={isSubmitting}
      >
        <span className="joli-login-btn-text">{isSubmitting ? 'Validando...' : 'Ingresar al Sistema'}</span>
      </button>
    </form>
  );
};
```

---

## 2. Hoja de Estilos en CSS Puro Integrando `variables.css`

```css
/* ==========================================================================
   FORMULARIO ENSAMBLADO DE LOGIN (CSS PURO)
   Consumo Total de variables.css con Soporte Noche/Día
   ========================================================================== */

@import '../variables.css';

/* Viewport Raíz */
.joli-login-viewport {
  position: relative;
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-viewport);
  padding: 1.5rem;
  box-sizing: border-box;
  overflow: hidden;
  font-family: var(--font-family);
  transition: background-color var(--transition-base);
}

/* Halos Dinámicos de Fondo */
.joli-login-orb {
  position: absolute;
  border-radius: var(--radius-full);
  filter: blur(100px);
  pointer-events: none;
}

.joli-login-orb-top {
  width: 420px;
  height: 420px;
  background: radial-gradient(circle, var(--orb-color-primary) 0%, transparent 70%);
  top: -10%;
  right: -5%;
}

.joli-login-orb-bottom {
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, var(--orb-color-secondary) 0%, transparent 70%);
  bottom: -10%;
  left: -5%;
}

/* Tarjeta Principal */
.joli-login-card {
  position: relative;
  z-index: var(--z-card);
  width: 100%;
  max-width: 440px;
  background-color: var(--bg-card);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border-subtle);
  border-top: 1px solid var(--border-card-accent);
  border-radius: var(--radius-2xl);
  box-shadow: var(--glass-shadow);
  color: var(--text-primary);
  box-sizing: border-box;
  transition: background-color var(--transition-base), border-color var(--transition-base);
}

.joli-login-card-inner {
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

/* Opciones: Recordar & Olvido */
.joli-login-options-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0.25rem 0 1.25rem 0;
  font-size: var(--font-size-xs);
}

.joli-login-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}

.joli-login-checkbox-control {
  accent-color: var(--brand-primary);
  width: 1rem;
  height: 1rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.joli-login-forgot-link {
  color: var(--brand-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  transition: color var(--transition-fast);
}

.joli-login-forgot-link:hover {
  text-decoration: underline;
  filter: brightness(1.15);
}

/* Alerta de Error */
.joli-login-alert-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  background-color: var(--alert-error-bg);
  border: 1px solid var(--alert-error-border);
  border-radius: var(--radius-md);
  color: var(--alert-error-text);
  font-size: var(--font-size-xs);
  margin-bottom: 1.25rem;
  box-sizing: border-box;
}

.joli-login-alert-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

/* Divisor "o continúa con" */
.joli-login-divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  gap: 1rem;
}

.joli-login-divider-line {
  flex: 1;
  height: 1px;
  background-color: var(--border-subtle);
}

.joli-login-divider-text {
  font-size: var(--font-size-2xs);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

/* Pie Institucional */
.joli-login-footer {
  margin-top: 1.75rem;
  text-align: center;
}

.joli-login-footer p {
  margin: 0;
  font-size: var(--font-size-2xs);
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

/* Responsive Móvil */
@media (max-width: 480px) {
  .joli-login-viewport {
    padding: 1rem;
  }
  .joli-login-card-inner {
    padding: 2rem 1.25rem;
  }
}
```
