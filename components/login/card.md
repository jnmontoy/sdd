# Componente: Cards y Contenedores de Login (`UI-COMP-LOGIN-CARD`)
## Ubicación SDD: `.sdd/components/login/card.md`

Este documento detalla las estructuras de contenedor autorizadas para la página de login utilizando **CSS puro**, implementando efectos de vidrio esmerilado (*Frosted Glass*) sin depender de librerías externas.

---

## 1. Estructura Canónica: Centered Glass Card

Contenedor flotante centralizado en la pantalla con efecto `backdrop-filter: blur()`, acento superior esmeralda y sombras volumétricas.

### 1.1. Estructura HTML / JSX
```html
<main class="login-viewport">
  <!-- Halos de luz de fondo generados con gradientes radiales -->
  <div class="login-orb login-orb-top" aria-hidden="true"></div>
  <div class="login-orb login-orb-bottom" aria-hidden="true"></div>

  <!-- Tarjeta Glassmorphic Centrada -->
  <section class="login-card" aria-label="Formulario de inicio de sesión">
    <div class="login-card-inner">
      <!-- Slot de contenido (Logo, Formulario, Botones) -->
    </div>
  </section>
</main>
```

### 1.2. Hoja de Estilos en CSS Puro (`card_centered.css`)
```css
/* ==========================================================================
   ESTRUCTURA: CENTERED GLASS CARD (CSS PURO)
   ========================================================================== */

.login-viewport {
  position: relative;
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0b0f19; /* Slate 950 */
  padding: 1.5rem;
  box-sizing: border-box;
  overflow: hidden;
}

/* Halos decorativos en segundo plano */
.login-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  opacity: 0.35;
}

.login-orb-top {
  width: 420px;
  height: 420px;
  background: radial-gradient(circle, #10b981 0%, transparent 70%);
  top: -10%;
  right: -5%;
}

.login-orb-bottom {
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, #065f46 0%, transparent 70%);
  bottom: -10%;
  left: -5%;
}

/* Contenedor Glassmorphic */
.login-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 440px;
  background-color: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-top: 1px solid rgba(16, 185, 129, 0.35); /* Acento esmeralda */
  border-radius: 1.5rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75),
              0 0 20px -5px rgba(16, 185, 129, 0.15);
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  box-sizing: border-box;
}

.login-card:hover {
  border-top-color: rgba(52, 211, 153, 0.55);
  box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.85),
              0 0 30px -5px rgba(16, 185, 129, 0.25);
}

.login-card-inner {
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

/* Adaptabilidad para pantallas móviles pequeñas */
@media (max-width: 480px) {
  .login-viewport {
    padding: 1rem;
  }
  
  .login-card-inner {
    padding: 2rem 1.25rem;
  }
}
```

---

## 2. Estructura Alternativa: Split-Screen Hero Card

Utilizada en pantallas panorámicas dividiendo la interfaz en un panel artístico institucional (50%) y el panel de autenticación (50%).

### 2.1. Estructura HTML / JSX
```html
<main class="login-split-root">
  <!-- Panel de Marca (Solo visible en pantallas de más de 1024px) -->
  <aside class="login-split-hero">
    <div class="login-split-hero-overlay"></div>
    <div class="login-split-hero-content">
      <span class="login-split-tag">Ecosistema Digital</span>
      <h2 class="login-split-title">Innovación y Seguridad Corporativa</h2>
      <p class="login-split-desc">Plataforma centralizada de autenticación y servicios institucionales.</p>
    </div>
  </aside>

  <!-- Panel de Formulario -->
  <section class="login-split-form-panel">
    <div class="login-split-form-container">
      <!-- Slot de formulario -->
    </div>
  </section>
</main>
```

### 2.2. Hoja de Estilos en CSS Puro (`card_split.css`)
```css
/* ==========================================================================
   ESTRUCTURA: SPLIT-SCREEN HERO (CSS PURO)
   ========================================================================== */

.login-split-root {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background-color: #0b0f19;
  box-sizing: border-box;
}

.login-split-hero {
  display: none;
  flex: 1;
  position: relative;
  background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
  align-items: flex-end;
  padding: 4rem;
  overflow: hidden;
  box-sizing: border-box;
}

@media (min-width: 1024px) {
  .login-split-hero {
    display: flex;
  }
}

.login-split-hero-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 30%, rgba(16, 185, 129, 0.35), transparent 60%);
  pointer-events: none;
}

.login-split-hero-content {
  position: relative;
  z-index: 2;
  max-width: 480px;
}

.login-split-tag {
  display: inline-block;
  padding: 0.35rem 0.85rem;
  background-color: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 9999px;
  color: #34d399;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 1.25rem;
}

.login-split-title {
  color: #f8fafc;
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 1rem 0;
}

.login-split-desc {
  color: #94a3b8;
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
}

.login-split-form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  box-sizing: border-box;
}

.login-split-form-container {
  width: 100%;
  max-width: 420px;
}
```
