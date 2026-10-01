# Componente: Formulario Ensamblado de Login (`UI-COMP-LOGIN-FORM`)
## Ubicación SDD: `.sdd/components/login/login_form.md`

Este documento especifica el componente orquestador que ensambla todos los componentes atómicos del Login (`logo`, `card`, `input_field`, `button_primary`, `button_microsoft`, `feedback_alerts`) utilizando **CSS puro** gobernado por `variables.css` con soporte nativo para **Modo Noche y Modo Día**.

---

## 1. Estructura HTML / JSX Completa

```html
<main class="login-viewport">
  <!-- Halos de luz de fondo reactivos al tema -->
  <div class="login-orb login-orb-top" aria-hidden="true"></div>
  <div class="login-orb login-orb-bottom" aria-hidden="true"></div>

  <!-- Tarjeta Contenedora Principal -->
  <section class="login-card" aria-labelledby="login-title">
    <div class="login-card-inner">
      
      <!-- 1. Encabezado / Logo -->
      <header class="login-logo-wrapper">
        <div class="login-logo-badge">
          <svg class="login-logo-svg" viewBox="0 0 48 48" fill="none" aria-hidden="true">
            <defs>
              <linearGradient id="formLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#34d399" />
                <stop offset="100%" stop-color="#059669" />
              </linearGradient>
            </defs>
            <rect width="48" height="48" rx="14" fill="url(#formLogoGrad)" fill-opacity="0.15" stroke="#10b981" stroke-width="1.5" />
            <path d="M24 10C16 10 12 16 12 24C12 32 18 38 24 38C30 38 36 32 36 24C36 14 28 10 24 10Z" fill="url(#formLogoGrad)" />
            <path d="M24 18V30M18 24H30" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" />
          </svg>
        </div>
        <h1 id="login-title" class="login-logo-title">Greenyard</h1>
        <p class="login-logo-subtitle">Portal de Acceso Corporativo</p>
      </header>

      <!-- 2. Formulario de Credenciales -->
      <form id="form-login" class="login-form-body" novalidate>
        
        <!-- Campo: Número de Documento -->
        <div class="login-input-group">
          <label for="input-doc" class="login-input-label">Número de Documento</label>
          <div class="login-input-box">
            <span class="login-input-prefix-icon" aria-hidden="true">
              <svg class="login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="3" y="4" width="18" height="16" rx="2" stroke-width="2" />
                <circle cx="9" cy="10" r="2" stroke-width="2" />
                <path d="M15 8h2M15 12h2M7 16h10" stroke-width="2" stroke-linecap="round" />
              </svg>
            </span>
            <input 
              id="input-doc" 
              name="documento" 
              type="text" 
              inputmode="numeric" 
              placeholder="Ej. 1037645123" 
              class="login-input-control" 
              required 
            />
          </div>
          <span class="login-input-error" style="display: none;">Documento inválido</span>
        </div>

        <!-- Campo: Contraseña con Toggle Ojo -->
        <div class="login-input-group">
          <label for="input-pass" class="login-input-label">Contraseña</label>
          <div class="login-input-box">
            <span class="login-input-prefix-icon" aria-hidden="true">
              <svg class="login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="5" y="11" width="14" height="10" rx="2" stroke-width="2" />
                <path d="M8 11V7a4 4 0 118 0v4" stroke-width="2" stroke-linecap="round" />
              </svg>
            </span>
            <input 
              id="input-pass" 
              name="password" 
              type="password" 
              placeholder="••••••••••••" 
              class="login-input-control login-has-suffix" 
              required 
            />
            <button type="button" class="login-input-toggle-btn" aria-label="Mostrar contraseña">
              <svg class="login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" stroke-width="2"/>
              </svg>
            </button>
          </div>
          <span class="login-input-error" style="display: none;">Contraseña requerida</span>
        </div>

        <!-- Barra de Opciones: Recordar & Olvido -->
        <div class="login-options-bar">
          <label class="login-checkbox-label">
            <input type="checkbox" id="chk-remember" class="login-checkbox-control" />
            <span class="login-checkbox-text">Recordarme</span>
          </label>
          <a href="#recuperar" class="login-forgot-link">¿Olvidaste tu contraseña?</a>
        </div>

        <!-- Banner de Error Condicional -->
        <div id="login-alert-banner" class="login-alert-box" role="alert" style="display: none;">
          <svg class="login-alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke-width="2" />
            <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round" />
            <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="login-alert-message">Credenciales incorrectas.</span>
        </div>

        <!-- Botón Submit Principal -->
        <button type="submit" class="login-btn-primary">
          <svg class="login-btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="login-btn-text">Ingresar al Sistema</span>
        </button>
      </form>

      <!-- 3. Divisor "o también" -->
      <div class="login-divider">
        <span class="login-divider-line"></span>
        <span class="login-divider-text">o continúa con</span>
        <span class="login-divider-line"></span>
      </div>

      <!-- 4. Botón Microsoft SSO -->
      <button type="button" class="login-btn-microsoft">
        <svg class="login-btn-microsoft-icon" viewBox="0 0 21 21">
          <path fill="#f25022" d="M1 1h9v9H1z" />
          <path fill="#00a4ef" d="M1 11h9v9H1z" />
          <path fill="#7fba00" d="M11 1h9v9h-9z" />
          <path fill="#ffb900" d="M11 11h9v9h-9z" />
        </svg>
        <span>Iniciar sesión con Microsoft 365</span>
      </button>

      <!-- 5. Pie institucional -->
      <footer class="login-footer">
        <p>Greenyard • Acceso Seguro Corporativo</p>
      </footer>

    </div>
  </section>
</main>
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
.login-viewport {
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
.login-orb {
  position: absolute;
  border-radius: var(--radius-full);
  filter: blur(100px);
  pointer-events: none;
}

.login-orb-top {
  width: 420px;
  height: 420px;
  background: radial-gradient(circle, var(--orb-color-primary) 0%, transparent 70%);
  top: -10%;
  right: -5%;
}

.login-orb-bottom {
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, var(--orb-color-secondary) 0%, transparent 70%);
  bottom: -10%;
  left: -5%;
}

/* Tarjeta Principal */
.login-card {
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

.login-card-inner {
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

/* Opciones: Recordar & Olvido */
.login-options-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0.25rem 0 1.25rem 0;
  font-size: var(--font-size-xs);
}

.login-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}

.login-checkbox-control {
  accent-color: var(--brand-primary);
  width: 1rem;
  height: 1rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.login-forgot-link {
  color: var(--brand-accent);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  transition: color var(--transition-fast);
}

.login-forgot-link:hover {
  text-decoration: underline;
  filter: brightness(1.15);
}

/* Alerta de Error */
.login-alert-box {
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

.login-alert-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

/* Divisor "o continúa con" */
.login-divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  gap: 1rem;
}

.login-divider-line {
  flex: 1;
  height: 1px;
  background-color: var(--border-subtle);
}

.login-divider-text {
  font-size: var(--font-size-2xs);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

/* Pie Institucional */
.login-footer {
  margin-top: 1.75rem;
  text-align: center;
}

.login-footer p {
  margin: 0;
  font-size: var(--font-size-2xs);
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

/* Responsive Móvil */
@media (max-width: 480px) {
  .login-viewport {
    padding: 1rem;
  }
  .login-card-inner {
    padding: 2rem 1.25rem;
  }
}
```
