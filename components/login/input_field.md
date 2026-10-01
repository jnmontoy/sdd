# Componente: Inputs de Login y Password Toggle (`UI-COMP-LOGIN-INPUT`)
## Ubicación SDD: `.sdd/components/login/input_field.md`

Este documento especifica los campos de entrada de datos para la página de login utilizando **CSS puro**, cubriendo el campo de Cédula/Documento y el campo de Contraseña con botón interactivo para mostrar u ocultar los caracteres.

---

## 1. Campo de Cédula / Documento

### 1.1. Estructura HTML / JSX
```html
<div class="login-input-group">
  <label for="login-doc" class="login-input-label">
    Número de Documento
  </label>
  <div class="login-input-box">
    <!-- Ícono Prefijo Vectorial (Cédula / IdCard) -->
    <span class="login-input-prefix-icon" aria-hidden="true">
      <svg class="login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <rect x="3" y="4" width="18" height="16" rx="2" stroke-width="2" />
        <circle cx="9" cy="10" r="2" stroke-width="2" />
        <path d="M15 8h2M15 12h2M7 16h10" stroke-width="2" stroke-linecap="round" />
      </svg>
    </span>

    <input
      id="login-doc"
      name="documento"
      type="text"
      inputmode="numeric"
      placeholder="Ej. 1037645123"
      class="login-input-control"
      autocomplete="username"
      required
    />
  </div>
  <!-- Mensaje de error condicional -->
  <p class="login-input-error" role="alert" style="display: none;">El documento debe contener solo números</p>
</div>
```

---

## 2. Campo de Contraseña con Toggle (Ver / Ocultar)

### 2.1. Estructura HTML / JSX
```html
<div class="login-input-group">
  <label for="login-pass" class="login-input-label">
    Contraseña
  </label>
  <div class="login-input-box">
    <!-- Ícono Prefijo Vectorial (Candado / Lock) -->
    <span class="login-input-prefix-icon" aria-hidden="true">
      <svg class="login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <rect x="5" y="11" width="14" height="10" rx="2" stroke-width="2" />
        <path d="M8 11V7a4 4 0 118 0v4" stroke-width="2" stroke-linecap="round" />
      </svg>
    </span>

    <input
      id="login-pass"
      name="password"
      type="password"
      placeholder="••••••••••••"
      class="login-input-control login-has-suffix"
      autocomplete="current-password"
      required
    />

    <!-- Botón Toggle Sufijo -->
    <button
      type="button"
      class="login-input-toggle-btn"
      aria-label="Mostrar contraseña"
    >
      <!-- Ícono Ojo Cerrado / Abierto en SVG -->
      <svg class="login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
        <circle cx="12" cy="12" r="3" stroke-width="2"/>
      </svg>
    </button>
  </div>
  <!-- Mensaje de error condicional -->
  <p class="login-input-error" role="alert" style="display: none;">La contraseña es requerida</p>
</div>
```

---

## 3. Hoja de Estilos en CSS Puro (`inputs.css`)

```css
/* ==========================================================================
   COMPONENTE: INPUTS DE LOGIN (CSS PURO)
   ========================================================================== */

.login-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  width: 100%;
  margin-bottom: 1.25rem;
  box-sizing: border-box;
}

.login-input-label {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #cbd5e1; /* Slate 300 */
}

.login-input-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
}

.login-input-prefix-icon {
  position: absolute;
  left: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b; /* Slate 500 */
  pointer-events: none;
  transition: color 0.2s ease;
  z-index: 2;
}

.login-input-svg {
  width: 1.25rem;
  height: 1.25rem;
  display: block;
}

.login-input-control {
  width: 100%;
  padding: 0.85rem 1rem 0.85rem 2.75rem;
  background-color: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  color: #f8fafc;
  font-size: 0.875rem;
  font-family: inherit;
  outline: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-sizing: border-box;
}

.login-input-control.login-has-suffix {
  padding-right: 2.75rem;
}

.login-input-control::placeholder {
  color: #475569;
}

.login-input-control:hover {
  border-color: rgba(255, 255, 255, 0.2);
  background-color: rgba(15, 23, 42, 0.8);
}

.login-input-control:focus {
  border-color: #10b981; /* Esmeralda Greenyard */
  background-color: rgba(15, 23, 42, 0.95);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.login-input-box:focus-within .login-input-prefix-icon {
  color: #10b981;
}

/* Botón interactivo para ver/ocultar contraseña */
.login-input-toggle-btn {
  position: absolute;
  right: 0.875rem;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease, transform 0.15s ease;
  outline: none;
  z-index: 2;
}

.login-input-toggle-btn:hover {
  color: #f1f5f9;
  transform: scale(1.1);
}

/* Estado de Error */
.login-input-group.has-error .login-input-control {
  border-color: #f43f5e;
  box-shadow: 0 0 0 3px rgba(244, 63, 94, 0.2);
  animation: loginShake 0.3s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}

.login-input-group.has-error .login-input-prefix-icon {
  color: #f43f5e;
}

.login-input-error {
  font-family: inherit;
  font-size: 0.75rem;
  color: #fb7185;
  margin: 0.25rem 0 0 0;
}

@keyframes loginShake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-3px, 0, 0); }
  40%, 60% { transform: translate3d(3px, 0, 0); }
}
```
