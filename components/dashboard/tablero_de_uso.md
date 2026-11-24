# Patrón UI: Tablero de uso (`TableroDeUso`)
## Spec-Driven Development (SDD)

Pantalla para ver **cuánto y cómo se usa** una funcionalidad (un asistente, una integración, un módulo): un rango de fechas, tarjetas de indicador, un gráfico por día y rankings de quién, qué y sobre qué. Casi todo se puede pulsar para bajar al detalle.

Estructura **DEBE** ser la misma en todas las apps que lo usen; solo cambia el **color de acento** de cada app. Se puede desviar con una decisión registrada (ADR).

> **Privacidad (DEBE, Ley 1581 de 2012):** el tablero muestra **conteos, nombres y fechas**, nunca el contenido de lo que se pidió o se escribió. Se DEBE decir en pantalla qué se cuenta (ícono de información con tooltip o una línea corta). Solo lo ve el rol que administra la funcionalidad.

---

## 0. Procedencia

Tablero de consumo de Claude en BI (modelo), replicado en noviembre de 2026 en **Fichas** (Métricas MCP, acento morado, ruta propia `/metricas-mcp`; la anterior `/uso-claude` redirige) y **App TIC** (Indicadores MCP, acento índigo, con filtro por app). Nombres de referencia en Fichas: `PanelUsoClaude`, `BarraTablero`, `Cifras`, `BarrasSerie`, `Ranking`, `EsqueletoTablero` y `domain/accesoMcp/grafico.ts`. Son solo referencia; cada proyecto usa los suyos.

---

## 1. Anatomía

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│ [* Uso] [* Fricción] [* Salud]      [BI|Fichas|Todas]  Desde [25/10] Hasta [23/11] [R] │  ← una fila
├──────────────────────────────────────────────────────────────────────────────────┤
│ Del 25 oct al 23 nov.  (i)                                                         │  ← línea corta
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │
│ │LLAMADAS  *│ │PERSONAS  * │ │CONEXIONES *│ │DENEGADAS * │ │ERRORES   ! │        │  ← indicadores
│ │ 1.380      │ │ 14         │ │ 9          │ │ 37         │ │ 4          │        │
│ │────────────│ │────────────│ │────────────│ │────────────│ │────────────│        │
│ │descripción │ │descripción │ │descripción │ │descripción │ │descripción │        │
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘        │
│ ┌──────────────────────────────────────────────────────────────────────────────┐ │
│ │ * Llamadas por día                                                           │ │
│ │──────────────────────────────────────────────────────────────────────────────│ │
│ │ 150 ┤- - - - - - - - - - - ▇ - - - - - - - - - - - - - - - - -               │ │
│ │  50 ┤- - ▅ ▃ - - - ▅ ▇ ▇ - █ ▃ - - - ▅ ▇ █ ▅ - - - ▅ ▇ █ ▆ ▃ ▅               │ │
│ │   0 ┼──────────────────────────────────────────────────────────                │ │
│ │     25 oct     29 oct     2 nov     6 nov     10 nov     14 nov                │ │
│ └──────────────────────────────────────────────────────────────────────────────┘ │
│ ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐             │
│ │* Herram.  Ver todo→│ │* Quién    Ver todo→│ │* Por MP   Ver todo→│             │  ← rankings
│ │────────────────────│ │────────────────────│ │────────────────────│             │
│ │HERRAMIENTA  VECES  │ │PERSONA      VECES  │ │CÓDIGO    CONSULTAS │             │
│ │▓▓▓▓▓▓▓▓ Ver… 512   │ │▓▓▓▓ Ana · I+D 402  │ │▓▓▓▓▓▓ MP-01  88    │             │
│ │▓▓▓▓▓ Mis…    344   │ │▓▓▓▓▓ Luis   311    │ │▓▓▓▓ MP-02    64    │             │
│ └────────────────────┘ └────────────────────┘ └────────────────────┘             │
└──────────────────────────────────────────────────────────────────────────────────┘
```

*Cifras ilustrativas.* La pantalla **arranca en la barra de pestañas**: sin título grande ni párrafo de explicación arriba. Si la app exige un título por accesibilidad, va oculto visualmente (`h1` solo para lectores de pantalla).

---

## 2. Barra superior (una sola fila)

1. **Izquierda: pestañas con ícono** (p. ej. Uso, Fricción, Salud; Reportes solo si hay datos). La activa lleva un **subrayado en el color de acento**. Patrón de pestañas ARIA: una sola en el orden de tabulación; flechas, Inicio y Fin se mueven entre ellas.
2. **Derecha: rango de fechas** «Desde / Hasta» en línea y compactos (rótulo pequeño al lado del campo, no encima), y **Actualizar como botón de ícono** con `aria-label` y tooltip.
3. **Filtros opcionales** (p. ej. segmentado por app: BI | Fichas | Todas) van entre las pestañas y el rango.
4. **Las fechas DEBEN mostrarse llenas con el rango vigente.** Si la persona no eligió fechas, el servidor usa un rango por defecto (p. ej. últimos 30 días) y lo devuelve en la respuesta (`desde`, `hasta`); los campos muestran ese rango, nunca `dd/mm/aaaa`. Si se edita una fecha, la otra conserva su valor.
5. Debajo, una **línea corta** con el rango en palabras («Del 25 de oct al 23 de nov.») y el **ícono de información** con el texto de privacidad en tooltip (enfocable con teclado).

---

## 3. Tarjetas de indicador

| Parte | Regla |
|---|---|
| Rejilla | `grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr))`. 14rem permite **5 tarjetas en una fila a 1366 px**; con un mínimo de 260 px la quinta queda sola. |
| Etiqueta | Mayúsculas, espaciado de letra ~0,06em, tamaño pequeño, gris. **Altura reservada de dos líneas** en escritorio para que las cifras queden alineadas entre tarjetas. |
| Ícono | Arriba a la derecha, en el color de acento, decorativo (`aria-hidden`). |
| Cifra | Grande y en negrita (~48 px), **derivada de un token** (p. ej. `calc(var(--text-titulo) * 2)`), nunca un tamaño suelto. Cifras tabulares. |
| Divisoria | Línea de 1 px entre la cifra y la descripción. |
| Descripción | Una frase corta en gris («37 denegadas · 4 errores», «Hoy; puedes revocarlas»). |
| Número | Separador de miles con **punto** (`Intl.NumberFormat("es-CO")`). |
| Color | **Rojo y naranja solo con significado** (errores > 0, denegadas). Sin datos malos, la cifra va en el color de texto normal. |

Fondo de tarjeta: superficie elevada con borde y sombra suave; **no** gris plano (se pierde la jerarquía).

---

## 4. Gráfico por día

- Va **dentro de una tarjeta**: encabezado con ícono y título, divisoria, gráfico.
- **Eje Y con líneas guía** (punteadas, 3 a 5) y valores redondos. Tope = siguiente paso de 1, 2 o 5 × 10ⁿ por encima del máximo; sin datos, tope 1 (no dividir por cero).
- **Fechas abajo** sin amontonar: como máximo ~8 rótulos (rotular cada `ceil(total / 8)` barras). En celular, ocultar uno de cada dos.
- **Barras en el color de acento**, de igual ancho, con un espacio pequeño en porcentaje (cabe la serie entera sin desplazamiento horizontal).
- **Tooltip** con la fecha completa y la cifra («04 de nov de 2026 · 120 llamadas») al pasar el mouse **y al enfocar** la barra.
- Fecha sin hora (`"2026-11-02"`): formatear **leyendo el texto** (o en UTC), no en la zona local, o se corre un día.
- Si toda la serie es cero: un mensaje («Sin llamadas en el rango»), no un gráfico vacío.
- La misma pieza sirve para series por hora (p. ej. errores en las últimas 48 h) con rótulo corto de hora.

---

## 5. Rankings

- Tarjetas **lado a lado** (3 en escritorio): `repeat(auto-fit, minmax(min(100%, 18rem), 1fr))`.
- Encabezado con ícono y título; **cabecera de columnas** en mayúsculas grises (nombre a la izquierda, cifra a la derecha).
- Cada fila: **barra de fondo proporcional** a su cifra (acento suave, ancho = valor / máximo; el máximo es el de la lista completa), nombre a la izquierda, **cifra en negrita** a la derecha.
- **Subtítulo en la misma línea** (p. ej. el área): va después del nombre, separado por « · », en gris y tamaño pequeño («Ana Gómez · I+D»). **Nunca en una segunda línea:** rompe la altura pareja entre tarjetas. Nombre y subtítulo comparten una sola línea con puntos suspensivos si no caben; el texto completo va en el tooltip y en el `aria-label`. **Todas las filas de todos los rankings tienen el mismo alto.**
- **Máximo 5 filas en la tarjeta.** Si hay más, el encabezado lleva a la derecha del título un enlace **«Ver todo (N) →»** con el total (un `button` con estilo de enlace, `aria-haspopup="dialog"`). Con 5 o menos, no aparece.
- «Ver todo» abre un **modal con la lista completa**, con el mismo estilo de fila (barra proporcional, misma cabecera de columnas) y **desplazamiento interno** si no cabe. Es accesible: foco atrapado dentro, **Escape cierra** y el foco **vuelve al enlace**. Cada fila del modal abre su detalle igual que en la tarjeta; al abrirlo se cierra la lista para no apilar dos ventanas (Escape cerraría ambas).
- El desglose secundario (exitosas, denegadas, errores) va en el **tooltip** de la fila o en el detalle, no en más columnas.
- Es una lista (`ol`), no una tabla: no hereda las reglas de la tabla global.
- **No inventar datos:** solo los rankings que el backend ya entrega.

---

## 6. Casi todo clicable (DEBE)

| Elemento | Lleva a |
|---|---|
| Tarjeta de indicador | Su detalle. Personas → quién; Conexiones/Autorizaciones → lista donde se revocan; Denegadas y Errores → pestaña Fricción; un conteo de una acción concreta (gestiones, mensajes) → quién usó esa herramienta. |
| Barra del gráfico | Filtra **ese día** (Desde = Hasta = el día) y recarga el tablero. |
| Fila de ranking | Abre el **detalle** filtrado (modal con navegación persona ↔ herramienta ↔ objeto y «Atrás»). |
| Tarjeta sin detalle | Se pinta como `div`, sin cursor de mano. |

Todo lo clicable es un `button` real: **cursor de mano, hover visible, foco visible** (contorno de 2 px en acento) y teclado (Enter/Espacio). El `aria-label` dice la cifra y a dónde lleva («Autorizaciones abiertas: 9. Ver y revocar»).

---

## 7. Carga

- **Esqueleto solo en la primera carga**, con la forma real: 5 tarjetas, una tarjeta de gráfico (~16rem de alto) y 3 tarjetas de ranking. Usa las mismas clases de las piezas reales para que no salte al llegar los datos.
- En recargas (cambio de rango, Actualizar) se mantiene lo visible hasta que llega lo nuevo.
- Error: mensaje en `role="alert"` arriba del contenido.

---

## 8. Responsive

| Ancho | Comportamiento |
|---|---|
| ≥ 1366 | Barra en una fila; 5 tarjetas en una fila; 3 rankings lado a lado. |
| ≤ 480 (390) | Barra en columna: pestañas con **desplazamiento horizontal** (sin barra visible) y rango debajo; tarjetas y rankings en **una columna**; gráfico más bajo (~9rem) y la mitad de los rótulos de fecha; sin altura reservada de dos líneas en las etiquetas. |

Sin desplazamiento horizontal de la página en ningún ancho (`scrollWidth === clientWidth`).

---

## 9. Acento por app

Colores y tamaños **solo desde los tokens** de cada app (`--color-accent`, `--color-accent-soft`, `--color-danger`, tamaños de texto, espacios, radios, sombras). La estructura es idéntica; el acento cambia (BI naranja, App TIC índigo, Fichas morado). Debe verse bien en tema claro y oscuro.

---

## 10. Contrato de datos (referencia)

```ts
interface RangoRespondido { desde: string; hasta: string } // AAAA-MM-DD, el rango que se usó
interface PuntoSerie { momento: string; n: number }         // día o fecha-hora ISO

interface MetricasDeUso extends RangoRespondido {
  total: number; personas_activas: number; conexiones_vivas: number;
  denegadas: number; errores: number;
  por_dia: PuntoSerie[];
  por_herramienta: { herramienta: string; llamadas: number; ok: number; denegadas: number; errores: number }[];
  por_persona: { usuario_id: number | null; nombre: string; area: string | null; llamadas: number }[];
}
```

Todo agregado en el servidor; la pantalla no suma filas para obtener totales.

---

## 11. Ubicación en la app

El tablero es **su propia entrada del menú lateral** (ícono de métricas), no una pestaña dentro de otra pantalla, con **ruta propia** (p. ej. `/metricas-mcp`) para recargar y compartir el enlace. Si la ruta cambia de nombre, la anterior **redirige** a la nueva sin dejar la vieja en el historial (los enlaces ya compartidos siguen sirviendo). El nombre del tablero se usa igual en el menú, el título oculto, la pestaña del navegador y las etiquetas accesibles. Mismos permisos en el menú, en la ruta y en el servidor: quien no tiene permiso no ve la entrada y, si entra por la ruta, cae en su pantalla por defecto.

---

## 12. Checklist antes de entregar

- [ ] Barra en una fila; fechas llenas con el rango vigente; Actualizar como ícono.
- [ ] Tarjetas alineadas, cifra grande con punto de miles, rojo/naranja solo con significado.
- [ ] Gráfico con eje, guías, fechas y tooltip con mouse y teclado; la barra filtra el día.
- [ ] Rankings con barra proporcional; máximo 5 filas y «Ver todo (N) →» con modal accesible; subtítulo en la misma línea y filas del mismo alto; cada fila abre su detalle (también desde el modal).
- [ ] Todo lo clicable con mano, hover, foco y teclado.
- [ ] Esqueleto con la forma real solo en la primera carga.
- [ ] Revisado a 1366 y 390 sin desborde horizontal, en claro y oscuro.
- [ ] Texto de privacidad visible (ícono o línea corta); ningún contenido de lo pedido.
