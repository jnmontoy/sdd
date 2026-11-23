# Patrón UI: Encuadre de tabla con la rueda del mouse
## Spec-Driven Development (SDD)

Una tabla con alto máximo y desplazamiento interno vive dentro de una página que también se desplaza. Este patrón decide qué se mueve con la rueda del mouse: **primero la página, hasta que la tabla se vea completa y centrada; después, el interior de la tabla**.

Regla **DEBERÍA** para toda tabla con desplazamiento vertical interno (ver [`data_table.md`](./data_table.md) §1, regla 2). Se puede desviar con una decisión registrada (ADR).

---

## 0. Procedencia

Fichas técnicas de materias primas (fichas), pestañas de hallazgos agrupados por responsable: grupos de hasta 850 filas con columnas anchas. Probado en producción en noviembre de 2026.

---

## 1. Problema

Por defecto, si el puntero cae sobre la tabla, la rueda mueve el interior de la tabla aunque esta se vea solo a medias. La parte baja y la barra de desplazamiento horizontal quedan fuera de la ventana, y el usuario se desplaza sin ver lo que está recorriendo.

**Alternativa descartada:** quitar el desplazamiento interno y dejar el encabezado fijo a la página. Con tablas largas, la página queda enorme y la barra horizontal termina al fondo de cada tabla, fuera de la vista.

---

## 2. Comportamiento

1. **Rueda hacia abajo con el puntero sobre la tabla:** primero se desplaza la página hasta dejar la tabla centrada en el área visible. Después se desplaza el interior. Al llegar al final de la tabla, sigue la página: es el encadenamiento nativo del navegador.
2. **Rueda hacia arriba:** no se interviene. El navegador ya mueve primero el interior hasta arriba y luego la página.
3. **Nunca se pasa del centro.** Con trackpad avanza delta a delta y sin animación, para que se sienta natural.

**Por qué:** el usuario siempre ve la tabla completa, con su encabezado y su barra horizontal, antes de recorrer su contenido.

---

## 3. Parámetros

| Parámetro | Valor | Por qué |
| :--- | :--- | :--- |
| `areaVisible.arriba` | Alto de la barra fija superior (token de layout, p. ej. `--topbar-height`) | El centrado se calcula bajo lo que está fijo. |
| `areaVisible.alto` | `innerHeight - areaVisible.arriba` | Espacio realmente útil. |
| `--margen-encuadre-tabla` | `28px` (token) | Aire arriba y abajo. Sin margen, la tabla queda pegada al borde y se siente apretada. |
| Alto máximo de la tabla | `min(altoDeseado, 100dvh - barraFija - 2 × margen)` | Garantiza que la tabla quepa completa, con su barra horizontal. |
| `arribaCentrada` | `areaVisible.arriba + (areaVisible.alto - altoTabla) / 2` | Con la tabla al alto máximo deja exactamente un margen arriba y otro abajo. |
| Tolerancia | `1px` | Absorbe posiciones con decimales (subpíxel). |

```css
:root {
  --margen-encuadre-tabla: 28px;
}

.tabla-con-scroll {
  max-height: min(70vh, calc(100dvh - var(--topbar-height) - 2 * var(--margen-encuadre-tabla)));
  overflow: auto;
}
```

---

## 4. Regla de decisión

Se escucha `wheel` con `passive: false` **solo en el contenedor de la tabla**, nunca en `window`.

```text
delta = deltaY en px      (deltaMode 1 -> x16 por línea; 2 -> x areaVisible.alto)

si shift o ctrl o |deltaX| >= |deltaY| o delta <= 0
   o tabla.scrollHeight <= tabla.clientHeight:
    no intervenir

hastaCentrar   = tabla.rect.top - arribaCentrada(areaVisible, tabla.rect.height)
paginaRestante = documento.scrollHeight - documento.scrollTop - documento.clientHeight
falta          = min(hastaCentrar, paginaRestante)

si falta <= tolerancia:
    no intervenir          // ya centrada o más arriba: que se mueva la tabla

preventDefault()
window.scrollBy({ top: min(delta, falta), behavior: "instant" })
```

**Estructura recomendada:** la regla va en una **función pura**. Recibe la rueda, la posición de la tabla y el área visible, y devuelve los píxeles que debe bajar la página (0 significa no intervenir). Un hook (`useEncuadreConRueda(ref)`) solo mide el DOM y aplica el resultado. Se monta una vez en el componente de tabla común, no tabla por tabla.

---

## 5. Excepciones

- **Shift + rueda** (desplazamiento horizontal) y **Ctrl + rueda** (zoom): no se tocan.
- **Táctil y teclado** (flechas, AvPág, espacio): no se tocan, porque solo se escucha `wheel`.
- **Tabla sin desbordamiento vertical:** no se toca; la rueda ya mueve la página.
- **`prefers-reduced-motion`:** no aplica, porque el desplazamiento es instantáneo y respeta el delta del usuario. Si se agrega suavizado, hay que desactivarlo con esa preferencia.
- **Pestañas o barras fijas adicionales** (p. ej. pestañas dentro de una ficha): deben sumarse a `areaVisible.arriba` para que el encabezado de la tabla no quede tapado.

---

## 6. Casos de prueba

Automáticos, sobre la función pura:

1. `arribaCentrada`: tabla de 600 en un área de 800 que empieza en y=56 → 156. Con la tabla al alto máximo (800 − 2×28) → 56 + 28.
2. Tabla debajo del centro (`top` 456): delta 100 → 100; delta 3 → 3; delta 0,5 → 0,5; delta 1000 → 300 (tope en el centro, sin pasarse).
3. Tabla ya centrada (`top` 156, y 156,8 por tolerancia) o por encima (`top` −200) → 0.
4. Página sin recorrido restante → 0; con 40 px restantes → 40.
5. Rueda hacia arriba, desplazamiento horizontal dominante, Shift, Ctrl o tabla sin desbordamiento → 0.
6. `deltaMode`: 3 líneas → 48 px; 1 página → alto del área; píxeles, tal cual.

Manuales: mouse de rueda, trackpad, Shift + rueda, táctil, teclado y una ventana baja (1366×650). En todos, la tabla debe quedar con el mismo aire arriba y abajo y sin saltos.
