# Componente: Alertas y Feedback de Login (`UI-COMP-LOGIN-FEEDBACK`)
## Ubicación SDD: `.sdd/components/login/feedback_alerts.md`

Este documento especifica los componentes visuales de alerta en línea y los avisos flotantes del login utilizando **CSS puro** gobernado por `variables.css`.

---

## 1. Banner de Alerta en Línea (`InlineAlert`)

### 1.1. Estructura HTML / JSX
```html
<div class="joli-login-alert joli-login-alert-error" role="alert">
  <svg class="joli-login-alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="10" stroke-width="2" />
    <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round" />
    <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round" />
  </svg>
  <div class="joli-login-alert-body">
    <strong class="joli-login-alert-title">Fallo de Autenticación</strong>
    <p class="joli-login-alert-desc">El número de documento o la contraseña ingresada son incorrectos.</p>
  </div>
</div>
```

### 1.2. Hoja de Estilos en CSS Puro
```css
.joli-login-alert {
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

.joli-login-alert-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.joli-login-alert-body {
  display: flex;
  flex-direction: column;
}

.joli-login-alert-title {
  font-weight: var(--font-weight-semibold);
  margin-bottom: 0.125rem;
}

.joli-login-alert-desc {
  margin: 0;
  opacity: 0.95;
}

/* Variante Error */
.joli-login-alert-error {
  background-color: var(--alert-error-bg);
  border-color: var(--alert-error-border);
  color: var(--alert-error-text);
}

.joli-login-alert-error .joli-login-alert-icon {
  color: var(--status-error);
}

/* Variante Advertencia (Rate Limit) */
.joli-login-alert-warning {
  background-color: var(--status-warning-bg);
  border-color: var(--status-warning);
  color: var(--text-primary);
}

.joli-login-alert-warning .joli-login-alert-icon {
  color: var(--status-warning);
}
```

---

## 2. Aviso de Sesión Expirada

El aviso de sesión vencida NO se define en este archivo: el componente canónico es [`SessionExpirationModal`](../modal/session_expiration_modal.md) (React, `role="alertdialog"`, foco atrapado, `data-testid="session-expiration-modal"`), que monta `AuthContext` al recibir el evento `session-expired`. Mantener una única implementación evita dos modales con textos y comportamientos distintos.

---

## 3. Notificaciones Flotantes en Login con Sonner (`ToastNotification`)

Para la retroalimentación no bloqueante durante el flujo de autenticación se usa **Sonner** encapsulado en [`../toast/toast_notification.md`](../toast/toast_notification.md). Los errores de credenciales DEBERÍAN mostrarse además en el banner en línea (§1), que queda junto al formulario y es anunciado por lectores de pantalla.

### 3.1. Montaje del Contenedor Toaster
Si la página de login se renderiza fuera del layout autenticado, monta allí `<CorporateToaster />`:

```tsx
import { CorporateToaster } from '../ui/ToastNotification';

export const LoginPage: React.FC = () => (
  <main className="joli-login-viewport">
    <CorporateToaster />
    <LoginForm />
  </main>
);
```

### 3.2. Matriz de Eventos y Toasts en Login
| Evento de Login | Método Sonner | Severidad | Duración | Mensaje / Título | Descripción de Ejemplo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Campos Incompletos** | `showToast.warning()` | Advertencia | 5000 ms | *"Campo requerido"* | *"Por favor ingresa tu número de documento."* |
| **Credenciales Inválidas (400/401)** | `showToast.error()` | Error | 6000 ms | *"Fallo de autenticación"* | *"El número de documento o la contraseña son incorrectos."* |
| **Rate Limit / Bloqueo (429)** | `showToast.warning()` | Advertencia | 7000 ms | *"Acceso temporalmente bloqueado"* | *"Demasiados intentos fallidos. Espera un momento antes de reintentar."* |
| **Error de Red / Servidor (5xx)** | `showToast.error()` | Error | 7000 ms | *"Error de conexión"* | *"No se pudo conectar con el servidor de autenticación."* |
| **Autenticación Exitosa** | `showToast.success()` | Éxito | 3500 ms | *"Inicio de sesión exitoso"* | *"Bienvenido, [Nombre de Usuario]."* |

### 3.3. Ejemplo de Implementación en el Manejador Submit
El mensaje de error es siempre genérico: NO DEBE mostrar `err.message` ni el detalle del servidor (podría revelar si un documento existe o detalles internos).

```tsx
import { isAxiosError } from 'axios';
import { useAuth } from '../../context/AuthContext';
import { showToast } from '../ui/ToastNotification';

const { login } = useAuth();

const handleSubmit = async (numeroDocumento: string, password: string) => {
  if (!numeroDocumento.trim()) {
    showToast.warning('Campo requerido', { description: 'Por favor ingresa tu número de documento.' });
    return;
  }

  setIsLoading(true);
  try {
    const user = await login({ numero_documento: numeroDocumento.trim(), password });
    showToast.success('Inicio de sesión exitoso', { description: `Bienvenido, ${user.nombre}.` });
  } catch (err: unknown) {
    const status = isAxiosError(err) ? err.response?.status : undefined;
    if (status === 429) {
      showToast.warning('Acceso temporalmente bloqueado', {
        description: 'Demasiados intentos. Espera un momento antes de reintentar.',
      });
    } else if (status === 400 || status === 401) {
      showToast.error('Fallo de autenticación', {
        description: 'El número de documento o la contraseña son incorrectos.',
      });
    } else {
      showToast.error('Error de conexión', {
        description: 'No se pudo conectar con el servidor de autenticación.',
      });
    }
  } finally {
    setIsLoading(false);
  }
};
```
