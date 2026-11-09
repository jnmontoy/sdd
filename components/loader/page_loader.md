# Especificación de Componente: Cargadores y Skeletons (`PageLoader` / `TableSkeleton` / `CardSkeleton`)
## Spec-Driven Development (SDD)

> **Origen:** patrón tomado de contenedores (`PageLoader`), app_tic (`AppLoader`), tiendita (`UserTableSkeleton`), vibra (`UserSkeletons`) y JoliVerso (cortinilla de transición entre apps). Aquí se describe de forma genérica.

Familia de indicadores de espera: cargador de página y *skeletons* (siluetas grises que imitan el contenido mientras llega), para que el usuario sepa que algo está cargando y la página no "salte" al aparecer los datos.

---

## 0. Implementación de referencia (Pandora, pantallas de tabla)

> Patrón completo de la pantalla: [`admin_table_screen.md`](../data_table/admin_table_screen.md). Lo de esta sección manda sobre el resto del documento cuando se contradicen; lo marcado **«Deuda en la referencia»** es lo que el código aún no cumple y NO se copia.

- Primera carga: `TableSkeleton` (8 filas, columnas visibles) dentro de la tarjeta de la tabla.
- La cortinilla `PageLoader variant="curtain"` (mensaje + submensaje) se muestra al cargar el módulo. En recargas DEBERÍA bastar con el giro del botón Recargar y `aria-busy` en la tarjeta. *(Deuda en la referencia: Usuarios la muestra en cada recarga.)*
- Los huesos `.joli-skeleton-bone` respetan `prefers-reduced-motion`.

---

### 1. Variantes y cuándo usarlas

| Variante | Uso |
| :--- | :--- |
| `PageLoader variant="inline"` | Carga de una sección o de una ruta dentro del layout. |
| `PageLoader variant="overlay"` | Operación que bloquea la vista actual (p. ej. procesar un archivo). |
| `PageLoader variant="curtain"` | Cortinilla de pantalla completa al entrar a la app o al pasar de una app a otra (logo + anillo + título configurable, p. ej. "Accediendo a [Nombre del Proyecto]"). |
| `TableSkeleton` | Primera carga de una tabla (cabecera + N filas). En recargas posteriores se mantiene la tabla y se muestra el spinner de [`DataTable`](../data_table/data_table.md). |
| `CardSkeleton` | Primera carga de una rejilla de tarjetas. |

- **Regla:** los skeletons DEBERÍAN usarse solo en la **primera** carga; DEBERÍAN respetar `prefers-reduced-motion` (sin brillo animado).
- **Regla:** toda pantalla con datos remotos DEBERÍA tener indicador de primera carga; un texto «Cargando…» dentro del estado vacío o un spinner suelto no reemplaza al esqueleto. Listas y paneles laterales (chats, contactos, permisos) arman su esqueleto con las mismas clases de la fila real y `.joli-skeleton-bone`, para que no salte al llegar los datos.
- **Accesibilidad:** el cargador usa `role="status"` con texto legible; los skeletons son decorativos (`aria-hidden="true"`) y el contenedor que los aloja indica `aria-busy="true"`.

---

### 2. Implementación TypeScript / React (`src/components/ui/PageLoader.tsx`)

```tsx
import React from 'react';
import './PageLoader.css';

export interface PageLoaderProps {
  message?: string;
  subMessage?: string;
  variant?: 'inline' | 'overlay' | 'curtain';
  logoSrc?: string;
}

export const PageLoader: React.FC<PageLoaderProps> = ({
  message = 'Cargando información...',
  subMessage = 'Por favor espera un momento',
  variant = 'inline',
  logoSrc = '/assets/logoJoli.png',
}) => (
  <div className={`joli-loader-container joli-loader-${variant}`} role="status" aria-live="polite">
    <div className="joli-loader-box">
      <div className="joli-loader-logo-ring" aria-hidden="true">
        <span className="joli-loader-ring" />
        <img src={logoSrc} alt="" className="joli-loader-logo" />
      </div>
      <p className="joli-loader-title">{message}</p>
      {subMessage && <p className="joli-loader-subtitle">{subMessage}</p>}
    </div>
  </div>
);

export interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

export const TableSkeleton: React.FC<TableSkeletonProps> = ({ rows = 5, columns = 6 }) => (
  <div className="joli-table-skeleton" aria-hidden="true">
    <div className="joli-skeleton-header-row">
      {Array.from({ length: columns }, (_, c) => (
        <div key={c} className="joli-skeleton-bone skeleton-th" />
      ))}
    </div>
    {Array.from({ length: rows }, (_, r) => (
      <div key={r} className="joli-skeleton-tr">
        {Array.from({ length: columns }, (_, c) => (
          <div key={c} className="joli-skeleton-cell">
            {/* Anchos variables y deterministas para imitar texto real */}
            <div className="joli-skeleton-bone" style={{ width: `${60 + ((c * 17 + r * 7) % 35)}%` }} />
          </div>
        ))}
      </div>
    ))}
  </div>
);

export const CardSkeleton: React.FC<{ count?: number }> = ({ count = 6 }) => (
  <div className="joli-card-skeleton-grid" aria-hidden="true">
    {Array.from({ length: count }, (_, i) => (
      <div key={i} className="joli-card-skeleton">
        <div className="joli-skeleton-bone skeleton-avatar" />
        <div className="joli-skeleton-bone" style={{ width: '70%' }} />
        <div className="joli-skeleton-bone" style={{ width: '45%' }} />
        <div className="joli-skeleton-bone skeleton-footer" />
      </div>
    ))}
  </div>
);
```

Uso con estado de carga:

```tsx
<section aria-busy={isFirstLoad}>
  {isFirstLoad ? <TableSkeleton rows={8} columns={columns.length} /> : <DataTable {...props} />}
</section>
```

---

### 3. Estilos CSS (`PageLoader.css`)

```css
.joli-loader-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.joli-loader-inline {
  min-height: 360px;
}

.joli-loader-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  background: color-mix(in srgb, var(--bg-viewport) 60%, transparent);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.joli-loader-curtain {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  background: var(--bg-viewport);
}

.joli-loader-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  text-align: center;
}

.joli-loader-logo-ring {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
}

.joli-loader-ring {
  position: absolute;
  inset: 0;
  border: 2.5px solid var(--border-subtle);
  border-top-color: var(--brand-primary);
  border-radius: var(--radius-full);
  animation: joliSpin 1.2s linear infinite;
}

.joli-loader-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.joli-loader-title {
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.joli-loader-subtitle {
  margin: 4px 0 0;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

/* Skeletons: colores derivados de tokens, válidos en ambos temas */
.joli-skeleton-bone {
  height: 14px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-active) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: joliShimmer 1.5s infinite;
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

.joli-skeleton-header-row {
  background: var(--bg-elevated);
}

.skeleton-th,
.joli-skeleton-cell {
  flex: 1;
}

.joli-card-skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
  width: 100%;
}

.joli-card-skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
}

.skeleton-footer {
  height: 26px;
  margin-top: 0.5rem;
}

@keyframes joliSpin {
  to { transform: rotate(360deg); }
}

@keyframes joliShimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .joli-skeleton-bone { animation: none; }
  .joli-loader-ring { animation-duration: 3s; }
}
```
