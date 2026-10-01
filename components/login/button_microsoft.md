# Componente: Botón Microsoft SSO para Login (`UI-COMP-LOGIN-BTN-MS`)
## Ubicación SDD: `.sdd/components/login/button_microsoft.md`

Este documento especifica la integración del botón de Single Sign-On con Microsoft 365 para la página de login.

---

## 1. Estructura HTML / JSX

```tsx
<button
  type="button"
  onClick={handleMicrosoftLogin}
  disabled={isLoading}
  className="gy-btn-microsoft"
  aria-label="Iniciar sesión con cuenta de Microsoft 365"
>
  <svg 
    className="gy-btn-microsoft-icon" 
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
.gy-btn-microsoft {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  background-color: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.875rem;
  color: #f1f5f9;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
  user-select: none;
}

.gy-btn-microsoft-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.gy-btn-microsoft:hover:not(:disabled) {
  background-color: rgba(51, 65, 85, 0.9);
  border-color: rgba(255, 255, 255, 0.25);
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}

.gy-btn-microsoft:active:not(:disabled) {
  transform: translateY(0);
}

.gy-btn-microsoft:focus-visible {
  border-color: #00a4ef;
  box-shadow: 0 0 0 3px rgba(0, 164, 239, 0.35);
}

.gy-btn-microsoft:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}
```
