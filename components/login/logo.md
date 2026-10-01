# Componente: Logo e Identidad Visual Jolifoods (`UI-COMP-LOGIN-LOGO`)
## Ubicación SDD: `.sdd/components/login/logo.md`

Este documento especifica la integración oficial de la marca e identidad gráfica corporativa de **Jolifoods**, así como los activos visuales y la regla obligatoria de parametrización del nombre del proyecto en títulos y navegadores.

---

## 1. Regla Mandatoria para la IA: Preguntar el Nombre del Proyecto

> **REGLA OBLIGATORIA DE GENERACIÓN (SDD)**:
> Cuando un desarrollador o agente de Inteligencia Artificial proceda a estructurar un nuevo proyecto a partir de este `.sdd`, **DEBE PREGUNTAR OBLIGATORIAMENTE AL USUARIO EL NOMBRE DEL PROYECTO** (ejemplo: *"¿Cuál es el nombre del proyecto o módulo que deseas crear? (ej. Tiendita, Porterías, Control Operativo, etc.)"*).

### Con el nombre provisto por el usuario, la IA debe generar:
1. **El `<title>` del documento HTML (`index.html`)**:
   ```html
   <title>[Nombre del Proyecto] | Jolifoods</title>
   ```
2. **El Favicon del navegador**:
   ```html
   <link rel="icon" type="image/svg+xml" href="./assets/Jolifoods.svg" />
   <link rel="alternate icon" type="image/png" href="./assets/logoJoli.png" />
   ```
3. **El encabezado visual del formulario de Login**:
   - Título H1: `[Nombre del Proyecto]`
   - Subtítulo: `Jolifoods • Acceso Seguro Corporativo`

---

## 2. Activos Oficiales de Marca en el SDD (`.sdd/assets/`)

Los archivos vectoriales y rasterizados oficiales de Jolifoods se encuentran centralizados en:

```
.sdd/
└── assets/                                 # Activos globales de marca Jolifoods
    ├── Jolifoods.svg                       # Isotipo optimizado para UI y Favicon (2.5 KB)
    ├── Joli.svg                            # Isotipo oficial de alta resolución (102 KB)
    ├── logoJoli.png                        # Logo rasterizado transparente (2.4 KB)
    └── Joli.png                            # Isotipo en alta definición PNG (178 KB)
```

---

## 3. Estructura HTML / JSX del Logo en el Login

```html
<header class="login-logo-wrapper">
  <!-- Contenedor del Logo con Halo Luminoso -->
  <div class="login-logo-badge">
    <img 
      src="./assets/Jolifoods.svg" 
      alt="Jolifoods Logo" 
      class="login-logo-img"
      onerror="this.onerror=null; this.src='./assets/logoJoli.png';"
    />
  </div>

  <!-- Grupo Tipográfico Parametrizable -->
  <div class="login-logo-text-group">
    <!-- El nombre del proyecto se inyecta aquí -->
    <h1 class="login-logo-title">[Nombre del Proyecto]</h1>
    <p class="login-logo-subtitle">Jolifoods • Acceso Seguro</p>
  </div>
</header>
```

---

## 4. Hoja de Estilos en CSS Puro (`logo.css`)

```css
/* ==========================================================================
   COMPONENTE: LOGO JOLIFOODS (CSS PURO)
   ========================================================================== */

.login-logo-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin-bottom: 2rem;
  user-select: none;
}

/* Insignia esmeralda translúcida con halo de luz */
.login-logo-badge {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--radius-xl, 1.25rem);
  margin-bottom: 1rem;
  box-shadow: 0 0 25px rgba(16, 185, 129, 0.35);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
  overflow: hidden;
}

.login-logo-badge:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 0 35px rgba(16, 185, 129, 0.55);
}

.login-logo-img {
  width: 44px;
  height: 44px;
  object-fit: contain;
  display: block;
}

/* Grupo de texto */
.login-logo-text-group {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-logo-title {
  margin: 0;
  font-family: var(--font-family, system-ui, sans-serif);
  font-size: var(--font-size-2xl, 1.75rem);
  font-weight: var(--font-weight-extrabold, 800);
  letter-spacing: -0.025em;
  color: var(--text-primary, #f8fafc);
  line-height: var(--line-height-tight, 1.2);
}

.login-logo-subtitle {
  margin: 0.375rem 0 0 0;
  font-family: var(--font-family, system-ui, sans-serif);
  font-size: var(--font-size-xs, 0.8125rem);
  font-weight: var(--font-weight-medium, 500);
  color: var(--text-secondary, #94a3b8);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
```

---

## 4. Provisión de Assets en Prototipos Autónomos No-Code (`mock/`)

Cuando se genera un prototipo modular dentro de `mock/<nombre_modulo>/`, los activos de marca de `.sdd/assets/` deben replicarse en la subcarpeta local `mock/<nombre_modulo>/assets/`:

```text
mock/<nombre_modulo>/
├── [modulo].html
├── [modulo].css
├── [modulo].js
├── datos_[modulo].md
└── assets/
    ├── Jolifoods.svg         <- Usado en TopHeader y Favicon
    ├── Joli.svg              <- Isotipo alternativo de alta resolución
    └── logoJoli.png          <- Imagen de respaldo ante error de carga
```

De esta manera, el enlace `<img src="./assets/Jolifoods.svg" onerror="this.onerror=null; this.src='./assets/logoJoli.png';">` funciona de forma 100% portable y offline en cualquier computadora o navegador sin requerir servidores locales.

