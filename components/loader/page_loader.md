# Especificación de Componente: Cargadores y Esqueletos (`PageLoader` / `TableSkeleton` / `BlockSkeleton`)
## Spec-Driven Development (SDD)

> **Origen:** patrón tomado de contenedores (`PageLoader`), app_tic (`AppLoader`), tiendita (`UserTableSkeleton`), vibra (`UserSkeletons`), JoliVerso (cortinilla de transición entre apps) y Fichas (`CargadorPagina`, `EsqueletoBloques`). Aquí se describe de forma genérica.

Familia de indicadores de espera: el cargador con el logo de la marca y los *esqueletos* (siluetas grises que imitan el contenido mientras llega). Sirven para que la persona sepa que algo está cargando y para que la página no "salte" al aparecer los datos.

---

## 0. Implementaciones de referencia y qué manda

Hay dos referencias. Cada una manda en lo suyo; lo marcado **«Deuda en la referencia»** es lo que el código aún no cumple y NO se copia.

| Tema | Manda | Referencia |
| :--- | :--- | :--- |
| Aspecto del cargador (anillos, logo, fondo, mensaje) | Esta especificación, secciones 2 y 3 | Fichas (`CargadorPagina`) y App TIC (`AppLoader`), que ya coinciden |
| Cuándo mostrar cortinilla, esqueleto o giro en pantallas de tabla | [`admin_table_screen.md`](../data_table/admin_table_screen.md) | Pandora |
| Esqueleto de listas, paneles y tarjetas | Sección 4 | Fichas (`EsqueletoBloques`) |

**Pandora (pantallas de tabla):**

- Primera carga: `TableSkeleton` (8 filas, columnas visibles) dentro de la tarjeta de la tabla.
- La cortinilla `PageLoader variant="curtain"` (mensaje + submensaje) se muestra al cargar el módulo. En recargas DEBERÍA bastar con el giro del botón Recargar y `aria-busy` en la tarjeta. En las pantallas de tabla la condición es `cargando && datos.length === 0`. Una recarga con datos visibles y sin botón Recargar (p. ej. Logs al cambiar de archivo) atenúa la tabla con `.joli-table-wrapper.is-recargando`.
- **Deuda en la referencia:** si el `PageLoader` de Pandora todavía dibuja un solo anillo con logo PNG y fondo sólido (el diseño de la versión anterior de esta especificación), se migra al aspecto de la sección 2 la próxima vez que se toque. Las reglas de uso de Pandora no cambian.

**Fichas (arranque, páginas y paneles):**

- Arranque de sesión, carga del usuario e ingreso: cortinilla con mensaje visible ("Verificando sesión", "Cargando", "Ingresando").
- Carga de una página diferida, del perfil o de una página puente: variante en línea.
- Paneles y listas con datos remotos: `BlockSkeleton` con las clases de la fila real (sección 4).
- Tablas: la tabla común ya dibuja su propio esqueleto cuando recibe `loading`; no se agrega un `TableSkeleton` aparte (ver sección 1).

---

## 1. Variantes y cuándo usarlas

| Variante | Uso |
| :--- | :--- |
| `PageLoader variant="curtain"` | Pantalla completa al entrar a la app, al recuperar la sesión, al iniciar sesión o al pasar de una app a otra. Título configurable, p. ej. "Verificando sesión" o "Accediendo a [Nombre del Proyecto]". |
| `PageLoader variant="inline"` | Carga de una página o de una sección dentro del layout (respaldo de `Suspense`, perfil, páginas puente). |
| `PageLoader variant="overlay"` | Operación que bloquea la vista actual (p. ej. procesar un archivo). Mismo aspecto que la cortinilla; cambia el uso, no el diseño. |
| `TableSkeleton` | Primera carga de una tabla (cabecera + N filas). Si la tabla común del proyecto ya dibuja su esqueleto con `loading`, se usa ese y no se duplica. En recargas posteriores se mantiene la tabla y se muestra el spinner de [`DataTable`](../data_table/data_table.md). |
| `BlockSkeleton` | Primera carga de listas, paneles laterales, historias, tarjetas y bloques de texto (sección 4). Reemplaza al antiguo `CardSkeleton`: una rejilla de tarjetas es un `BlockSkeleton` con las clases de la tarjeta. |

- **Regla (solo primera carga):** los esqueletos se muestran **solo cuando aún no hay datos**: la condición es `cargando && datos === null` (o `datos.length === 0`), nunca `cargando` a secas. Una recarga con datos visibles mantiene los datos y, como mucho, muestra el giro del botón Actualizar.
- **Regla:** toda pantalla con datos remotos DEBERÍA tener indicador de primera carga; un texto «Cargando…» suelto, dentro del estado vacío o un spinner suelto no reemplaza al esqueleto.
- **Regla:** una sola implementación de cada pieza, reutilizable. Si una forma se repite, sale del componente común; no se copia el marcado del esqueleto en cada panel.
- **Fuera de alcance:** el texto o el giro dentro de un botón ("Cargando…" / "Ver anteriores", ícono `Loader2` mientras guarda) y el valor provisional de un campo de cabecera no son cargas de pantalla y no llevan cortinilla ni esqueleto.
- **Accesibilidad:** el cargador usa `role="status"` y `aria-live="polite"` con texto legible; los huesos del esqueleto son decorativos (`aria-hidden="true"`) y su envoltura indica `aria-busy="true"` e incluye un texto oculto con `role="status"` para lectores de pantalla.
- **Movimiento reducido:** con `prefers-reduced-motion: reduce` los anillos y el logo se ralentizan (no se detienen: siguen indicando actividad) y el brillo de los esqueletos se apaga.

---

## 2. Implementación TypeScript / React (`src/components/ui/PageLoader.tsx`)

Aspecto: tres anillos concéntricos que giran a distinto ritmo y sentido, el logo de la marca en SVG al centro latiendo suavemente y, debajo, un mensaje visible opcional.

```tsx
import { createPortal } from 'react-dom';
import logoUrl from '../../assets/brand/logo.svg'; // isotipo de la marca en SVG (en Fichas, flor.svg)
import './PageLoader.css';

export type PageLoaderVariant = 'curtain' | 'inline' | 'overlay';

export interface PageLoaderProps {
  variant?: PageLoaderVariant;
  /** Visible debajo del logo y leído por lectores de pantalla. */
  message?: string;
  subMessage?: string;
  logoSrc?: string;
}

export function PageLoader({
  variant = 'inline',
  message = 'Cargando',
  subMessage,
  logoSrc = logoUrl,
}: PageLoaderProps) {
  const loader = (
    <div className={`joli-loader joli-loader-${variant}`} role="status" aria-live="polite">
      <div className="joli-loader-rings" aria-hidden="true">
        <span className="joli-loader-ring" />
        <span className="joli-loader-ring" />
        <span className="joli-loader-ring" />
        <img src={logoSrc} alt="" className="joli-loader-logo" />
      </div>
      {message && <p className="joli-loader-message">{message}</p>}
      {subMessage && <p className="joli-loader-submessage">{subMessage}</p>}
    </div>
  );
  // Cortinilla y overlay van al body para cubrir toda la pantalla sobre cualquier layout.
  return variant === 'inline' ? loader : createPortal(loader, document.body);
}
```

Uso en el arranque (ver [`protected_route.md`](../routing/protected_route.md)):

```tsx
if (isLoading) return <PageLoader variant="curtain" message="Verificando sesión" />;
```

---

## 3. Estilos CSS (`PageLoader.css`)

**Fondo de la cortinilla:** es el color de fondo del tema, translúcido y con desenfoque; **no negro**. Los anillos y el texto usan los colores de texto del tema; en tema claro son oscuros y sobre un negro al 75 % casi no se leen. Con el fondo del tema se leen en los dos temas sin cambiar nada más.

```css
.joli-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-6);
}

.joli-loader-curtain,
.joli-loader-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-loader); /* por encima de --z-modal: ver nota abajo */
  background: color-mix(in srgb, var(--bg-viewport) 80%, transparent);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.joli-loader-inline {
  width: 100%;
  min-height: 40vh;
}

.joli-loader-rings {
  position: relative;
  display: grid;
  place-items: center;
  width: 120px;
  height: 120px;
}

.joli-loader-ring {
  position: absolute;
  border: 3px solid transparent;
  border-radius: var(--radius-full);
}
.joli-loader-ring:nth-child(1) {
  width: 100%;
  height: 100%;
  border-top-color: var(--text-primary);
  animation: joliSpin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}
.joli-loader-ring:nth-child(2) {
  width: 85%;
  height: 85%;
  border-right-color: var(--text-secondary);
  animation: joliSpin 2s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite reverse;
}
.joli-loader-ring:nth-child(3) {
  width: 115%;
  height: 115%;
  border-bottom-color: var(--text-muted);
  animation: joliSpin 2.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.joli-loader-logo {
  position: absolute;
  width: 50px;
  height: auto;
  animation: joliPulse 2s ease-in-out infinite;
}

.joli-loader-message,
.joli-loader-submessage {
  margin: 0;
  text-align: center;
}
.joli-loader-message {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
.joli-loader-submessage {
  margin-top: calc(var(--space-6) * -1 + var(--space-1));
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

@keyframes joliSpin {
  to { transform: rotate(360deg); }
}
@keyframes joliPulse {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.1); opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  .joli-loader-ring,
  .joli-loader-logo {
    animation-duration: 6s;
  }
}
```

- **Capa (z-index):** `--z-loader` DEBE quedar por encima de `--z-modal`. Si el cargador y un modal comparten capa y los dos van al `body`, el cargador puede quedar debajo del modal (lección de Pandora en `memory/learnings/bug_lessons.md`).

---

## 4. Esqueleto de bloques (`BlockSkeleton`)

Un solo componente para listas, historias, paneles y tarjetas. No inventa su propio marcado: recibe las **clases del contenedor y de la fila real**, de modo que la silueta ocupa el mismo lugar, con los mismos bordes y separaciones, que el contenido que va a llegar. Dentro de cada bloque dibuja barras de ancho variable y estable (no cambian entre renders) que imitan texto.

```tsx
import type { CSSProperties } from 'react';

type Container = 'ul' | 'ol' | 'div';

export interface BlockSkeletonProps {
  count?: number;          // número de filas o tarjetas
  lines?: number;          // barras por fila
  as?: Container;          // 'div' para rejillas y listas de definición
  containerClassName?: string; // clase del contenedor real (p. ej. la lista)
  blockClassName?: string;     // clase de la fila o tarjeta real
  message?: string;        // texto oculto para lectores de pantalla
}

const MIN_WIDTH = 45;
const WIDTH_RANGE = 45;

// Anchos variables pero deterministas, para imitar texto real sin parpadear.
const lineWidth = (block: number, line: number) =>
  `${MIN_WIDTH + ((block * 17 + line * 29) % WIDTH_RANGE)}%`;

export function BlockSkeleton({
  count = 3, lines = 2, as = 'ul', containerClassName, blockClassName = '', message = 'Cargando',
}: BlockSkeletonProps) {
  const Wrapper = as;
  const Block = as === 'div' ? 'div' : 'li';
  return (
    <div className="joli-skeleton" aria-busy="true">
      <span className="visually-hidden" role="status">{message}</span>
      <Wrapper className={containerClassName} aria-hidden="true">
        {Array.from({ length: count }, (_, b) => (
          <Block key={b} className={`${blockClassName} joli-skeleton-block`.trim()}>
            {Array.from({ length: lines }, (_, l) => (
              <span key={l} className="joli-skeleton-bone joli-skeleton-line"
                style={{ '--width': lineWidth(b, l) } as CSSProperties} />
            ))}
          </Block>
        ))}
      </Wrapper>
    </div>
  );
}
```

Uso (lista de personas de un chat; las clases son las de la fila real):

```tsx
{loading && people.length === 0 && (
  <BlockSkeleton containerClassName="chat-people" blockClassName="chat-row" count={6} />
)}
```

- **Especificidad:** algunas filas reales centran su contenido o definen su propio `display`. Las reglas del esqueleto van anidadas bajo `.joli-skeleton` para que no las pise el estilo de la fila.
- **Relleno en la cabecera:** si la fila real pone su relleno en un hijo (p. ej. el botón de cabecera de un grupo plegable) y no en la fila, la hoja de estilos de ese módulo agrega el relleno a `.joli-skeleton .<fila>.joli-skeleton-block`. No se le pone al esqueleto la clase del hijo, porque arrastra estilos que no corresponden (p. ej. `border: 0`).
- **Tablas:** dentro de una tabla no se usa `BlockSkeleton`; se usa el esqueleto de la tabla (sección 5).

---

## 5. Esqueleto de tabla y estilos compartidos

`TableSkeleton` se usa cuando la tabla del proyecto no dibuja su propio esqueleto. Si la tabla común ya acepta `loading` y pinta filas de huesos (caso de Fichas), se usa esa y no se crea otra pieza.

```tsx
export function TableSkeleton({ rows = 5, columns = 6 }: { rows?: number; columns?: number }) {
  return (
    <div className="joli-table-skeleton" aria-hidden="true">
      <div className="joli-skeleton-header-row">
        {Array.from({ length: columns }, (_, c) => <div key={c} className="joli-skeleton-bone skeleton-th" />)}
      </div>
      {Array.from({ length: rows }, (_, r) => (
        <div key={r} className="joli-skeleton-tr">
          {Array.from({ length: columns }, (_, c) => (
            <div key={c} className="joli-skeleton-cell">
              <div className="joli-skeleton-bone" style={{ width: `${60 + ((c * 17 + r * 7) % 35)}%` }} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
```

```tsx
<section aria-busy={isFirstLoad}>
  {isFirstLoad ? <TableSkeleton rows={8} columns={columns.length} /> : <DataTable {...props} />}
</section>
```

```css
/* Hueso común: tablas y bloques. Colores derivados de tokens, válidos en ambos temas. */
.joli-skeleton-bone {
  display: block;
  height: 0.75rem;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-active) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: joliShimmer 1.4s ease-in-out infinite;
}

.joli-skeleton { width: 100%; }

.joli-skeleton .joli-skeleton-block {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--space-2);
  pointer-events: none;
}

.joli-skeleton .joli-skeleton-line {
  width: var(--width, 70%);
  margin: 0;
}

.joli-table-skeleton {
  width: 100%;
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}
.joli-skeleton-header-row,
.joli-skeleton-tr {
  display: flex;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
}
.joli-skeleton-header-row { background: var(--bg-elevated); }
.skeleton-th,
.joli-skeleton-cell { flex: 1; }

@keyframes joliShimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .joli-skeleton-bone { animation: none; }
}
```

---

## 6. Tokens usados y equivalencias en Fichas

Los nombres de esta especificación son genéricos. Cada proyecto los mapea a sus tokens; no se crean alias si el proyecto ya tiene los suyos.

| Token genérico | Fichas |
| :--- | :--- |
| `--bg-viewport` | `--color-bg` |
| `--text-primary` / `--text-secondary` / `--text-muted` | `--color-text` / `--color-text-muted` / `--color-text-faint` |
| `--font-size-sm` | `--text-pequeno` |
| `--z-loader` | `--z-cargador` |
| `--bg-elevated` / `--bg-active` (huesos) | `--color-surface-hover` / `--color-border` |
| `--space-*`, `--radius-*` | iguales |
| `PageLoader` / `curtain` / `inline` | `CargadorPagina` / `cortina` / `en-linea` (Fichas no usa `overlay`) |
| `BlockSkeleton` / `.joli-skeleton-bone` | `EsqueletoBloques` / `.esqueleto-barra` |

---

## 7. Lista de verificación

- [ ] El arranque de sesión muestra la cortinilla con mensaje visible, no un texto suelto sobre fondo blanco.
- [ ] Una sola implementación de `PageLoader` y de `BlockSkeleton`; ningún panel copia su marcado.
- [ ] Los esqueletos solo aparecen sin datos (`cargando && datos === null`); en recargas se mantienen los datos.
- [ ] `role="status"` + `aria-live` en el cargador; `aria-busy` en la envoltura del esqueleto y huesos con `aria-hidden`.
- [ ] Con `prefers-reduced-motion` los anillos se ralentizan y el brillo de los huesos se apaga.
- [ ] La cortinilla se lee en tema claro y oscuro (fondo del tema translúcido, no negro).
- [ ] Revisado en pantalla grande (~1920), portátil (~1366) y celular (~390), sin barra horizontal.
