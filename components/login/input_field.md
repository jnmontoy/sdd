# Componente: Campo con Etiqueta Flotante y Password Toggle (`UI-COMP-LOGIN-INPUT`)
## Ubicación SDD: `.sdd/components/login/input_field.md`

Este documento especifica el **campo de texto canónico** del login (y de cualquier formulario que lo adopte): estilo *outlined* con **etiqueta flotante**. La etiqueta hace de placeholder dentro del campo y, al enfocarlo o cuando tiene valor, sube animada hasta la línea superior y la corta. Así no se necesita una fila aparte para la etiqueta y el campo no crece.

Implementación de referencia (Pandora):
- **Web (panel):** estilo genérico en `src/styles/campo-flotante.css` (clases `.campo-flotante` en la caja y `.campo-flotante-label` en la etiqueta, medidas por variables `--cf-*`); login en `CampoLogin.tsx`; `SelectFilter` con la prop `flotante`. Aquí se documenta con el prefijo SDD `joli-login-*`.
- **APK (React Native):** `src/components/formulario/CampoFlotante.tsx` (texto, clave, multilínea), `SelectorFlotante.tsx` (lista propia) y `EtiquetaFlotante.tsx` (animación compartida). Ver §5.

### 0. Alcance (obligatorio)
- **Sí:** formularios de captura de datos — login, crear/cambiar contraseña, CRUD (crear o editar usuarios, reglas, acuerdos, motivos), incluidos `<select>`, selectores propios y `<textarea>`.
- **No:** buscadores, filtros de tablas, barras de herramientas, cuadros de chat ni campos de solo consulta (detalles de una ruta, enlaces para copiar). Esos conservan su estilo.
- Selectores nativos siempre tienen valor: su etiqueta queda arriba. Selectores propios: en reposo si no hay valor y están cerrados; si están deshabilitados, la etiqueta queda arriba para que se lea su mensaje.
- Una etiqueta que lleva elementos extra (contadores, insignias como «Llave primaria») los mueve a una nota bajo el campo: dentro de la etiqueta flotante solo va texto y el `*` de obligatorio.

---

## 1. Estados visuales

| Estado | Condición CSS | Etiqueta | Corte del borde | Placeholder de ejemplo |
|---|---|---|---|---|
| **Reposo** | vacío y sin foco | Dentro del campo, tras el icono, tamaño de texto, `--text-muted` | Oculto (`opacity: 0`) | Oculto |
| **Activo** | `:focus-within` | Sobre el borde, `--font-size-xs`, `--brand-primary` | Visible | Aparece con fundido tras la subida |
| **Con valor** | `:not(:placeholder-shown)` o `:autofill` | Sobre el borde, `--text-secondary` | Visible | — |
| **Error** | `.has-error` | Igual que el estado de posición, en `--status-error` | Según posición | Según foco |
| **Deshabilitado** | input `:disabled` | Sin cambio de posición; caja con `opacity: 0.65` | Según posición | — |

### 1.1. Animación (subida y bajada)

- **Solo `transform` y `opacity`** (no animar `top`, `left` ni `font-size`: provocan saltos y recálculo de diseño).
- Posición base de la etiqueta = **posición activa** (sobre el borde). El reposo se obtiene con `transform: translate(dx, dy) scale(1.15)`, con `transform-origin: left center`:
  - `dy = 1.5rem` = mitad del alto del campo (48 px), lleva la etiqueta del borde al centro.
  - `dx` = distancia entre el inicio de la etiqueta en el borde y el inicio del texto tras el icono (`2.65rem − 0.75rem − padding escalado ≈ 1.47rem`). Recalcular si cambian el icono o el padding.
  - `scale(1.15)` lleva `--font-size-xs` a tamaño de texto del input.
- Duración **220 ms**, curva estándar `cubic-bezier(0.4, 0, 0.2, 1)` (suave en ambos extremos, para que se vea el recorrido intermedio). El color se anima con la misma curva.
- El **corte del borde** (`::before`) aparece con un fundido de `opacity` sincronizado con la subida; no cambiar el `background` directamente (los degradados no se animan).
- El **placeholder de ejemplo** aparece con fundido de 150 ms y **120 ms de retraso**, cuando la etiqueta ya dejó libre la línea.
- Con `prefers-reduced-motion: reduce` se quitan todas las transiciones (los estados cambian sin movimiento).

---

## 2. Estructura HTML / JSX

La `<label>` real va **dentro de la caja y después del input** (el estado se calcula con `:focus-within` y `:has()` sobre la caja). El input **siempre** lleva `placeholder`: un espacio `" "` si no hay texto de ejemplo, porque `:placeholder-shown` es lo que indica que está vacío.

### 2.1. Campo de documento
```html
<div class="joli-login-input-group">
  <div class="joli-login-input-box">
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
    <label for="joli-login-doc" class="joli-login-float-label">Número de documento</label>
  </div>
  <!-- Solo con error: el input lleva aria-invalid="true" y aria-describedby="joli-login-doc-error" -->
  <p id="joli-login-doc-error" class="joli-login-input-error" hidden>Escribe tu número de documento.</p>
</div>
```

### 2.2. Campo de contraseña con toggle y aviso de Bloq Mayús
```html
<div class="joli-login-input-group">
  <div class="joli-login-input-box">
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
    <label for="joli-login-pass" class="joli-login-float-label">Contraseña</label>

    <button
      type="button"
      class="joli-login-input-toggle-btn"
      aria-label="Mostrar contraseña"
      aria-pressed="false"
    >
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

### 2.3. Comportamiento
- **Toggle:** alterna `type="password"` / `type="text"`, actualiza `aria-pressed` y `aria-label` ("Mostrar contraseña" / "Ocultar contraseña"); es alcanzable con Tab (sin `tabindex="-1"`). La clave nunca se guarda en storage.
- **Error:** al enviar, los campos vacíos reciben `.has-error`, `aria-invalid="true"` y `aria-describedby` al mensaje; el foco va al primero con error. El error se limpia al escribir.
- **Aviso de Bloq Mayús:** se añade a `aria-describedby` mientras está visible; no se muestra si ya hay un error.

---

## 3. Hoja de Estilos en CSS Puro (`inputs.css`)

> **Requisito del corte:** `--bg-card` (fondo detrás del campo) y `--bg-input` / `--bg-input-focus` deben ser **colores sólidos**. Si el contenedor usa un fondo translúcido o una imagen, el corte se nota; en ese caso, no usar este estilo o igualar el fondo del corte al del contenedor.

```css
/* ==========================================================================
   COMPONENTE: CAMPO CON ETIQUETA FLOTANTE (CSS PURO)
   ========================================================================== */

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

.joli-login-input-box:hover:not(:focus-within) {
  border-color: var(--border-strong);
}

.joli-login-input-box:focus-within {
  background-color: var(--bg-input-focus);
  border-color: var(--border-focus);
  box-shadow: var(--shadow-input-focus);
}

.joli-login-input-box:has(.joli-login-input-control:disabled) {
  opacity: 0.65;
}

.joli-login-input-prefix-icon {
  position: absolute;
  left: 0.875rem;
  display: flex;
  color: var(--text-muted);
  pointer-events: none;
  transition: color var(--transition-fast);
}

.joli-login-input-box:focus-within .joli-login-input-prefix-icon {
  color: var(--brand-primary);
}

.joli-login-input-svg {
  width: 1.125rem;
  height: 1.125rem;
  display: block;
}

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

.joli-login-input-control.joli-login-has-suffix {
  padding-right: 3rem;
}

.joli-login-input-control:disabled {
  cursor: not-allowed;
}

/* ---------- Etiqueta flotante ---------- */

/* Posición base = activa: sobre la línea superior, cortándola */
.joli-login-float-label {
  --flotante-duracion: 220ms;
  --flotante-curva: cubic-bezier(0.4, 0, 0.2, 1);
  position: absolute;
  top: -1px;
  left: 0.75rem;
  max-width: calc(100% - 1.5rem);
  isolation: isolate;
  padding: 0 0.375rem;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  line-height: 1.2;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: text;
  transform: translateY(-50%);
  transform-origin: left center;
  transition:
    transform var(--flotante-duracion) var(--flotante-curva),
    color var(--flotante-duracion) var(--flotante-curva);
}

/* Corte del borde: fondo partido detrás de la etiqueta (mitad tarjeta, mitad campo) */
.joli-login-float-label::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(to bottom, var(--bg-card) 50%, var(--bg-input) 50%);
  opacity: 1;
  transition: opacity var(--flotante-duracion) var(--flotante-curva);
}

.joli-login-input-box:focus-within .joli-login-float-label::before {
  background: linear-gradient(to bottom, var(--bg-card) 50%, var(--bg-input-focus) 50%);
}

/* Reposo: vacío y sin foco → la etiqueta baja a la línea del texto y hace de placeholder */
.joli-login-input-box:not(:focus-within):has(.joli-login-input-control:placeholder-shown:not(:autofill))
  .joli-login-float-label {
  transform: translate(1.47rem, calc(-50% + 1.5rem)) scale(1.15);
  color: var(--text-muted);
}

.joli-login-input-box:not(:focus-within):has(.joli-login-input-control:placeholder-shown:not(:autofill))
  .joli-login-float-label::before {
  opacity: 0;
}

.joli-login-input-box:focus-within .joli-login-float-label {
  color: var(--brand-primary);
}

/* Placeholder de ejemplo: solo con foco, con fundido cuando la etiqueta ya subió */
.joli-login-input-control::placeholder {
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 150ms ease 120ms;
}

.joli-login-input-control:focus::placeholder {
  opacity: 0.7;
}

/* ---------- Toggle ver/ocultar ---------- */

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

.joli-login-input-toggle-btn:hover:not(:disabled) {
  color: var(--text-primary);
  background-color: var(--bg-hover);
}

.joli-login-input-toggle-btn:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 0;
}

/* ---------- Error y avisos ---------- */

.joli-login-input-group.has-error .joli-login-input-box,
.joli-login-input-group.has-error .joli-login-input-box:hover {
  border-color: var(--border-error);
}

.joli-login-input-group.has-error .joli-login-input-box:focus-within {
  border-color: var(--border-error);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--status-error) 22%, transparent);
}

.joli-login-input-group.has-error .joli-login-input-prefix-icon,
.joli-login-input-group.has-error .joli-login-float-label,
.joli-login-input-group.has-error .joli-login-input-box:not(:focus-within):has(.joli-login-input-control:placeholder-shown)
  .joli-login-float-label {
  color: var(--status-error);
}

.joli-login-input-error,
.joli-login-input-hint {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin: 0.125rem 0 0;
  font-size: var(--font-size-xs);
  line-height: 1.4;
}

.joli-login-input-error {
  color: var(--status-error);
}

.joli-login-input-hint {
  color: var(--text-secondary);
}

@media (prefers-reduced-motion: reduce) {
  .joli-login-float-label,
  .joli-login-float-label::before,
  .joli-login-input-control::placeholder {
    transition: none;
  }
}
```

---

## 4. Reglas de acabado profesional (obligatorias)

Aplicadas en el login del panel admin de Pandora (`CampoLogin.tsx`). Sirven para cualquier formulario de acceso.

- **Etiqueta flotante (sección 1):** sin fila de etiqueta aparte; la `<label>` real dentro de la caja, después del input. Nunca reemplazar la etiqueta por un placeholder solo (el placeholder desaparece al escribir y no lo anuncian bien los lectores de pantalla).
- **Error en línea, no solo toast:** campo vacío o inválido → borde `--border-error` + mensaje bajo el campo (`<p id="{id}-error">`), `aria-invalid="true"` y `aria-describedby` apuntando al mensaje. Al enviar, el foco va al primer campo con error. El error se limpia al escribir.
- **Errores del servidor en banner fijo** (`.login-alert`, `role="alert"`) sobre el formulario; no desaparecen solos como un toast. Tras credenciales incorrectas se vacía la clave y se enfoca.
- **Aviso de Bloq Mayús** en campos de clave (`getModifierState('CapsLock')`), como `role="status"`.
- **Toggle ver/ocultar alcanzable con teclado** (sin `tabIndex={-1}`), con `aria-pressed`, área de 36 px y `:focus-visible`.
- **Alto uniforme de 48 px** (`3rem`) para inputs y botones; hover del borde con `--border-strong`.
- **Sin adornos de plantilla:** sin degradados, brillos (`glow`), saltos `translateY` en hover ni animaciones infinitas. Botón primario de color sólido; secundario con borde. Textos en mayúscula inicial normal (no `uppercase` espaciado, no Title Case en español).
- **Spinner con `currentColor`** para que contraste con el color de texto del botón.
- Todo elemento interactivo con `:focus-visible` (contorno 2 px `--border-focus`) y animaciones desactivadas con `prefers-reduced-motion`.
- El nombre accesible de un botón es su texto visible: no poner `aria-label` distinto (WCAG 2.5.3).

---

## 5. Versión APK (React Native)

Mismo comportamiento que la web, con `Animated` del núcleo de React Native (sin dependencias nuevas):

- **`EtiquetaFlotante`:** `Animated.Value` de 0 (reposo) a 1 (activo), `Animated.timing` de 220 ms, `Easing.bezier(0.4, 0, 0.2, 1)`, `useNativeDriver: true`. Interpola `translateX`, `translateY` y `scale` con `transformOrigin: "left center"`. El corte del borde son dos `View` (mitad `fondoExterior`, mitad `fondoCampo`) con `opacity` animada. Con «reducir movimiento» (`AccessibilityInfo.isReduceMotionEnabled`) la duración es 0. El valor animado se crea con `useState(() => new Animated.Value(...))` (la regla `react-hooks/refs` rechaza leer `useRef().current` en render).
- **Colores por contenedor:** cada pantalla pasa `colores: ColoresCampo` (`fondoExterior`, `fondoCampo`, `borde`, `bordeFoco`, `texto`, `textoSecundario`), porque el fondo detrás del campo cambia entre modal, panel y tarjeta.
- **Medidas:** alto 52, borde 1.5 (no cambia de grosor con foco: solo de color, para no mover el diseño), radio 14, icono 20 + separación 10. En reposo, `dy = alto/2 − borde/2`; multilínea, `dy = rellenoY + líneaTexto/2`.
- **Accesibilidad:** el `TextInput` lleva `accessibilityLabel` = etiqueta; la etiqueta visual se oculta a lectores de pantalla para no leerse dos veces. El ojo de la clave es un `Pressable` con `accessibilityRole="button"` y etiqueta "Mostrar/Ocultar contraseña".
- **Placeholder** solo con foco (`placeholder={enfocado ? texto : undefined}`).
- `llenar` hace que un multilínea ocupe el alto restante (paneles de motivo); `SelectorFlotante` expone `onLayout` para ubicar listas flotantes debajo.
