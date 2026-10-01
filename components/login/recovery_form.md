# Componente: Formularios de Restablecimiento de Contraseña (`UI-COMP-LOGIN-RECOVERY`)
## Ubicación SDD: `.sdd/components/login/recovery_form.md`

Este documento especifica la interfaz para el flujo de recuperación de credenciales utilizando **CSS puro** gobernado por `variables.css` con soporte nativo de **Modo Noche y Modo Día**.

Comprende dos pantallas:
1. **Formulario de Solicitud de Recuperación** (Ingreso de cédula o correo).
2. **Formulario de Definición de Nueva Contraseña** (Clave nueva y confirmación).

---

## 1. Pantalla 1: Formulario de Solicitud de Enlace (`RecoveryRequestForm`)

### 1.1. Estructura HTML / JSX
```html
<section class="login-card" aria-labelledby="recovery-title">
  <div class="login-card-inner">
    
    <!-- Encabezado con Ícono de Llave / Candado -->
    <header class="login-logo-wrapper">
      <div class="login-recovery-icon-badge">
        <svg class="login-recovery-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <rect x="3" y="11" width="18" height="11" rx="2" stroke-width="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke-width="2" stroke-linecap="round" />
        </svg>
      </div>
      <h1 id="recovery-title" class="login-logo-title">Recuperar Acceso</h1>
      <p class="login-logo-subtitle">Ingresa tu número de documento o correo para recibir un enlace seguro</p>
    </header>

    <form id="form-recovery" class="login-form-body">
      <!-- Input Identificador -->
      <div class="login-input-group">
        <label for="recovery-id" class="login-input-label">Cédula o Correo Corporativo</label>
        <div class="login-input-box">
          <span class="login-input-prefix-icon" aria-hidden="true">
            <svg class="login-input-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke-width="2" />
              <polyline points="22,6 12,13 2,6" stroke-width="2" />
            </svg>
          </span>
          <input 
            id="recovery-id" 
            name="identificador" 
            type="text" 
            placeholder="Ej. 1037645123 o usuario@jolifoods.com" 
            class="login-input-control" 
            required 
          />
        </div>
      </div>

      <!-- Botón de Envío -->
      <button type="submit" class="login-btn-primary">
        <span>Enviar Enlace de Recuperación</span>
      </button>

      <!-- Enlace para Volver al Login -->
      <div class="login-recovery-back-bar">
        <a href="#login" class="login-recovery-back-link">
          <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <line x1="19" y1="12" x2="5" y2="12" stroke-width="2" stroke-linecap="round" />
            <polyline points="12 19 5 12 12 5" stroke-width="2" stroke-linecap="round" />
          </svg>
          Volver a Iniciar Sesión
        </a>
      </div>
    </form>

  </div>
</section>
```

---

## 2. Pantalla 2: Formulario de Nueva Contraseña (`NewPasswordForm`)

### 2.1. Estructura HTML / JSX
```html
<section class="login-card" aria-labelledby="newpass-title">
  <div class="login-card-inner">
    
    <header class="login-logo-wrapper">
      <div class="login-recovery-icon-badge success">
        <svg class="login-recovery-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke-width="2" />
          <path d="M9 12l2 2 4-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <h1 id="newpass-title" class="login-logo-title">Nueva Contraseña</h1>
      <p class="login-logo-subtitle">Define una contraseña segura para tu cuenta</p>
    </header>

    <form id="form-new-password" class="login-form-body">
      <!-- Nueva Contraseña -->
      <div class="login-input-group">
        <label for="new-pass" class="login-input-label">Nueva Contraseña</label>
        <div class="login-input-box">
          <input 
            id="new-pass" 
            name="new_password" 
            type="password" 
            placeholder="Mínimo 8 caracteres" 
            class="login-input-control" 
            required 
          />
        </div>
      </div>

      <!-- Confirmar Contraseña -->
      <div class="login-input-group">
        <label for="confirm-pass" class="login-input-label">Confirmar Contraseña</label>
        <div class="login-input-box">
          <input 
            id="confirm-pass" 
            name="confirm_password" 
            type="password" 
            placeholder="Repite la contraseña" 
            class="login-input-control" 
            required 
          />
        </div>
      </div>

      <!-- Requisitos de Seguridad Visuales -->
      <ul class="login-password-rules">
        <li class="rule-item">Mínimo 8 caracteres</li>
        <li class="rule-item">Al menos un número y una mayúscula</li>
      </ul>

      <!-- Botón de Confirmación -->
      <button type="submit" class="login-btn-primary">
        <span>Guardar y Entrar</span>
      </button>
    </form>

  </div>
</section>
```

---

## 3. Hoja de Estilos en CSS Puro (`recovery.css`)

```css
/* ==========================================================================
   COMPONENTE: FORMULARIO DE RESTABLECIMIENTO (CSS PURO)
   Integrado con variables.css para Modo Noche y Modo Día
   ========================================================================== */

.login-recovery-icon-badge {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--radius-xl);
  color: var(--brand-primary);
  margin-bottom: 1rem;
  box-shadow: 0 0 20px var(--brand-glow);
}

.login-recovery-icon-badge.success {
  color: #34d399;
  background-color: rgba(52, 211, 153, 0.15);
  border-color: rgba(52, 211, 153, 0.35);
}

.login-recovery-icon {
  width: 28px;
  height: 28px;
}

.login-recovery-back-bar {
  margin-top: 1.5rem;
  text-align: center;
}

.login-recovery-back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-family: var(--font-family);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  transition: color var(--transition-fast);
}

.login-recovery-back-link:hover {
  color: var(--brand-accent);
}

/* Reglas de Complejidad de Contraseña */
.login-password-rules {
  margin: 0.25rem 0 1.25rem 0;
  padding-left: 1.25rem;
  font-family: var(--font-family);
  font-size: var(--font-size-2xs);
  color: var(--text-muted);
  line-height: var(--line-height-normal);
}

.login-password-rules li {
  margin-bottom: 0.25rem;
}
```
