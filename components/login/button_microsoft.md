# Componente: Botón Microsoft SSO para Login (`UI-COMP-LOGIN-BTN-MS`)
## Ubicación SDD: `.sdd/components/login/button_microsoft.md`

Este documento especifica el botón de inicio de sesión único (SSO, *Single Sign-On*) con Microsoft 365 para la página de login.

> **Sesión resultante:** el flujo SSO DEBE terminar igual que el login por documento (ver [`auth_context.md`](../context/auth_context.md)): el backend valida el código de Microsoft (OAuth 2.0 / OpenID Connect con PKCE), emite el access token en el cuerpo y la cookie `HttpOnly` `refresh_token`. El frontend no guarda tokens de Microsoft ni de la app en storage.
>
> **Accesibilidad:** el botón no lleva `aria-label`; su nombre accesible es el texto visible (WCAG 2.5.3, la etiqueta debe contener el texto visible).

> Los cuatro colores del logotipo son de la marca Microsoft y se mantienen como hex (excepción de SVG de marca).

---

## 1. Estructura HTML / JSX

```tsx
<button
  type="button"
  onClick={handleMicrosoftLogin}
  disabled={isLoading}
  className="login-btn-microsoft"
>
  <svg 
    className="login-btn-microsoft-icon" 
    viewBox="0 0 21 21" 
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path fill="#f25022" d="M1 1h9v9H1z" />
    <path fill="#00a4ef" d="M1 11h9v9H1z" />
    <path fill="#7fba00" d="M11 1h9v9h-9z" />
    <path fill="#ffb900" d="M11 11h9v9h-9z" />
  </svg>
  <span>Iniciar sesión con Microsoft 365</span>
</button>
```

---

## 2. CSS Canónico

```css
.login-btn-microsoft {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  background-color: var(--bg-btn-secondary);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-family: inherit;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast), transform var(--transition-fast);
  box-shadow: var(--shadow-card);
  user-select: none;
}

.login-btn-microsoft-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.login-btn-microsoft:hover:not(:disabled) {
  background-color: var(--bg-btn-secondary-hover);
  border-color: var(--border-strong);
  transform: translateY(-1px);
}

.login-btn-microsoft:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn-microsoft:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}

.login-btn-microsoft:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}
```
