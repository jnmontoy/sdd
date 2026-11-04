# 06. Diseño UI/UX, Tokens de Diseño y Accesibilidad
## Módulo de Login / Autenticación — SDD Joli Foods (`SPEC-AUTH-001`)

Identidad visual, interacción y accesibilidad de la pantalla de inicio de sesión. La composición de componentes y su código están en [`11_componentes_de_la_pagina.md`](./11_componentes_de_la_pagina.md).

---

## 1. Tokens de `variables.css`

La página DEBERÍA consumir solo los tokens de [`variables.css`](../../../components/variables.css), que define modo noche y modo día (`[data-theme='light']`). **Por qué:** el contraste se verifica una sola vez en los tokens y no se rompe al cambiar de tema.

| Uso | Tokens |
| :--- | :--- |
| Tipografía | `--font-family`, `--font-size-sm`, `--font-size-base` |
| Texto | `--text-primary`, `--text-secondary`, `--text-muted` |
| Tarjeta | `--glass-bg`, `--glass-blur`, `--glass-border`, `--glass-shadow`, `--border-card-accent` |
| Campos | `--input-bg`, `--input-border`, `--input-focus-border`, `--input-focus-ring`, `--input-placeholder` |
| Marca y acción | `--brand-primary`, `--brand-primary-hover`, `--brand-glow`, `--text-on-brand` |
| Error | `--status-error`, `--alert-error-bg`, `--alert-error-border`, `--alert-error-text` |
| Fondo | `--bg-viewport`, `--orb-color-primary`, `--orb-color-secondary` |

> La paleta actual de `variables.css` (verde) está pendiente de alinearse con la identidad de marca Joli (morado, amarillo, azul, naranja; Gotham y Arvo). Es una decisión de negocio fuera de este documento; al cambiar los tokens, el login se actualiza sin tocar su CSS.

---

## 2. Anatomía

El login es una de las excepciones permitidas al diseño a todo lo ancho: la **tarjeta de inicio de sesión se centra** en el viewport. Variante opcional: pantalla dividida (arte institucional a la izquierda, tarjeta a la derecha) en pantallas ≥ 1200 px.

```
+-------------------------------------------------------------+
|                 [ LOGO DE LA APLICACIÓN ]                   |
|                  <Nombre del proyecto>                      |
|                                                             |
|   Número de documento                                       |
|   [ [IdCard] 1000000001                                 ]   |
|   (error en línea si aplica)                                |
|                                                             |
|   Contraseña                                                |
|   [ [Lock] ••••••••••••                        [Ojo]    ]   |
|                                                             |
|   [x] Recordar mi documento    ¿Olvidaste tu contraseña?    |
|                                                             |
|   [            INGRESAR  (o spinner de carga)           ]   |
|                                                             |
|   ------------------- o continúa con -------------------    |
|   [ [MS] Iniciar sesión con Microsoft 365               ]   |
|                                                             |
|              Joli Foods • Acceso corporativo                |
+-------------------------------------------------------------+
```

---

## 3. Estados de Interacción

1. **Hover del botón principal:** transición `var(--transition-fast)`, color `--brand-primary-hover` y sombra con `--brand-glow`.
2. **Foco visible:** anillo `box-shadow: var(--shadow-input-focus)` (color base `--input-focus-ring`) con contraste ≥ 3:1 frente al fondo (WCAG 2.4.7 / 1.4.11). NO DEBE quitarse el `outline` sin reemplazo.
3. **Enviando:** botón e inputs deshabilitados (`disabled`), spinner y texto "Ingresando…"; el botón conserva su ancho para evitar saltos.
4. **Error:** borde `--status-error` en el campo, mensaje en línea y animación de sacudida de 300 ms que DEBE desactivarse con `@media (prefers-reduced-motion: reduce)`.

---

## 4. Accesibilidad (WCAG 2.1 AA)

- **A11y-01 Contraste:** texto normal ≥ 4.5:1 y texto grande ≥ 3:1 en ambos temas.
- **A11y-02 Teclado:** orden de tabulación `Documento → Contraseña → Ver contraseña → Recordar → ¿Olvidaste…? → Ingresar → Microsoft`. `Enter` en un campo envía el formulario; `Espacio` activa casilla y botones.
- **A11y-03 ARIA:** cada campo tiene `<label htmlFor>`, `aria-invalid` y `aria-describedby` hacia su mensaje de error; el botón de ojo usa `aria-label` dinámico ("Mostrar contraseña" / "Ocultar contraseña") y `aria-pressed`; la alerta general usa `role="alert"`.
- **A11y-04 Zoom:** sin pérdida de contenido ni scroll horizontal al 200 % de zoom y a 320 px de ancho (reflow 1.4.10).
- **A11y-05 Autocompletado:** `autoComplete="username"` en documento y `autoComplete="current-password"` en contraseña, para que los gestores de contraseñas funcionen.
