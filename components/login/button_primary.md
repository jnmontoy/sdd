# Componente: Botón Submit y Loader de Login (`UI-COMP-LOGIN-BTN-PRI`)
## Ubicación SDD: `.sdd/components/login/button_primary.md`

Este documento detalla la especificación del botón primario de acción de autenticación utilizando **CSS puro** con soporte integrado de estado de carga asíncrono.

---

## 1. Estructura HTML / JSX

```html
<button
  type="submit"
  class="login-btn-primary"
  data-testid="btn-login-submit"
>
  <!-- Estado Regular: Ícono de Escudo + Texto -->
  <svg class="login-btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <span class="login-btn-text">Ingresar al Sistema</span>

  <!-- Estado de carga (isLoading=true): el botón lleva disabled y aria-busy="true" y el contenido se reemplaza por: -->
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
  background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-primary-hover) 100%);
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  color: var(--text-on-brand);
  font-family: var(--font-family);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: transform var(--transition-base), box-shadow var(--transition-base), filter var(--transition-base);
  box-shadow: 0 10px 20px -5px var(--brand-glow);
  user-select: none;
  box-sizing: border-box;
}

.login-btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.login-btn-primary:hover:not(:disabled) {
  filter: brightness(1.08);
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -5px var(--brand-glow);
}

.login-btn-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 5px 12px -2px var(--brand-glow);
}

.login-btn-primary:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
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
  border: 2.5px solid color-mix(in srgb, var(--text-on-brand) 25%, transparent);
  border-top-color: var(--text-on-brand);
  border-radius: var(--radius-full);
  animation: loginBtnSpin 0.75s linear infinite;
  display: inline-block;
  box-sizing: border-box;
}

@keyframes@keyframes loginBtnSpin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-btn-primary { transition: none; }
  .login-btn-primary:hover:not(:disabled) { transform: none; }
  .login-btn-spinner { animation-duration: 1.5s; }
}
```
