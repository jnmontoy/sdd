# Componente: Inputs de Login y Password Toggle (`UI-COMP-LOGIN-INPUT`)
## Ubicación SDD: `.sdd/components/login/input_field.md`

Este documento especifica los campos de entrada de datos para la página de login utilizando **CSS puro**, cubriendo el campo de Cédula/Documento y el campo de Contraseña con botón interactivo para mostrar u ocultar los caracteres.

---

## 1. Campo de Cédula / Documento

### 1.1. Estructura HTML / JSX
```html
<div class="joli-login-input-group">
  <label for="joli-login-doc" class="joli-login-input-label">
    Número de Documento
  </label>
  <div class="joli-login-input-box">
    <!-- Ícono Prefijo Vectorial (Cédula / IdCard) -->
    <span class="joli-login-input-prefix-icon" aria-hidden="true">
      <svg class="joli-login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <rect x="3" y="4" width="18" height="16" rx="2" stroke-width="2" />
        <circle cx="9" cy="10" r="2" stroke-width="2" />
        <path d="M15 8h2M15 12h2M7 16h10" stroke-width="2" stroke-linecap="round" />
      </svg>
    </span>

    <input
      id="joli-login-doc"
      name="numero_documento"
      type="text"
      inputmode="numeric"
      placeholder="Ej. 1000000001"
      class="joli-login-input-control"
      autocomplete="username"
      aria-describedby="joli-login-doc-error"
      data-testid="input-username"
      required
    />
  </div>
  <!-- Mensaje de error condicional -->
  <p id="joli-login-doc-error" class="joli-login-input-error" role="alert" hidden>El documento debe contener solo números</p>
</div>
```

---

## 2. Campo de Contraseña con Toggle (Ver / Ocultar)

### 2.1. Estructura HTML / JSX
```html
<div class="joli-login-input-group">
  <label for="joli-login-pass" class="joli-login-input-label">
    Contraseña
  </label>
  <div class="joli-login-input-box">
    <!-- Ícono Prefijo Vectorial (Candado / Lock) -->
    <span class="joli-login-input-prefix-icon" aria-hidden="true">
      <svg class="joli-login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <rect x="5" y="11" width="14" height="10" rx="2" stroke-width="2" />
        <path d="M8 11V7a4 4 0 118 0v4" stroke-width="2" stroke-linecap="round" />
      </svg>
    </span>

    <input
      id="joli-login-pass"
      name="password"
      type="password"
      placeholder="••••••••••••"
      class="joli-login-input-control joli-login-has-suffix"
      autocomplete="current-password"
      aria-describedby="joli-login-pass-error"
      data-testid="input-password"
      required
    />

    <!-- Botón Toggle Sufijo -->
    <button
      type="button"
      class="joli-login-input-toggle-btn"
      aria-label="Mostrar contraseña"
      aria-controls="joli-login-pass"
      aria-pressed="false"
    >
      <!-- Ícono Ojo Cerrado / Abierto en SVG -->
      <svg class="joli-login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
        <circle cx="12" cy="12" r="3" stroke-width="2"/>
      </svg>
    </button>
  </div>
  <!-- Mensaje de error condicional -->
  <p id="joli-login-pass-error" class="joli-login-input-error" role="alert" hidden>La contraseña es requerida</p>
</div>
```

---

### 2.2. Comportamiento del toggle
Al pulsar el botón se alterna `type="password"` / `type="text"`, se actualiza `aria-pressed` y `aria-label` ("Mostrar contraseña" / "Ocultar contraseña") y el foco permanece en el botón. El valor de la contraseña nunca se guarda en storage.

---

## 3. Hoja de Estilos en CSS Puro (`inputs.css`)

```css
/* ==========================================================================
   COMPONENTE: INPUTS DE LOGIN (CSS PURO)
   ========================================================================== */

.joli-login-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  width: 100%;
  margin-bottom: 1.25rem;
  box-sizing: border-box;
}

.joli-login-input-label {
  font-family: var(--font-family);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--label-color);
}

.joli-login-input-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
}

.joli-login-input-prefix-icon {
  position: absolute;
  left: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  pointer-events: none;
  transition: color 0.2s ease;
  z-index: 2;
}

.joli-login-input-svg {
  width: 1.25rem;
  height: 1.25rem;
  display: block;
}

.joli-login-input-control {
  width: 100%;
  padding: 0.85rem 1rem 0.85rem 2.75rem;
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--radius-lg);
  color: var(--input-text);
  font-size: var(--font-size-sm);
  font-family: inherit;
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast);
  box-sizing: border-box;
}

.joli-login-input-control.joli-login-has-suffix {
  padding-right: 2.75rem;
}

.joli-login-input-control::placeholder {
  color: var(--input-placeholder);
}

.joli-login-input-control:hover {
  border-color: var(--input-border-hover);
}

.joli-login-input-control:focus {
  border-color: var(--input-focus-border);
  background-color: var(--bg-input-focus);
  box-shadow: var(--shadow-input-focus);
}

.joli-login-input-box:focus-within .joli-login-input-prefix-icon {
  color: var(--brand-primary);
}

/* Botón interactivo para ver/ocultar contraseña */
.joli-login-input-toggle-btn {
  position: absolute;
  right: 0.875rem;
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease, transform 0.15s ease;
  z-index: 2;
}

.joli-login-input-toggle-btn:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 1px;
}

.joli-login-input-toggle-btn:hover {
  color: var(--text-primary);
  transform: scale(1.1);
}

/* Estado de Error */
.joli-login-input-group.has-error .joli-login-input-control {
  border-color: var(--border-error);
  box-shadow: var(--shadow-error-focus);
  animation: loginShake 0.3s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}

.joli-login-input-group.has-error .joli-login-input-prefix-icon {
  color: var(--status-error);
}

.joli-login-input-error {
  font-family: inherit;
  font-size: var(--font-size-xs);
  color: var(--status-error);
  margin: 0.25rem 0 0 0;
}

@keyframes loginShake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-3px, 0, 0); }
  40%, 60% { transform: translate3d(3px, 0, 0); }
}

@media (prefers-reduced-motion: reduce) {
  .joli-login-input-group.has-error .joli-login-input-control { animation: none; }
}
```
