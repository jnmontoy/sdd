# Especificación UI: Barra Lateral de Navegación (Sidebar Colapsable)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

> **DIRECTRIZ DE ARQUITECTURA SDD — COMPONENTE OPTATIVO (NO POR DEFECTO)**:
> El Sidebar de navegación **NO se incluye por defecto** en prototipos ni aplicaciones de Jolifoods.
> Por defecto, la interfaz utiliza un **Layout Full-Width (ancho completo)** gobernado por la Top Navbar.
> **El Sidebar ÚNICAMENTE se incluye si el usuario solicita explícitamente navegación lateral multifuncional**.

La **Sidebar** proporciona la estructura de navegación principal de la aplicación cuando se requiere acceso a múltiples módulos, soportando **control de acceso basado en roles (RBAC)** y estados colapsado/expandido con micro-animaciones fluidas en CSS puro.

---

## 1. Estados e Interacción

- **Estado Expandido (Desktop, 260px)**: Muestra ícono, etiqueta de texto, submenús y badges informativos.
- **Estado Colapsado (Desktop Mini, 76px)**: Oculta etiquetas y expande tooltips flotantes al pasar el cursor sobre los íconos.
- **Estado Móvil (Drawer deslizable, 0 a 280px)**: Se superpone a la pantalla con un fondo oscurecido (`backdrop overlay`).

---

## 2. Código HTML / JSX Canónico

```html
<aside class="joli-sidebar" id="mainSidebar" aria-label="Navegación principal">
  <!-- CABECERA SIDEBAR (SECCIÓN SUPERIOR) -->
  <div class="joli-sidebar-header">
    <span class="joli-sidebar-section-title">MÓDULOS DEL SISTEMA</span>
  </div>

  <!-- NAVEGACIÓN PRINCIPAL -->
  <nav class="joli-sidebar-nav">
    <ul class="joli-nav-list">
      
      <!-- ITEM: DASHBOARD -->
      <li class="joli-nav-item active">
        <a href="#dashboard" class="joli-nav-link">
          <svg class="joli-nav-icon" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" fill="none">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
          <span class="joli-nav-label">Tablero Principal</span>
        </a>
      </li>

      <!-- ITEM: OPERACIONES (ROL OPERADOR / ADMIN) -->
      <li class="joli-nav-item">
        <a href="#operaciones" class="joli-nav-link">
          <svg class="joli-nav-icon" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" fill="none">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
          <span class="joli-nav-label">Operaciones</span>
          <span class="joli-nav-badge">En vivo</span>
        </a>
      </li>

      <!-- ITEM: REPORTES & EXCEL (ROL ADMIN / AUDITOR) -->
      <li class="joli-nav-item">
        <a href="#reportes" class="joli-nav-link">
          <svg class="joli-nav-icon" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" fill="none">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          <span class="joli-nav-label">Reportes & Excel</span>
        </a>
      </li>

      <!-- ITEM: AUDITORÍA & ACCESOS (ROL ADMIN EXCLUSIVO) -->
      <li class="joli-nav-item">
        <a href="#auditoria" class="joli-nav-link">
          <svg class="joli-nav-icon" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" fill="none">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          <span class="joli-nav-label">Auditoría de Accesos</span>
        </a>
      </li>

    </ul>
  </nav>

  <!-- PIE DE LA SIDEBAR (ESTADO DEL SISTEMA) -->
  <div class="joli-sidebar-footer">
    <div class="joli-system-status">
      <span class="joli-status-dot online"></span>
      <span class="joli-status-text">Backend Conectado</span>
    </div>
  </div>
</aside>
```

---

## 3. Estilos CSS Canónicos (Gobernados por `variables.css`)

```css
.joli-sidebar {
  position: fixed;
  top: 64px; /* Debajo de la navbar */
  left: 0;
  bottom: 0;
  width: 260px;
  background-color: var(--color-bg-card);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: 900;
  transition: width var(--transition-normal), transform var(--transition-normal);
  overflow-x: hidden;
}

/* ESTADO COLAPSADO */
.joli-sidebar.collapsed {
  width: 76px;
}

.joli-sidebar.collapsed .joli-nav-label,
.joli-sidebar.collapsed .joli-nav-badge,
.joli-sidebar.collapsed .joli-sidebar-section-title,
.joli-sidebar.collapsed .joli-status-text {
  display: none;
}

.joli-sidebar.collapsed .joli-nav-link {
  justify-content: center;
  padding: var(--space-3) 0;
}

.joli-sidebar-header {
  padding: var(--space-4) var(--space-5) var(--space-2) var(--space-5);
}

.joli-sidebar-section-title {
  font-size: 11px;
  font-weight: var(--weight-bold);
  color: var(--color-text-muted);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.joli-sidebar-nav {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  overflow-y: auto;
}

.joli-nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.joli-nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  transition: all var(--transition-fast);
}

.joli-nav-link:hover {
  background-color: var(--color-bg-card-hover);
  color: var(--color-text-primary);
}

.joli-nav-item.active .joli-nav-link {
  background: rgba(16, 185, 129, 0.12);
  color: var(--color-primary);
  font-weight: var(--weight-semibold);
  border-left: 3px solid var(--color-primary);
}

.joli-nav-icon {
  flex-shrink: 0;
}

.joli-nav-badge {
  margin-left: auto;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: var(--weight-bold);
  color: #10b981;
  background-color: rgba(16, 185, 129, 0.15);
  border-radius: var(--radius-full);
}

/* PIE DE SIDEBAR */
.joli-sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid var(--color-border);
}

.joli-system-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.joli-status-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.joli-status-dot.online {
  background-color: var(--color-primary);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
}

.joli-status-text {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
```
