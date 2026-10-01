# Componente: Alertas y Feedback de Login (`UI-COMP-LOGIN-FEEDBACK`)
## Ubicación SDD: `.sdd/components/login/feedback_alerts.md`

Este documento especifica los componentes visuales de alerta en línea y el modal de sesión expirada utilizando **CSS puro** gobernado por `variables.css`.

---

## 1. Banner de Alerta en Línea (`InlineAlert`)

### 1.1. Estructura HTML / JSX
```html
<div class="login-alert login-alert-error" role="alert" aria-live="polite">
  <svg class="login-alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="10" stroke-width="2" />
    <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round" />
    <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round" />
  </svg>
  <div class="login-alert-body">
    <strong class="login-alert-title">Fallo de Autenticación</strong>
    <p class="login-alert-desc">El número de documento o la contraseña ingresada son incorrectos.</p>
  </div>
</div>
```

### 1.2. Hoja de Estilos en CSS Puro
```css
.login-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: var(--radius-md);
  font-family: var(--font-family);
  font-size: var(--font-size-xs);
  line-height: var(--line-height-normal);
  margin-bottom: 1.25rem;
  border: 1px solid transparent;
  box-sizing: border-box;
}

.login-alert-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.login-alert-body {
  display: flex;
  flex-direction: column;
}

.login-alert-title {
  font-weight: var(--font-weight-semibold);
  margin-bottom: 0.125rem;
}

.login-alert-desc {
  margin: 0;
  opacity: 0.95;
}

/* Variante Error */
.login-alert-error {
  background-color: var(--alert-error-bg);
  border-color: var(--alert-error-border);
  color: var(--alert-error-text);
}

.login-alert-error .login-alert-icon {
  color: var(--status-error);
}

/* Variante Advertencia (Rate Limit) */
.login-alert-warning {
  background-color: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.3);
  color: #fde68a;
}

.login-alert-warning .login-alert-icon {
  color: var(--status-warning);
}
```

---

## 2. Modal de Sesión Expirada (`SessionExpiredModal`)

### 2.1. Estructura HTML / JSX
```html
<div class="login-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-exp-title">
  <div class="login-modal-box">
    <div class="login-modal-badge">
      <svg class="login-modal-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke-width="2" />
        <polyline points="12 6 12 12 16 14" stroke-width="2" stroke-linecap="round" />
      </svg>
    </div>
    
    <h3 id="modal-exp-title" class="login-modal-title">Tu sesión ha finalizado</h3>
    <p class="login-modal-desc">
      Por políticas de seguridad corporativa, tu sesión caducó por inactividad. Inicia sesión nuevamente para continuar tu trabajo.
    </p>

    <div class="login-modal-actions">
      <button type="button" class="login-btn-primary">
        Volver a Iniciar Sesión
      </button>
    </div>
  </div>
</div>
```

### 2.2. Hoja de Estilos en CSS Puro
```css
.login-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  box-sizing: border-box;
}

.login-modal-box {
  width: 100%;
  max-width: 400px;
  background-color: var(--bg-card);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85);
  padding: 2rem;
  text-align: center;
  box-sizing: border-box;
  animation: modalEnter 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-modal-badge {
  width: 56px;
  height: 56px;
  margin: 0 auto 1.25rem auto;
  border-radius: var(--radius-full);
  background-color: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--status-warning);
}

.login-modal-icon {
  width: 28px;
  height: 28px;
}

.login-modal-title {
  margin: 0 0 0.5rem 0;
  font-family: var(--font-family);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.login-modal-desc {
  margin: 0 0 1.5rem 0;
  font-family: var(--font-family);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: var(--line-height-normal);
}

.login-modal-actions {
  display: flex;
  justify-content: center;
}

@keyframes modalEnter {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
```

---

## 3. Notificaciones Flotantes en Login con Sonner (`ToastNotification`)

Para la retroalimentación reactiva y no bloqueante durante el flujo de autenticación, el sistema utiliza el complemento **Sonner** encapsulado en [`../toast/toast_notification.md`](../toast/toast_notification.md).

### 3.1. Montaje del Contenedor Toaster
En la vista o layout del Login (`LoginPage.tsx`), se debe montar el contenedor corporativo `<CorporateToaster />`:

```tsx
import { CorporateToaster } from '../ui/ToastNotification';

export const LoginPage: React.FC = () => {
  return (
    <main className="gy-login-viewport">
      <CorporateToaster />
      {/* Contenido del Login */}
    </main>
  );
};
```

### 3.2. Matriz de Eventos y Toasts en Login
| Evento de Login | Método Sonner | Severidad | Duración | Mensaje / Título | Descripción de Ejemplo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Campos Incompletos** | `showToast.warning()` | Advertencia | 5000 ms | *"Campo requerido"* | *"Por favor ingresa tu número de documento."* |
| **Credenciales Inválidas** | `showToast.error()` | Error | 6000 ms | *"Fallo de autenticación"* | *"El número de documento o la contraseña ingresada son incorrectos."* |
| **Rate Limit / Bloqueo (429)** | `showToast.warning()` | Advertencia | 7000 ms | *"Acceso temporalmente bloqueado"* | *"Demasiados intentos fallidos. Por seguridad espera 60 segundos."* |
| **Error de Red / Servidor (500)** | `showToast.error()` | Error | 7000 ms | *"Error de conexión"* | *"No se pudo conectar con el servidor de autenticación."* |
| **Autenticación Exitosa** | `showToast.success()` | Éxito | 3500 ms | *"¡Inicio de sesión exitoso!"* | *"Bienvenido al sistema, [Nombre de Usuario]."* |
| **Cambio de Tema (Dark/Light)** | `showToast.info()` | Informativo | 3500 ms | *"Tema actualizado"* | *"Modo oscuro activado / Modo claro activado"* |

### 3.3. Ejemplo de Implementación en el Manejador Submit
```tsx
import { showToast } from '../ui/ToastNotification';

const handleSubmit = async (data: LoginFormData) => {
  if (!data.documento.trim()) {
    showToast.warning('Campo requerido', {
      description: 'Por favor ingresa tu número de documento.',
    });
    return;
  }

  try {
    setIsLoading(true);
    const res = await api.login(data);

    if (res.success && res.user) {
      showToast.success('¡Inicio de sesión exitoso!', {
        description: `Bienvenido, ${res.user.nombre}.`,
      });
      onLoginSuccess(res.user);
    } else {
      showToast.error('Fallo de autenticación', {
        description: res.message || 'Credenciales inválidas.',
      });
    }
  } catch (err: any) {
    if (err.response?.status === 429) {
      showToast.warning('Acceso temporalmente bloqueado', {
        description: 'Demasiados intentos. Espera un momento antes de reintentar.',
      });
    } else {
      showToast.error('Error de acceso', {
        description: err.message || 'No fue posible validar tus credenciales.',
      });
    }
  } finally {
    setIsLoading(false);
  }
};
```

