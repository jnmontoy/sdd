# Especificación UI: Barra de Navegación Superior (Top Navbar)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

La **Top Navbar** es el componente de cabecera persistente en todas las vistas autenticadas de las aplicaciones de Jolifoods.

Provee identidad de marca, selector dinámico del tema **Modo Noche / Modo Día** (sincronizado con [`variables.css`](../variables.css)), badge de alertas y menú desplegable del perfil del colaborador con acción de cierre de sesión seguro.

---

> **REGLAS DE ORO DE CABECERA Y ESPACIO VERTICAL (UX/UI)**:
> 1. **Cero Sidebar por Defecto (Full-Width Layout)**: Las aplicaciones y prototipos no incluyen menú lateral izquierdo (Sidebar) a menos que el usuario lo solicite explícitamente. La Top Navbar ocupa el 100% del ancho de la pantalla de forma nativa.
> 2. **Título Directo de la Página en Lado Izquierdo (Cero Breadcrumbs de Navegación)**: 
>    - Para no desperdiciar espacio vertical en el cuerpo de la página con encabezados `<h1>` o banners, **el Título de la Página Actual se ubica obligatoriamente en el LADO IZQUIERDO del TopHeader**, contiguo al logotipo oficial de Jolifoods, separado por una barra sutil `/` y con un badge de contexto opcional.
>    - **Queda estrictamente prohibido usar cadenas de navegación tipo breadcrumb / migas de pan (`Jolifoods > Módulo > Pantalla`) a menos que el usuario lo solicite expresamente**.
>    - **Queda estrictamente prohibido usar textos en verde para títulos o rutas de navegación** (mala presentación visual; el verde es de uso exclusivo en badges de estado óptimo).
> 3. **Lado Derecho para Controles de Sesión**: El lado derecho se reserva exclusivamente para el conmutador de tema (Día/Noche), el centro de multi-notificaciones y el menú de perfil de usuario con confirmación de salida.

---

## 1. Anatomía Visual y Elementos

```
+-------------------------------------------------------------------------------------------------------------------------+
| [Logo Jolifoods]  /  [Título de Página / Módulo] [BADGE]       (Espaciador)          [☀️/🌙]  [🔔 (3)]  [ (JM) Joan M. v ] |
+-------------------------------------------------------------------------------------------------------------------------+
```

1. **Lado Izquierdo (`topheader-left`)**:
   - Logotipo corporativo Jolifoods (Isotipo SVG).
   - Divisor vertical sutil (`.topheader-brand-divider`).
   - **Caja de Título de Página (`topheader-title-box`)**:
     - Nombre del módulo o pantalla activa (`.topheader-page-title`).
     - Badge compacto de contexto o estado (`.topheader-page-badge`, ej. "ACTIVO", "IDEAM", "PRODUCCIÓN").
2. **Lado Derecho (`topheader-right`)**:
   - Conmutador de Tema Noche / Día (`theme-toggle`).
   - Campana de notificaciones con contador (`notifications-badge`).
   - Perfil de usuario con avatar y rol (`user-profile-badge`).

---

## 2. Código HTML / JSX Canónico

```html
<header class="top-header" role="banner">
  <!-- LADO IZQUIERDO: BRANDING + TÍTULO DE LA PÁGINA (Ahorro de espacio vertical) -->
  <div class="topheader-left">
    <div class="topheader-brand">
      <img src="./assets/Jolifoods.svg" alt="Jolifoods" class="topheader-logo" />
    </div>

    <div class="topheader-brand-divider">/</div>

    <div class="topheader-title-box">
      <h1 class="topheader-page-title" id="pageMainHeading">Monitoreo Agroclimático Colombia</h1>
      <span class="topheader-page-badge" id="pageMainBadge">RED IDEAM</span>
    </div>
  </div>

  <!-- LADO DERECHO: CONTROLES DE SESIÓN Y TEMA -->
  <div class="top-header-right">
    <!-- Conmutador Tema Día / Noche -->
    <button type="button" class="icon-btn-header" id="themeToggleBtn" aria-label="Cambiar tema">
      <i data-lucide="moon" id="themeIcon"></i>
    </button>

    <!-- Notificaciones -->
    <div class="icon-btn-header" aria-label="Notificaciones">
      <i data-lucide="bell"></i>
      <span class="notif-badge">3</span>
    </div>

    <!-- Perfil de Usuario con Menú Desplegable y Salida Segura (Ver user_profile_dropdown.md) -->
    <div class="user-profile-menu-container" id="userProfileContainer">
      <button type="button" class="user-profile-badge" id="userProfileBtn" onclick="toggleUserProfile(event)">
        <div class="user-avatar-circle">
          JM
          <span class="status-indicator-dot online"></span>
        </div>
        <span class="d-none d-sm-inline font-sm fw-medium">Joan Montoya</span>
        <i data-lucide="chevron-down" style="width: 13px; height: 13px;"></i>
      </button>

      <!-- Dropdown Flotante de Perfil -->
      <div class="profile-dropdown-menu" id="userProfileDropdown">
        <div class="profile-dropdown-header">
          <div class="dropdown-avatar-lg">JM</div>
          <div class="dropdown-user-info">
            <span class="dropdown-user-name">Joan Montoya</span>
            <span class="dropdown-user-email">joan.montoya@jolifoods.com</span>
            <span class="dropdown-user-role-badge">ADMINISTRADOR</span>
          </div>
        </div>
        <div class="dropdown-divider"></div>
        <div class="profile-dropdown-items">
          <button type="button" class="dropdown-item" onclick="alert('Navegar a Mi Perfil')">
            <i data-lucide="user" style="width: 15px; height: 15px;"></i>
            <span>Mi Perfil</span>
          </button>
        </div>
        <div class="dropdown-divider"></div>
        <div class="profile-dropdown-footer">
          <button type="button" class="dropdown-item logout" onclick="openLogoutModal()">
            <i data-lucide="log-out" style="width: 15px; height: 15px;"></i>
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</header>
```

---

## 3. Estilos CSS Canónicos (Gobernados por `variables.css`)

```css
.top-header {
  position: sticky;
  top: 0;
  z-index: 900;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--topbar-height, 60px);
  padding: 0 1.5rem;
  background: var(--glass-bg, rgba(26, 26, 46, 0.88));
  border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.09));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.top-header-right {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

/* Regla de Oro: Título de Página Integrado en TopHeader */
.topheader-page-title-box {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  background: var(--bg-hover, rgba(255, 255, 255, 0.05));
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-md, 8px);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.09));
}

.topheader-page-title {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-primary, #ffffff);
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.topheader-page-badge {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 7px;
  border-radius: var(--radius-pill, 9999px);
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
  white-space: nowrap;
}

.topheader-divider {
  width: 1px;
  height: 22px;
  background: var(--border-color, rgba(255, 255, 255, 0.09));
  margin: 0 0.15rem;
}
  gap: var(--space-4);
}

.joli-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.joli-navbar-logo {
  height: 30px;
  width: auto;
}

.joli-brand-divider {
  color: var(--color-text-muted);
  font-weight: 300;
}

.joli-project-title {
  font-size: var(--text-base);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  letter-spacing: -0.3px;
}

.joli-nav-icon-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.joli-nav-icon-btn:hover {
  background-color: var(--color-bg-card-hover);
  color: var(--color-primary);
}

.joli-badge-counter {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  font-size: 10px;
  font-weight: var(--weight-bold);
  color: #ffffff;
  background-color: var(--color-primary);
  border-radius: var(--radius-full);
}

/* THEME TOGGLE */
.joli-theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: 16px;
  transition: all var(--transition-fast);
}

[data-theme='light'] .joli-theme-icon-light { display: none; }
[data-theme='light'] .joli-theme-icon-dark { display: inline-block; }
:root:not([data-theme='light']) .joli-theme-icon-dark { display: none; }
:root:not([data-theme='light']) .joli-theme-icon-light { display: inline-block; }

/* USER MENU */
.joli-user-menu {
  position: relative;
}

.joli-user-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 4px 8px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.joli-user-trigger:hover {
  background-color: var(--color-bg-card-hover);
}

.joli-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, var(--color-primary), #059669);
  color: #ffffff;
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  border-radius: var(--radius-full);
}

.joli-user-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.joli-user-name {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  line-height: 1.2;
}

.joli-user-role {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.joli-dropdown-chevron {
  color: var(--color-text-muted);
}

.joli-dropdown-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  padding: var(--space-2) 0;
  display: none;
}

.joli-user-menu.open .joli-dropdown-panel {
  display: block;
}

.joli-dropdown-header {
  padding: var(--space-3) var(--space-4);
}

.joli-dropdown-user {
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.joli-dropdown-email {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.joli-dropdown-divider {
  height: 1px;
  background-color: var(--color-border);
  margin: var(--space-2) 0;
}

.joli-dropdown-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.joli-dropdown-item:hover {
  background-color: var(--color-bg-card-hover);
  color: var(--color-text-primary);
}

.joli-dropdown-item.text-danger {
  color: var(--color-danger);
}

.joli-dropdown-item.text-danger:hover {
  background-color: rgba(239, 68, 68, 0.1);
}
```
