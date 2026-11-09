# Componente: Campo con Etiqueta Flotante (`UI-COMP-FORM-FLOATING-FIELD`)
## Ubicación SDD: `sdd/components/form/floating_field.md`

Campo de formulario estilo *outlined* (con borde) cuya **etiqueta hace de placeholder** dentro del campo y, al enfocarlo o cuando tiene valor, **sube animada hasta la línea superior y la corta**. Así no se necesita una fila aparte para la etiqueta y el campo no crece.

Es el **campo estándar de todo formulario de captura** (login, contraseñas, crear o editar registros), en web y en apps React Native. Se extrajo de Pandora (panel admin y APK); la especificación es genérica.

| Plataforma | Implementación de referencia (Pandora) |
| :--- | :--- |
| Web (React + CSS) | `frontend-admin/src/styles/campo-flotante.css` (estilo genérico, clases `campo-flotante*`); login en `components/login/CampoLogin.tsx`; selector propio con `SelectFilter` prop `flotante` |
| React Native (Expo) | `frontend/src/components/formulario/`: `CampoFlotante.tsx` (texto, clave, multilínea), `SelectorFlotante.tsx` (lista propia), `EtiquetaFlotante.tsx` (animación compartida); login en `components/login/LoginTextField.tsx` |

---

## 1. Alcance (OBLIGATORIO)

**SÍ se usa en formularios de captura de datos:**
- Login y recuperación de contraseña.
- Crear, cambiar o confirmar contraseña.
- Formularios CRUD: crear o editar usuarios, reglas, acuerdos, perfiles, motivos, observaciones.
- Dentro de esos formularios: `<input>`, `<select>` nativo, selectores propios (`SelectFilter`, listas desplegables) y `<textarea>` / campos multilínea.

**NO se usa (conservan su estilo propio):**
- Buscadores (barras de búsqueda de tablas, listas, chats, contactos, catálogos).
- Filtros de tablas y barras de herramientas ([`expandable_filter_group.md`](../dropdown/expandable_filter_group.md), [`checklist_popover.md`](../data_table/checklist_popover.md)).
- El cuadro para escribir mensajes de un chat.
- Campos de solo consulta **fuera de un formulario** (ficha de detalle de un registro, enlaces para copiar). Un campo de solo lectura **dentro** de un formulario de captura (p. ej. «Contrato de uso aceptado» en el drawer de usuario) SÍ lleva etiqueta flotante, con candado y `aria-readonly`, para no romper la rejilla ([`drawer.md`](../drawer/drawer.md) §1.2).
- Casillas, interruptores y radios.

> **Razón:** el estilo da más presencia al formulario donde el usuario captura datos; en filtros y buscadores, que se usan a cada rato, sería intrusivo y ocuparía espacio sin aportar.

**Casos de borde:**
- Un **`<select>` nativo** siempre tiene valor: su etiqueta queda siempre arriba.
- Un **selector propio** está en reposo si no hay valor y está cerrado. Si está **deshabilitado**, la etiqueta queda arriba para que se lea su mensaje (p. ej. «Todos los clientes tienen regla»).
- Una etiqueta con **elementos extra** (contador de caracteres, insignia «Llave primaria») los mueve a una nota bajo el campo: dentro de la etiqueta flotante solo va texto y el `*` de obligatorio.
- Una **fila de datos que se edita en línea** (modo lectura y edición en la misma fila) puede conservar su diseño: cambiarla altera también el modo lectura.

---

## 2. Estados

| Estado | Condición | Etiqueta | Corte del borde | Texto de ejemplo (placeholder) |
| :--- | :--- | :--- | :--- | :--- |
| **Reposo** | vacío y sin foco | Dentro del campo, tras el icono, tamaño de texto, color tenue | Oculto | Oculto |
| **Activo** | con foco | Sobre el borde, tamaño pequeño, color de foco (marca) | Visible | Aparece con fundido tras la subida |
| **Con valor** | tiene valor o lo autocompletó el navegador | Sobre el borde, color secundario | Visible | — |
| **Error** | `aria-invalid="true"` (web) | Igual posición, en color de error | Según posición | Según foco |
| **Deshabilitado** | control deshabilitado | No cambia de posición; caja con opacidad 0.6–0.65 | Según posición | — |

---

## 3. Animación

- **Solo `transform` y `opacity`.** No animar `top`, `left` ni `font-size` (provocan saltos y recálculo del diseño).
- La **posición base es la activa** (sobre el borde). El reposo se obtiene con `translate(dx, dy) scale(s)` y origen `left center`:
  - `dy` = distancia del borde a la línea del texto: mitad del alto del campo (una línea) o `relleno superior + media línea` (multilínea).
  - `dx` = `inicio del texto − inicio de la etiqueta − relleno de la etiqueta × s`.
  - `s` = `tamaño del texto del campo / tamaño de la etiqueta` (≈ 1.15–1.17).
- **Duración 220 ms**, curva `cubic-bezier(0.4, 0, 0.2, 1)`: suave en ambos extremos, para que se vea el recorrido intermedio. Con curvas muy bruscas al inicio (p. ej. `0.16, 1, 0.3, 1`) o 150 ms se ve como un salto.
- El **corte del borde** aparece con un fundido de `opacity` sincronizado con la subida. Los degradados no se animan: nunca cambiar el `background` para mostrarlo u ocultarlo.
- El **placeholder de ejemplo** aparece con fundido de 150 ms y **120 ms de retraso**, cuando la etiqueta ya dejó libre la línea.
- Con **«reducir movimiento»** del sistema (`prefers-reduced-motion` en web, `AccessibilityInfo.isReduceMotionEnabled` en RN) los estados cambian sin animación.

---

## 4. El corte del borde

La etiqueta tapa la línea del borde con un **fondo partido**: mitad superior del color de lo que hay detrás del campo (tarjeta, modal, panel) y mitad inferior del color del campo.

- **Requisito:** ambos colores DEBEN ser **sólidos**. Sobre fondos translúcidos, imágenes o degradados el corte se nota: en ese caso no usar este estilo o igualar el fondo del corte al del contenedor.
- **Cada contenedor declara su fondo:** en web con `--cf-fondo-exterior` (por defecto `--bg-card`); en RN con `colores.fondoExterior`. Un campo en un modal usa el color del modal, no el de la página.
- La etiqueta queda centrada sobre la línea del borde (en web `top: -1px` si la etiqueta vive dentro de la caja con borde; `0` si vive en una envoltura sin borde cuyo hijo trae el borde, como `<textarea>` o `SelectFilter`).
- El grupo del campo suma un **relleno superior** (≈ 0.45–0.5 rem / 8 px) para la mitad de la etiqueta que sobresale.

---

## 5. Web: estructura

La `<label>` real va **dentro de la caja y después del control**. El estado se calcula con `:focus-within` y `:has()` sobre la caja. Todo `input`/`textarea` lleva `placeholder` (un espacio `" "` si no hay ejemplo), porque `:placeholder-shown` es lo que indica que está vacío.

### 5.1. Input con icono (formulario de panel lateral)
```tsx
<div className="drawer-form-field">
  <div className="drawer-input-control campo-flotante has-icon">
    <Mail size={15} className="drawer-input-icon" />
    <input
      id="campo-correo"
      type="email"
      className="drawer-field-input"
      placeholder="usuario@empresa.com"
      value={correo}
      onChange={(e) => setCorreo(e.target.value)}
      required
    />
    <label htmlFor="campo-correo" className="campo-flotante-label">
      Correo corporativo <span className="req">*</span>
    </label>
  </div>
</div>
```

### 5.2. Select nativo
Igual que 5.1, con `<select>` en lugar de `<input>`. No necesita `placeholder`: la etiqueta queda siempre arriba.

### 5.3. Textarea (control con borde propio)
```tsx
<div className="drawer-form-field campo-flotante-grupo">
  <div className="campo-flotante campo-flotante-envoltura campo-flotante-multilinea">
    <textarea id="campo-texto" className="mi-textarea" placeholder=" " value={texto} onChange={...} />
    <label htmlFor="campo-texto" className="campo-flotante-label">
      Texto del contrato <span className="req">*</span>
    </label>
  </div>
</div>
```

### 5.4. Selector propio (`SelectFilter`)
```tsx
<SelectFilter id="regla-atc" label="ATC asignado" flotante options={opciones} value={atc} onChange={setAtc} />
```
Con `flotante`, el componente pone `campo-flotante campo-flotante-envoltura` en su contenedor, añade `is-vacio` cuando no hay valor, está cerrado y no está deshabilitado, y dibuja la etiqueta después del disparador. **Sin `flotante`** (filtros) conserva su etiqueta de siempre. Ver [`select_filter.md`](../dropdown/select_filter.md).

### 5.5. Contraseña
Igual que 5.1 con `has-suffix` y el botón ver/ocultar después de la etiqueta: `type="button"`, `aria-label` «Mostrar contraseña» / «Ocultar contraseña», `aria-pressed`, alcanzable con Tab (sin `tabIndex={-1}`). Si el campo lleva además un botón pegado a la derecha (p. ej. «Requiere cambio de contraseña»), ver el patrón `drawer-input-group` en [`drawer.md`](../drawer/drawer.md) §1.2.

### 5.6. Variables por contenedor
| Variable | Qué es | Valor por defecto |
| :--- | :--- | :--- |
| `--cf-alto` | alto del campo | `40px` (panel lateral) |
| `--cf-texto-x` | dónde empieza el texto | `0.75rem`; `2.35rem` con `.has-icon` |
| `--cf-label-x` | dónde se posa la etiqueta | `0.5rem` |
| `--cf-pad` | relleno horizontal de la etiqueta | `0.3125rem` |
| `--cf-escala` | texto del campo / etiqueta | `1.1667` |
| `--cf-reposo-y` | borde → línea del texto (multilínea) | mitad de `--cf-alto` |
| `--cf-fondo-exterior` | fondo detrás del campo | `--bg-card` |
| `--cf-fondo-campo` / `--cf-fondo-campo-foco` | fondo del campo / con foco | `--bg-input` |

Ejemplos: el login usa `--cf-alto: 3rem; --cf-texto-x: 2.65rem; --cf-label-x: 0.75rem; --cf-pad: 0.375rem; --cf-escala: 1.15; --cf-fondo-campo-foco: var(--bg-input-focus)`. Un formulario compacto de 34 px solo cambia `--cf-alto: 34px`.

### 5.7. CSS canónico (`campo-flotante.css`)
```css
.campo-flotante {
  --cf-alto: 40px;
  --cf-texto-x: 0.75rem;
  --cf-label-x: 0.5rem;
  --cf-pad: 0.3125rem;
  --cf-escala: 1.1667;
  --cf-duracion: 220ms;
  --cf-curva: cubic-bezier(0.4, 0, 0.2, 1);
  --cf-top: -1px;
  position: relative;
}

/* Control con borde propio (textarea, SelectFilter): la línea está en el borde del hijo */
.campo-flotante.campo-flotante-envoltura { --cf-top: 0px; }
.campo-flotante.has-icon { --cf-texto-x: 2.35rem; }
.campo-flotante.campo-flotante-multilinea { --cf-texto-x: 0.9rem; --cf-reposo-y: 1.5rem; }

/* Espacio para la mitad de la etiqueta que sobresale del borde */
.drawer-form-field:has(> .campo-flotante),
.drawer-form-field:has(> .drawer-input-group > .campo-flotante),
.campo-flotante-grupo {
  padding-top: 0.45rem;
}

/* Posición base = activa: sobre la línea superior */
.campo-flotante-label {
  position: absolute;
  top: var(--cf-top);
  left: var(--cf-label-x);
  z-index: 1;
  max-width: calc(100% - var(--cf-label-x) * 2);
  isolation: isolate;
  padding: 0 var(--cf-pad);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  line-height: 1.2;
  text-transform: none;
  letter-spacing: 0;
  color: var(--cf-color, var(--text-secondary));
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: text;
  user-select: none;
  pointer-events: none;
  transform: translateY(-50%);
  transform-origin: left center;
  transition:
    transform var(--cf-duracion) var(--cf-curva),
    color var(--cf-duracion) var(--cf-curva);
}

.campo-flotante-label .req { color: var(--status-error); }

/* Corte del borde: fondo partido detrás de la etiqueta */
.campo-flotante-label::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(
    to bottom,
    var(--cf-fondo-exterior, var(--bg-card)) 50%,
    var(--cf-fondo-campo, var(--bg-input)) 50%
  );
  opacity: 1;
  transition: opacity var(--cf-duracion) var(--cf-curva);
}

.campo-flotante:focus-within .campo-flotante-label {
  color: var(--cf-color-foco, var(--brand-primary));
}

.campo-flotante:focus-within .campo-flotante-label::before {
  background: linear-gradient(
    to bottom,
    var(--cf-fondo-exterior, var(--bg-card)) 50%,
    var(--cf-fondo-campo-foco, var(--cf-fondo-campo, var(--bg-input))) 50%
  );
}

/* Reposo: vacío y sin foco → la etiqueta baja a la línea del texto y hace de placeholder */
.campo-flotante:not(:focus-within):has(:is(input, textarea):placeholder-shown:not(:autofill)) .campo-flotante-label,
.campo-flotante.is-vacio:not(:focus-within) .campo-flotante-label {
  transform: translate(
      calc(var(--cf-texto-x) - var(--cf-label-x) - var(--cf-pad) * var(--cf-escala)),
      calc(-50% + var(--cf-reposo-y, calc(var(--cf-alto) / 2)))
    )
    scale(var(--cf-escala));
  font-weight: var(--font-weight-regular);
  color: var(--cf-color-reposo, var(--text-muted));
}

.campo-flotante:not(:focus-within):has(:is(input, textarea):placeholder-shown:not(:autofill))
  .campo-flotante-label::before,
.campo-flotante.is-vacio:not(:focus-within) .campo-flotante-label::before {
  opacity: 0;
}

/* Error: aria-invalid pinta la etiqueta en rojo en cualquier posición */
.campo-flotante:has([aria-invalid='true']) {
  --cf-color: var(--status-error);
  --cf-color-foco: var(--status-error);
  --cf-color-reposo: var(--status-error);
}

/* El texto de ejemplo solo aparece con foco, cuando la etiqueta ya subió */
.campo-flotante :is(input, textarea)::placeholder {
  opacity: 0;
  transition: opacity 150ms ease 120ms;
}

.campo-flotante :is(input, textarea):focus::placeholder { opacity: 0.7; }
.campo-flotante.is-vacio:not(:focus-within) .joli-select-placeholder { opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .campo-flotante-label,
  .campo-flotante-label::before,
  .campo-flotante :is(input, textarea)::placeholder {
    transition: none;
  }
}
```

---

## 6. React Native (Expo)

Mismo comportamiento, con `Animated` del núcleo de React Native (sin dependencias nuevas).

```tsx
<CampoFlotante
  etiqueta="Nueva contraseña"
  icono="lock-closed-outline"
  esClave
  placeholder="Mínimo 8 caracteres"
  value={clave}
  onChangeText={setClave}
  colores={coloresCampo}
  escalaFuente={escalaFuente}
/>

<SelectorFlotante etiqueta="Motivo" valor={causa} abierto={listaAbierta} onPress={alternarLista} colores={coloresCampo} />
```

- **`EtiquetaFlotante`:** `Animated.Value` de 0 (reposo) a 1 (activo); `Animated.timing` de 220 ms con `Easing.bezier(0.4, 0, 0.2, 1)` y `useNativeDriver: true`. Interpola `translateX`, `translateY` y `scale` con `transformOrigin: "left center"`. El corte del borde son dos `View` (mitad `fondoExterior`, mitad `fondoCampo`) con `opacity` animada. El valor animado se crea con `useState(() => new Animated.Value(...))`: la regla de lint `react-hooks/refs` rechaza leer `useRef().current` durante el render.
- **Colores por contenedor:** cada pantalla pasa `colores: ColoresCampo` (`fondoExterior`, `fondoCampo`, `borde`, `bordeFoco`, `texto`, `textoSecundario`), porque el fondo detrás del campo cambia entre página, modal, panel y tarjeta. Si la misma pantalla se muestra en una tarjeta en escritorio web, el fondo exterior es el de la tarjeta.
- **Medidas:** alto 52, borde 1.5 (con foco cambia solo de color, no de grosor, para no mover el diseño), radio 14, icono 20 + separación 10, texto 15 y etiqueta 12 (× escala de letra del usuario). En reposo `dy = alto/2 − borde/2`; multilínea `dy = relleno superior + líneaTexto/2`.
- **Opciones:** `esClave` (ojo para ver), `multilinea` + `altoMinimo`, `llenar` (el multilínea ocupa el alto restante), `debajo` (contador o medidor bajo el campo), `editable`, `keyboardType`, `maxLength`. `SelectorFlotante` expone `onLayout` para ubicar listas flotantes debajo.
- **Placeholder** solo con foco: `placeholder={enfocado ? ejemplo : undefined}`.

---

## 7. Accesibilidad

- **Web:** `<label htmlFor>` real asociada al control (nunca reemplazar la etiqueta por un placeholder solo: desaparece al escribir y los lectores de pantalla no lo anuncian bien). La etiqueta tiene `pointer-events: none`: un clic sobre ella llega al control.
- **RN:** el `TextInput` lleva `accessibilityLabel` = etiqueta; la etiqueta visual se oculta a los lectores (`accessibilityElementsHidden`, `importantForAccessibility="no-hide-descendants"`) para no leerse dos veces. El selector usa `accessibilityRole="button"` y `accessibilityState={{ expanded }}`.
- **Error** con `aria-invalid="true"` y `aria-describedby` al mensaje bajo el campo.
- **Foco visible** en el campo (borde y anillo de foco) y en el botón del ojo.
- **Contraste:** la etiqueta en reposo usa el color tenue del tema; verificar que se lea en modo claro.

## 8. Textos
- Etiquetas con **mayúscula inicial solamente** («Número de documento», no «Número de Documento» ni «NÚMERO DE DOCUMENTO»).
- El texto de ejemplo empieza por «Ej.» o describe el formato («Mínimo 8 caracteres»); no repite la etiqueta.

## 9. Lista de revisión
- [ ] El formulario es de captura (§1); no es un buscador, filtro ni chat.
- [ ] La etiqueta está dentro de la caja, después del control, asociada con `htmlFor` / `accessibilityLabel`.
- [ ] Todo `input`/`textarea` web tiene `placeholder` (un espacio si no hay ejemplo).
- [ ] El fondo exterior declarado coincide con el contenedor real y es sólido.
- [ ] Reposo alineado con el texto tras el icono; si cambian icono, relleno o alto, se recalculan `dx`/`dy`.
- [ ] La animación se ve en ambos sentidos y desaparece con «reducir movimiento».
- [ ] Autocompletado del navegador: la etiqueta queda arriba (`:autofill`).
- [ ] Revisado en modo claro y oscuro, abriendo la pantalla.
