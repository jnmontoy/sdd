# Patrón UI: Anchos de columna y alto de fila
## Spec-Driven Development (SDD)

Cómo se reparten los anchos de las columnas y cuánto puede medir una fila en una tabla cuyas celdas pueden ocupar más de una línea. Objetivo: que ninguna palabra se parta a la mitad y que ninguna fila se dispare de alto por los datos.

Regla **DEBERÍA** para toda tabla con `table-layout: fixed` (ver [`data_table.md`](./data_table.md) §1, regla 5). Se puede desviar con una decisión registrada (ADR).

---

## 0. Procedencia

Fichas técnicas de materias primas (fichas), tablas virtuales de las pestañas de hallazgos. Probado en producción en noviembre de 2026. Nombres de referencia en ese proyecto: `useAnchosCongelados.ts` (medición de anchos) y las clases `col-texto-largo`, `col-pedido` y `texto-recortado`. Son solo referencia; cada proyecto usa los suyos.

---

## 1. Problema (lección)

En una pestaña, una fila llegó a medir **unos 500 px** de alto y, en una pantalla más angosta, una columna partía palabras a la mitad («obligat orio»). Dos causas que se sumaban:

1. **Anchos congelados en porcentaje y medidos una sola vez.** Con `table-layout: fixed` el navegador ignora el ancho mínimo del contenido; al angostarse la caja, el porcentaje encogía la columna por debajo de lo que necesitaba su palabra más larga.
2. **`overflow-wrap: anywhere` en la celda.** Permite partir en cualquier carácter, así que el navegador puede encoger la columna hasta el ancho de una letra. La celda se vuelve una tira vertical y la fila crece sin límite.

A eso se sumaba una celda que mostraba una lista completa (todos los documentos de un pedido), así que el alto dependía de cuántos datos trajera la fila.

---

## 2. Reglas

1. **Anchos congelados en píxeles, medidos de nuevo con la caja.** Los anchos se miden una vez con la distribución automática del navegador (`table-layout: auto`) y se congelan en **píxeles**; nunca en porcentaje. Se vuelven a medir cada vez que cambia el ancho de la caja de la tabla (`ResizeObserver`). Si las columnas no caben, la tabla se desplaza de lado; no se encogen por debajo de lo medido. Las columnas ocultas (`display: none`, p. ej. las secundarias en celular) **no cuentan**: los anchos se reparten entre las visibles, en orden.
2. **Nunca `overflow-wrap: anywhere` dentro de una tabla.** Las celdas usan `overflow-wrap: break-word`, que solo parte una palabra cuando por sí sola no cabe. Toda columna de texto libre lleva un **ancho mínimo con una clase** (no con estilo en línea), para que ninguna medición la deje por debajo de una palabra normal.
3. **Ninguna celda crece con los datos.** Una lista o un texto largo se **resume** en la celda, con un máximo de unas **tres líneas** (`-webkit-line-clamp: 3`), y el detalle completo se abre en el panel de la fila (drawer o fila expandida). Ejemplo: en lugar de listar todos los documentos, la celda dice «4 documentos · 4 obligatorios» y sus estados; la lista vive en el panel.
4. **Celdas alineadas arriba; encabezados abajo.** Con filas de varias líneas, `vertical-align: top` en `td` deja el inicio de cada dato a la misma altura; `vertical-align: bottom` en `th` alinea los títulos de una y de dos líneas sobre la misma base.

**Por qué:** el alto de la fila queda acotado por diseño (tres líneas), no por los datos, y el ancho de cada columna nunca baja de lo que su contenido necesita. Si falta espacio, aparece desplazamiento horizontal, que el [encuadre con la rueda](./encuadre_con_rueda.md) mantiene a la vista.

---

## 3. Alcance y relación con otros documentos

| Caso | Qué aplica |
| :--- | :--- |
| Tabla de una sola línea por celda (`white-space: nowrap` + `text-overflow: ellipsis`, como [`data_table.md`](./data_table.md) §4 y [`admin_table_screen.md`](./admin_table_screen.md) §4.2) | Ya cumple las reglas 2 y 3. Puede seguir con `vertical-align: middle`: todas las filas miden lo mismo. |
| Tabla con anchos declarados o que el usuario redimensiona ([`column_resizer.md`](./column_resizer.md)) | Mandan esos píxeles; la regla 1 solo cubre las columnas **sin** ancho declarado. Las reglas 2, 3 y 4 aplican igual si la celda puede partir líneas. |
| Tabla con celdas de varias líneas (texto libre, listas, varios datos apilados) | Las cuatro reglas. |
| Tabla con desplazamiento interno dentro de una página que también se desplaza | Además, [`encuadre_con_rueda.md`](./encuadre_con_rueda.md). |

---

## 4. CSS de referencia

```css
.tabla-multilinea {
  table-layout: fixed;
}

.tabla-multilinea th {
  vertical-align: bottom;
}

.tabla-multilinea td {
  vertical-align: top;
  overflow-wrap: break-word;   /* nunca anywhere */
}

/* Ancho mínimo por clase en columnas de texto libre */
.tabla-multilinea .col-texto-largo {
  min-width: 16rem;
}

/* Resumen acotado: el detalle va en el panel de la fila */
.texto-recortado {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  overflow: hidden;
}
```

**Medición (estructura recomendada):** un hook (`useAnchosCongelados(refTabla, columnasVisibles)`) pone la tabla en `table-layout: auto`, lee el ancho de cada encabezado visible, congela esos píxeles en las columnas y vuelve a `fixed`. Repite la medición desde un `ResizeObserver` sobre la caja de la tabla. Se monta una vez en el componente de tabla común, no tabla por tabla.

---

## 5. Casos de prueba

Manuales, en pantalla grande (~1920), portátil (~1366) y celular (~390):

1. Ninguna palabra aparece partida a la mitad en ningún ancho; buscar a propósito la columna con la palabra más larga.
2. Ninguna fila supera el alto de tres líneas más su relleno, aun con el registro que trae la lista más larga.
3. Al angostar la ventana, los anchos se vuelven a medir; si no caben, aparece la barra horizontal en lugar de columnas aplastadas.
4. En celular, con las columnas secundarias ocultas, las visibles ocupan el ancho sin huecos.
5. El detalle resumido en la celda se puede ver completo en el panel de la fila.
6. En una fila con celdas de distinto alto, el primer renglón de cada celda queda a la misma altura; los encabezados de una y dos líneas comparten base.
