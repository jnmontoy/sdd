# 06. Diseño UI/UX, Design Tokens y Accesibilidad
## Módulo de Login / Autenticación — SDD Greenyard (`GY-SPEC-AUTH-001`)

Este documento establece la identidad visual, tokens de diseño, ergonomía interactiva y lineamientos de accesibilidad para la interfaz de inicio de sesión de Greenyard.

---

## 1. Sistema Central de Textos y Temas: `variables.css`

La página de Login y todos sus componentes consumen obligatoriamente el archivo central [`variables.css`](../../../components/variables.css), el cual define la tipografía, escala de textos y el soporte reactivo para **Modo Noche (Dark Mode)** y **Modo Día (Light Mode)** mediante el atributo `[data-theme='light']`.

### 1.1. Tokens Clave Consumidos por el Login
- **Tipografía Global**: `var(--font-family)`, `var(--font-size-sm)`, `var(--font-size-base)`.
- **Textos Reactivos**: `var(--text-primary)`, `var(--text-secondary)`, `var(--text-muted)`.
- **Superficie de Tarjeta**: `var(--bg-card)`, `var(--glass-blur)`, `var(--glass-shadow)`.
- **Campos de Entrada**: `var(--bg-input)`, `var(--border-subtle)`, `var(--shadow-input-focus)`.
- **Marca y Acciones**: `var(--brand-primary)`, `var(--brand-primary-hover)`, `var(--brand-glow)`.
- **Alertas y Errores**: `var(--status-error)`, `var(--alert-error-bg)`, `var(--alert-error-border)`.

---

## 2. Anatomía de la Interfaz y Jerarquía de Componentes

La página de inicio de sesión sigue un patrón de **Tarjeta Flotante Centralizada (Centered Glass Card)** para resoluciones móviles y medianas, y opcionalmente **Pantalla Dividida (Split Screen)** para pantallas grandes con arte corporativo institucional.

```
+-------------------------------------------------------------+
|                                                             |
|                    [ LOGO GREENYARD ]                       |
|               "Portal de Identidad Digital"                 |
|                                                             |
|   +-----------------------------------------------------+   |
|   | Documento de Identidad                              |   |
|   | [ [Icon: IdCard] Ingrese su cédula                ] |   |
|   | Error en línea si aplica                            |   |
|   +-----------------------------------------------------+   |
|                                                             |
|   +-----------------------------------------------------+   |
|   | Contraseña                                          |   |
|   | [ [Icon: Lock] ••••••••••••••••   [Icon: Eye/Off] ] |   |
|   +-----------------------------------------------------+   |
|                                                             |
|   [x] Recordar mi documento      ¿Olvidaste tu contraseña?  |
|                                                             |
|   +-----------------------------------------------------+   |
|   | [   INICIAR SESIÓN  (o Spinner de carga)   ]        |   |
|   +-----------------------------------------------------+   |
|                                                             |
|   ------------------ o también ----------------------       |
|                                                             |
|   +-----------------------------------------------------+   |
|   | [Icon: MS Logo] Iniciar sesión con Microsoft 365    |   |
|   +-----------------------------------------------------+   |
|                                                             |
|             Greenyard © 2026 — Acceso Seguro                |
+-------------------------------------------------------------+
```

---

## 3. Microinteracciones y Estados de Interacción

1. **Estado Hover en Botón Principal**:
   - Transición de 200ms `ease-in-out` con elevación leve de escala (`scale: 1.01`) y halo esmeralda `box-shadow: 0 10px 25px -5px var(--gy-brand-glow)`.
2. **Estado Focus Visible en Inputs**:
   - Anillo de enfoque de 2px `focus:ring-2 focus:ring-emerald-500` con contraste superior a 3:1 frente al fondo.
3. **Estado de Carga (Submitting)**:
   - Botón deshabilitado (`pointer-events: none; opacity: 0.75`).
   - El texto del botón es reemplazado por un spinner `animate-spin` y la etiqueta *"Autenticando..."*.
4. **Retroalimentación de Error**:
   - El campo inválido se ilumina con borde carmesí (`--gy-status-error`).
   - Animación de sacudida leve (Shake animation de 300ms) para advertir visualmente del fallo.

---

## 4. Requisitos de Accesibilidad (WCAG 2.1 AA)

- **A11y-01 (Ratio de Contraste)**: Todos los textos principales tienen un ratio de contraste mínimo de **4.5:1** frente a su fondo contenedor. Los textos grandes cumplen al menos 3:1.
- **A11y-02 (Navegación por Teclado)**:
  - Secuencia de tabulación lógica: `Documento -> Contraseña -> Toggle Ojo -> Checkbox -> Botón Submit -> Enlace Olvido -> Botón Microsoft`.
  - La tecla `Enter` en cualquier input desencadena el envío del formulario.
  - La tecla `Espacio` conmuta el checkbox de "Recuérdame" y el botón de visibilidad de contraseña.
- **A11y-03 (Lectores de Pantalla - ARIA)**:
  - Campos de entrada provistos de `aria-required="true"`, `aria-invalid="true|false"` y `aria-describedby` apuntando al identificador del mensaje de error correspondiente.
  - Botón de alternar contraseña con `aria-label="Mostrar contraseña"` o `aria-label="Ocultar contraseña"` dinámico.
- **A11y-04 (Zoom y Reflow)**:
  - La interfaz se adapta sin pérdida de funcionalidad ni solapamiento de elementos con niveles de zoom de hasta 200%.
