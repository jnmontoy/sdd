# Componente: Botón Submit y Loader de Login (`UI-COMP-LOGIN-BTN-PRI`)
## Ubicación SDD: `.sdd/components/login/button_primary.md`

Este documento detalla la especificación del botón primario de acción de autenticación utilizando **CSS puro** con soporte integrado de estado de carga asíncrono.

---

## 1. Estructura HTML / JSX

```html
<button
  type="submit"
  class="login-btn-primary"
>
  <!-- Estado Regular: Ícono de Escudo + Texto -->
  <svg class="login-btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <span class="login-btn-text">Ingresar al Sistema</span>

  <!-- Estado de Carga Alternativo (Reemplaza el contenido cuando isLoading=true) -->
  <!--
  <span class="login-btn-spinner" aria-hidden="true"></span>
  <span class="login-btn-text">Autenticando...</span>
  -->
</button>
```

---

## 2. Hoja de Estilos en CSS Puro (`button_primary.css`)

```css
/* ==========================================================================
   COMPONENTE: BOTÓN PRIMARIO DE LOGIN (CSS PURO)
   ========================================================================== */

.login-btn-primary {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 0.875rem;
  color: #ffffff;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  cursor: pointer;
  outline: none;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.4),
              0 2px 4px rgba(0, 0, 0, 0.2);
  user-select: none;
  box-sizing: border-box;
}

.login-btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.login-btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -5px rgba(16, 185, 129, 0.55),
              0 4px 8px rgba(0, 0, 0, 0.25);
}

.login-btn-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 5px 12px -2px rgba(16, 185, 129, 0.35);
}

.login-btn-primary:focus-visible {
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.45),
              0 0 0 1px #ffffff;
}

.login-btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Spinner de carga circular en CSS puro */
.login-btn-spinner {
  width: 1.125rem;
  height: 1.125rem;
  border: 2.5px solid rgba(255, 255, 255, 0.25);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: loginBtnSpin 0.75s linear infinite;
  display: inline-block;
  box-sizing: border-box;
}

@keyframes loginBtnSpin {
  to {
    transform: rotate(360deg);
  }
}
```
