# Regla Inflexible de Maquetación: Layout 100% Horizontal (Prohibido Desarrollos Centrados)
## Ecosistema Corporativo Jolifoods — Metodología Spec-Driven Development (SDD)

> [!CAUTION]
> **DIRECTRIZ DE DISEÑO FRONTEND DE CUMPLIMIENTO OBLIGATORIO PARA TODA IA Y DESARROLLADOR**:
> **NINGÚN DESARROLLO, MÓDULO O PANTALLA DEBE ESTAR CENTRADO EN EL FRONTEND**.  
> Está estrictamente prohibido que la IA o el programador generen interfaces donde el contenido principal quede encogido o flotando en una columna estrecha en el centro de la pantalla (ej. `max-w-xl`, `max-w-2xl`, `max-w-4xl`, `mx-auto`, `items-center justify-center` en el contenedor de vista).
> 
> **TODO DESARROLLO DEBE EXTENDERSE A LO LARGO DE LA PANTALLA EN HORIZONTAL (FULL-WIDTH 100%)**, aprovechando de extremo a extremo todo el ancho del monitor de trabajo.

---

## 1. Justificación Operativa Empresarial
Las soluciones de Jolifoods (`app_tic`, `tiendita`, `vibra`, `contenedores`, `porterias`, `bi`, `proyectovideo`) son herramientas de gestión masiva de datos, monitoreo de procesos, tablas financieras tipo Excel, reportería en tiempo real y porterías operativas.
- **Centrar la vista** en cajas estrechas provoca apiñamiento de columnas en las tablas, mutilación de nombres, scrollbar horizontal artificial y desperdicio del 60% del área útil del monitor del usuario.
- **El layout horizontal fluido (100% width)** garantiza visualización cómoda de múltiples columnas, filtros desplegados en una sola línea, KPIs en rejilla horizontal amplia y máximo aprovechamiento ergonómico de la jornada laboral.

---

## 2. Lo que está PROHIBIDO vs. Lo que es OBLIGATORIO

| Elemento | ❌ PROHIBIDO (Centrado / Bloque Estrecho) | ✅ OBLIGATORIO (Horizontal a lo Largo de la Pantalla) |
| :--- | :--- | :--- |
| **Contenedor Principal de Vista** | `<div class="container max-w-4xl mx-auto flex flex-col items-center">` | `<div class="view-container-full w-full" style="width: 100%; min-width: 100%;">` |
| **TopHeader / Barra Superior** | Barra centrada o con márgenes laterales vacíos | Ocupa el **100% del viewport de borde a borde**. Branding a la izquierda extrema, controles a la derecha extrema. |
| **Barra de Filtros y Búsqueda** | Apilada verticalmente o en caja centrada | Barra horizontal continua (`.filter-topbar`) expandida al 100% con inputs, selects y botones en línea fluida. |
| **Tablas de Datos (`DataTable`)** | Tablas encerradas en tarjetas pequeñas con scroll forzado | La tabla se extiende a lo largo de todo el ancho disponible (`width: 100%`), permitiendo visualizar todas las columnas cómodamente. |
| **Tarjetas KPI** | Tarjetas apiladas en columna o centradas en el medio | Rejilla inteligente horizontal fluida (`display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); width: 100%;`). |
| **Toolbar de Acciones** | Botones centrados o dispersos | Caja compacta alineada a la izquierda o derecha ocupando el flujo horizontal natural de la vista. |

---

## 3. Únicas Excepciones Permitidas de Centrado
El centrado en el viewport se restringe **únicamente** a los siguientes 2 elementos atómicos flotantes:
1. **Diálogos Modales Emergentes**: (`ModalDialog`, `ConfirmModal`, `SignatureModal`, `ScannerModal`) que abren sobre un backdrop oscurecido (`backdrop-blur`).
2. **Formulario de Inicio de Sesión (`LoginCard`)**: En la pantalla de login previo a la autenticación, donde se utiliza una tarjeta de acceso centrada.

Una vez el usuario ingresa al sistema autenticado, **EL 100% DE LAS VISTAS ES HORIZONTAL DE BORDE A BORDE**.

---

## 4. Estructura Canónica de Contenedor Full-Width (CSS / JSX)

### En CSS Puro (Consumiendo `variables.css`):
```css
/* ==========================================================================
   CONTENEDOR MAESTRO DE VISTA — FULL WIDTH HORIZONTAL (100% ANCHO)
   ========================================================================== */
.page-wrapper-full {
  width: 100%;
  min-height: calc(100vh - var(--topheader-height, 60px));
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-sizing: border-box;
  /* PROHIBIDO max-width con mx-auto */
  max-width: 100% !important;
  margin: 0 !important;
}

/* Rejilla de KPIs a lo largo de la pantalla */
.kpi-grid-full {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

/* Barra de filtros horizontal */
.filter-topbar-full {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md, 8px);
  padding: 0.75rem 1rem;
}

/* Contenedor de tabla 100% horizontal */
.table-wrapper-full {
  width: 100%;
  overflow-x: auto;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md, 8px);
}
```

### En JSX / React:
```tsx
import React from 'react';

export const MasterLayoutPage: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="page-wrapper-full w-full">
      {/* Todo el contenido se expande a lo largo de la pantalla */}
      {children}
    </div>
  );
};
```

---

## 5. Verificación Automática en Pre-Commit y Auditoría
Cualquier archivo de vista (`.tsx`, `.jsx`, `.vue`, `.html`) que contenga:
- `<div className="... max-w-xl mx-auto ...">` en su contenedor raíz de pantalla.
- `<div className="min-h-screen flex items-center justify-center">` en una vista autenticada.
**Será calificado como violación de diseño corporativo en la auditoría** y deberá remediarse inmediatamente a ancho completo horizontal.
