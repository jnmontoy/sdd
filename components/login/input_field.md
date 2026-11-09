# Componente: Campos del Login y Password Toggle (`UI-COMP-LOGIN-INPUT`)
## Ubicación SDD: `sdd/components/login/input_field.md`

Campos de documento y contraseña del login. Usan el **campo con etiqueta flotante** de [`../form/floating_field.md`](../form/floating_field.md), que define el estilo, los estados, la animación, el alcance (solo formularios de captura, nunca filtros ni buscadores) y la versión React Native. Este documento solo agrega lo propio del login: medidas, contraseña, Bloq Mayús, errores y las reglas de acabado.

Implementación de referencia (Pandora): web en `frontend-admin/src/components/login/CampoLogin.tsx` + `src/styles/login.css`; APK en `frontend/src/components/login/LoginTextField.tsx` (envuelve `CampoFlotante`).

---

## 1. Estructura HTML / JSX

La caja lleva `campo-flotante` y la etiqueta `campo-flotante-label`, después del input ([`floating_field.md`](../form/floating_field.md) §5). El input siempre lleva `placeholder` (un espacio `" "` si no hay ejemplo).

### 1.1. Campo de documento
```html
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
      id="joli-login-doc"
      name="numero_documento"
      type="text"
      inputmode="numeric"
      placeholder="Ej. 1000000001"
      class="joli-login-input-control"
      autocomplete="username"
      autocapitalize="none"
      spellcheck="false"
      data-testid="input-username"
      required
    />
    <label for="joli-login-doc" class="campo-flotante-label">Número de documento</label>
  </div>
  <!-- Solo con error: el input lleva aria-invalid="true" y aria-describedby="joli-login-doc-error" -->
  <p id="joli-login-doc-error" class="joli-login-input-error" hidden>Escribe tu número de documento.</p>
</div>
```

### 1.2. Campo de contraseña con toggle y aviso de Bloq Mayús
```html
<div class="joli-login-input-group">
  <div class="joli-login-input-box campo-flotante">
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
      placeholder=" "
      class="joli-login-input-control joli-login-has-suffix"
      autocomplete="current-password"
      data-testid="input-password"
      required
    />
    <label for="joli-login-pass" class="campo-flotante-label">Contraseña</label>

    <button type="button" class="joli-login-input-toggle-btn" aria-label="Mostrar contraseña" aria-pressed="false">
      <svg class="joli-login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-width="2"/>
        <circle cx="12" cy="12" r="3" stroke-width="2"/>
      </svg>
    </button>
  </div>
  <p id="joli-login-pass-error" class="joli-login-input-error" hidden>Escribe tu contraseña.</p>
  <!-- Con Bloq Mayús activo (getModifierState('CapsLock') en keydown/keyup; se oculta en blur) -->
  <p id="joli-login-pass-aviso" class="joli-login-input-hint" role="status" hidden>Bloq Mayús está activado</p>
</div>
```

### 1.3. Comportamiento
- **Toggle:** alterna `type="password"` / `type="text"`, actualiza `aria-pressed` y `aria-label` («Mostrar contraseña» / «Ocultar contraseña»); alcanzable con Tab (sin `tabindex="-1"`). La clave nunca se guarda en storage.
- **Error:** al enviar, los campos vacíos reciben `aria-invalid="true"` y `aria-describedby` al mensaje (la etiqueta flotante se pinta en rojo sola); el foco va al primero con error. El error se limpia al escribir.
- **Aviso de Bloq Mayús:** se añade a `aria-describedby` mientras está visible; no se muestra si ya hay un error.

---

## 2. CSS del login

Solo las medidas propias del login y las piezas que no son de la etiqueta. La etiqueta flotante es el CSS de [`floating_field.md`](../form/floating_field.md) §5.7.

```css
/* Medidas del login para la etiqueta flotante (48 px de alto, icono de 18 px) */
.joli-login-input-box.campo-flotante {
  --cf-alto: 3rem;
  --cf-texto-x: 2.65rem;
  --cf-label-x: 0.75rem;
  --cf-pad: 0.375rem;
  --cf-escala: 1.15;
  --cf-fondo-campo-foco: var(--bg-input-focus);
}

.joli-login-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  width: 100%;
  padding-top: 0.5rem; /* mitad de la etiqueta que sobresale del borde */
  box-sizing: border-box;
}

.joli-login-input-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-sizing: border-box;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast);
}

.joli-login-input-box:hover:not(:focus-within) { border-color: var(--border-strong); }

.joli-login-input-box:focus-within {
  background-color: var(--bg-input-focus);
  border-color: var(--border-focus);
  box-shadow: var(--shadow-input-focus);
}

.joli-login-input-box:has(.joli-login-input-control:disabled) { opacity: 0.65; }

.joli-login-input-prefix-icon {
  position: absolute;
  left: 0.875rem;
  display: flex;
  color: var(--text-muted);
  pointer-events: none;
  transition: color var(--transition-fast);
}

.joli-login-input-box:focus-within .joli-login-input-prefix-icon { color: var(--brand-primary); }

.joli-login-input-svg { width: 1.125rem; height: 1.125rem; display: block; }

.joli-login-input-control {
  width: 100%;
  height: 3rem; /* 48 px: mismo alto que los botones */
  padding: 0 0.875rem 0 2.65rem;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-family: inherit;
  font-size: var(--font-size-sm);
  box-sizing: border-box;
}

.joli-login-input-control.joli-login-has-suffix { padding-right: 3rem; }
.joli-login-input-control:disabled { cursor: not-allowed; }

/* Toggle ver/ocultar */
.joli-login-input-toggle-btn {
  position: absolute;
  right: 0.5rem;
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.joli-login-input-toggle-btn:hover:not(:disabled) { color: var(--text-primary); background-color: var(--bg-hover); }
.joli-login-input-toggle-btn:focus-visible { outline: 2px solid var(--border-focus); outline-offset: 0; }

/* Error y avisos bajo el campo */
.joli-login-input-box:has([aria-invalid='true']),
.joli-login-input-box:has([aria-invalid='true']):hover { border-color: var(--border-error); }

.joli-login-input-box:has([aria-invalid='true']):focus-within {
  border-color: var(--border-error);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--status-error) 22%, transparent);
}

.joli-login-input-box:has([aria-invalid='true']) .joli-login-input-prefix-icon { color: var(--status-error); }

.joli-login-input-error,
.joli-login-input-hint {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin: 0.125rem 0 0;
  font-size: var(--font-size-xs);
  line-height: 1.4;
}

.joli-login-input-error { color: var(--status-error); }
.joli-login-input-hint { color: var(--text-secondary); }
```

---

## 3. Reglas de acabado profesional (obligatorias)

Aplicadas en el login del panel admin de Pandora. Sirven para cualquier formulario de acceso.

- **Etiqueta flotante:** sin fila de etiqueta aparte ([`floating_field.md`](../form/floating_field.md)). Nunca reemplazar la etiqueta por un placeholder solo.
- **Error en línea, no solo toast:** campo vacío o inválido → borde `--border-error` + mensaje bajo el campo (`<p id="{id}-error">`), `aria-invalid="true"` y `aria-describedby` apuntando al mensaje. Al enviar, el foco va al primer campo con error. El error se limpia al escribir.
- **Errores del servidor en banner fijo** (`.login-alert`, `role="alert"`) sobre el formulario; no desaparecen solos como un toast. Tras credenciales incorrectas se vacía la clave y se enfoca.
- **Aviso de Bloq Mayús** en campos de clave (`getModifierState('CapsLock')`), como `role="status"`.
- **Toggle ver/ocultar alcanzable con teclado** (sin `tabIndex={-1}`), con `aria-pressed`, área de 36 px y `:focus-visible`.
- **Alto uniforme de 48 px** (`3rem`) para inputs y botones en web; hover del borde con `--border-strong`. En la APK el campo mide 52 (ver [`floating_field.md`](../form/floating_field.md) §6).
- **Sin adornos de plantilla:** sin degradados, brillos (`glow`), saltos `translateY` en hover ni animaciones infinitas. Botón primario de color sólido; secundario con borde. Textos en mayúscula inicial normal (no `uppercase` espaciado, no Title Case en español).
- **Spinner con `currentColor`** para que contraste con el color de texto del botón.
- Todo elemento interactivo con `:focus-visible` (contorno 2 px `--border-focus`) y animaciones desactivadas con `prefers-reduced-motion`.
- El nombre accesible de un botón es su texto visible: no poner `aria-label` distinto (WCAG 2.5.3).
