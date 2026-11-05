# Regla de Maquetación: Layout Horizontal a Ancho Completo
## Spec-Driven Development (SDD)

### La regla

- **Regla:** las vistas del sistema autenticado (páginas, tablas, tableros, módulos operativos) DEBERÍAN ocupar todo el ancho disponible (`width: 100%`), sin contenedores estrechos centrados (`max-w-xl`, `max-w-2xl`, `max-w-4xl`, `mx-auto`, `items-center justify-center` en el contenedor de la vista).
- **Por qué:** son herramientas de gestión de datos (tablas con muchas columnas, filtros en línea, KPIs, reportes). Un contenedor estrecho amontona columnas, recorta nombres, fuerza scroll horizontal y desperdicia buena parte del monitor.
- **Excepciones:**
  1. Diálogos modales (`ModalDialog`, `ConfirmModal`, `SignatureModal`, `ScannerModal`, `SessionExpirationModal`) sobre un fondo difuminado.
  2. La tarjeta de inicio de sesión ([`login/card.md`](../login/card.md)) antes de autenticarse.
  3. Contenido de lectura larga (p. ej. ayuda o términos), donde un ancho de línea limitado (~75 caracteres) mejora la lectura.
  4. Cualquier otra desviación con pedido explícito del usuario o decisión registrada (ADR).

---

## 1. Qué evitar y qué usar

| Elemento | Evitar (centrado / estrecho) | Usar (ancho completo) |
| :--- | :--- | :--- |
| **Contenedor de la vista** | `<div class="container max-w-4xl mx-auto flex flex-col items-center">` | `<div class="page-wrapper-full">` |
| **Barra superior** ([`navbar.md`](./navbar.md)) | Barra centrada o con márgenes vacíos | 100% del viewport: marca y título a la izquierda, controles de sesión a la derecha. |
| **Barra de filtros y búsqueda** | Apilada verticalmente o en caja centrada | Barra horizontal continua (`.filter-topbar-full`) con controles en línea ([`expandable_filter_group.md`](../dropdown/expandable_filter_group.md)). |
| **Tablas** ([`data_table.md`](../data_table/data_table.md)) | Tablas en tarjetas pequeñas con scroll forzado | La tabla usa todo el ancho disponible. |
| **Tarjetas KPI** | Apiladas en columna o centradas | Rejilla fluida `repeat(auto-fit, minmax(220px, 1fr))`. |
| **Acciones** ([`icon_action_group.md`](../button/icon_action_group.md)) | Botones centrados o dispersos | Caja compacta alineada a izquierda o derecha. |

---

## 2. Contenedor de ancho completo

### CSS (tokens de `variables.css`)

```css
.page-wrapper-full {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  min-height: calc(100vh - var(--topbar-height));
  padding: 1.25rem 1.5rem;
  box-sizing: border-box;
}

.kpi-grid-full {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  width: 100%;
}

.filter-topbar-full {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.table-wrapper-full {
  width: 100%;
  overflow-x: auto;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

@media (max-width: 768px) {
  .page-wrapper-full { padding: 1rem; }
}
```

### React

```tsx
import React from 'react';

export const PageContainer: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <main className="page-wrapper-full">{children}</main>
);
```

---

## 3. Verificación en revisión de código

En revisión (manual o con una regla de lint), se marca como hallazgo de diseño una vista autenticada cuyo contenedor raíz contenga:
- `max-w-xl` / `max-w-2xl` / `max-w-4xl` junto con `mx-auto`.
- `min-h-screen flex items-center justify-center`.

Se corrige llevando el contenedor a ancho completo, salvo que aplique una de las excepciones.
