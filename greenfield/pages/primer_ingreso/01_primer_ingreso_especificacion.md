# Especificación de Página: Cambio Obligatorio de Contraseña (Primer Ingreso)
## Joli Foods — Flujo de Activación de Credenciales

Flujo que se activa cuando un usuario recién creado, o con contraseña temporal, inicia sesión con `debe_cambiar_clave = true` ([modelo `Usuario`](../../../model/login/spec_model_usuario.md)). Hasta que defina una contraseña propia no puede usar ninguna otra vista.

---

## 1. Requisitos

1. **Bloqueo en el servidor (DEBE):** mientras `debe_cambiar_clave = true`, un middleware o permiso de DRF DEBE responder 403 `PASSWORD_CHANGE_REQUIRED` a toda ruta autenticada excepto `/api/v1/auth/change-password/`, `/api/v1/auth/me/`, `/api/v1/auth/refresh/` y `/api/v1/auth/logout/`. **Por qué:** la redirección del frontend sola se puede saltar llamando la API directamente.
2. **Redirección en el cliente:** si el login devuelve `user.debe_cambiar_clave = true`, el frontend navega a `/primer-ingreso` y `ProtectedRoute` impide salir de allí.
3. **Política de contraseñas:** la decide el backend con `AUTH_PASSWORD_VALIDATORS` (longitud mínima 10, no común, no parecida a los datos del usuario, no solo números). El medidor visual es una ayuda, no la regla.
4. **Distinta de la temporal:** el backend rechaza una nueva contraseña igual a la actual (`PASSWORD_REUSED`).
5. **Al terminar:** el backend pone `debe_cambiar_clave = false`, revoca otras sesiones, rota el refresh y devuelve un access nuevo; el cliente lo guarda en memoria y navega al tablero.

### Contrato
Se reutiliza `POST /api/v1/auth/change-password/` (`ENDPOINTS.AUTH.CHANGE_PASSWORD`) definido en [`../profile/01_perfil_usuario_especificacion.md`](../profile/01_perfil_usuario_especificacion.md) §2.1, con `password_actual` = contraseña temporal. No existe un endpoint aparte.

### Diseño
La tarjeta se centra en el viewport, igual que la tarjeta de login (excepción permitida a la regla de ancho completo: es un paso previo a la aplicación, no una vista de trabajo).

---

## 2. Implementación (`FirstTimePasswordPage.tsx`)

```tsx
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { isAxiosError } from 'axios';
import { ShieldCheck, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiClient, setAccessToken } from '../services/apiClient';
import { ENDPOINTS } from '../services/endpoints';
import { showToast } from '../components/ToastNotification';
import './first_time_password.css';

const schema = z
  .object({
    password_actual: z.string().min(1, 'Ingresa la contraseña temporal.'),
    nueva_password: z.string().min(10, 'Mínimo 10 caracteres.').max(128),
    confirmar: z.string(),
  })
  .refine((v) => v.nueva_password === v.confirmar, { path: ['confirmar'], message: 'Las contraseñas no coinciden.' });
type FormData = z.infer<typeof schema>;

const NIVELES = [
  { label: 'Muy débil', className: 'is-weak' },
  { label: 'Débil', className: 'is-weak' },
  { label: 'Media', className: 'is-medium' },
  { label: 'Buena', className: 'is-good' },
  { label: 'Fuerte', className: 'is-strong' },
] as const;

/** Estimación orientativa: prioriza longitud; la regla real la aplica el backend. */
function puntuar(clave: string): number {
  let score = 0;
  if (clave.length >= 10) score += 1;
  if (clave.length >= 14) score += 1;
  if (/[a-z]/.test(clave) && /[A-Z]/.test(clave)) score += 1;
  if (/[0-9]/.test(clave) && /[^A-Za-z0-9]/.test(clave)) score += 1;
  return score;
}

export function FirstTimePasswordPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [verClave, setVerClave] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { register, handleSubmit, control, formState: { errors, isSubmitting } } =
    useForm<FormData>({ resolver: zodResolver(schema) });
  const nueva = useWatch({ control, name: 'nueva_password' }) ?? '';
  const score = useMemo(() => puntuar(nueva), [nueva]);
  const nivel = NIVELES[score];

  const onSubmit = handleSubmit(async ({ password_actual, nueva_password }) => {
    setErrorMsg(null);
    try {
      const { data } = await apiClient.post<{ access: string }>(ENDPOINTS.AUTH.CHANGE_PASSWORD, { password_actual, nueva_password });
      setAccessToken(data.access);
      showToast.success('Contraseña definida', { description: 'Tu cuenta quedó activada.' });
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      const body = isAxiosError<{ error_code?: string; message?: string }>(err) ? err.response?.data : undefined;
      setErrorMsg(
        body?.error_code === 'INVALID_CURRENT_PASSWORD' ? 'La contraseña temporal no es correcta.'
        : body?.error_code === 'PASSWORD_REUSED' ? 'La nueva contraseña debe ser distinta de la temporal.'
        : body?.message ?? 'No fue posible cambiar la contraseña. Intenta de nuevo.'
      );
    }
  });

  return (
    <main className="joli-first-time-viewport">
      <section className="joli-first-time-card" aria-labelledby="first-time-title">
        <span className="joli-first-time-icon" aria-hidden="true"><ShieldCheck size={40} /></span>
        <h1 id="first-time-title" className="joli-first-time-title">Activación de cuenta</h1>
        <p className="joli-first-time-subtitle">
          {user?.nombre ? `${user.nombre}, por` : 'Por'} seguridad debes definir una contraseña personal antes de continuar.
        </p>

        {errorMsg && (
          <div className="alert alert-danger d-flex align-items-center gap-2 small" role="alert">
            <AlertCircle size={16} aria-hidden="true" /><span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={onSubmit} className="w-100 text-start" noValidate>
          <div className="mb-3">
            <label htmlFor="ft-actual" className="form-label small fw-semibold">Contraseña temporal</label>
            <input id="ft-actual" type="password" autoComplete="current-password"
                   className={`form-control input-control ${errors.password_actual ? 'is-invalid' : ''}`}
                   aria-invalid={Boolean(errors.password_actual)} {...register('password_actual')} />
            {errors.password_actual && <div className="invalid-feedback">{errors.password_actual.message}</div>}
          </div>

          <div className="mb-3">
            <label htmlFor="ft-nueva" className="form-label small fw-semibold">Nueva contraseña</label>
            <div className="input-group">
              <input id="ft-nueva" type={verClave ? 'text' : 'password'} autoComplete="new-password"
                     className={`form-control input-control ${errors.nueva_password ? 'is-invalid' : ''}`}
                     aria-invalid={Boolean(errors.nueva_password)} aria-describedby="ft-fuerza"
                     {...register('nueva_password')} />
              <button type="button" className="btn btn-outline-secondary" onClick={() => setVerClave((v) => !v)}
                      aria-label={verClave ? 'Ocultar contraseña' : 'Mostrar contraseña'} aria-pressed={verClave}>
                {verClave ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
              </button>
              {errors.nueva_password && <div className="invalid-feedback">{errors.nueva_password.message}</div>}
            </div>
            {nueva && (
              <div id="ft-fuerza" className="mt-2" aria-live="polite">
                <div className="d-flex justify-content-between small">
                  <span className="text-muted">Seguridad estimada:</span>
                  <span className={`joli-strength-label ${nivel.className}`}>{nivel.label}</span>
                </div>
                <div className="joli-strength-track" role="meter" aria-valuemin={0} aria-valuemax={4} aria-valuenow={score}
                     aria-label="Seguridad de la contraseña">
                  <div className={`joli-strength-bar ${nivel.className}`} style={{ width: `${(score / 4) * 100}%` }} />
                </div>
              </div>
            )}
          </div>

          <div className="mb-4">
            <label htmlFor="ft-confirmar" className="form-label small fw-semibold">Confirmar nueva contraseña</label>
            <input id="ft-confirmar" type={verClave ? 'text' : 'password'} autoComplete="new-password"
                   className={`form-control input-control ${errors.confirmar ? 'is-invalid' : ''}`}
                   aria-invalid={Boolean(errors.confirmar)} {...register('confirmar')} />
            {errors.confirmar && <div className="invalid-feedback">{errors.confirmar.message}</div>}
          </div>

          <button type="submit" className="btn btn-primary w-100" disabled={isSubmitting}>
            {isSubmitting ? 'Guardando…' : 'Definir contraseña y continuar'}
          </button>
          <button type="button" className="btn btn-link w-100 mt-2" onClick={() => void logout()}>
            Salir
          </button>
        </form>
      </section>
    </main>
  );
}
```

---

## 3. Estilos (`first_time_password.css`)

Solo tokens de [`variables.css`](../../../components/variables.css); funcionan en tema noche y día sin reglas `[data-theme]` propias.

```css
.joli-first-time-viewport {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100%;
  padding: var(--space-6);
  background-color: var(--bg-viewport);
}

.joli-first-time-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 100%;
  max-width: 460px; /* ancho de tarjeta, no de página */
  padding: var(--space-8) var(--space-6);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-modal);
  color: var(--text-primary);
}

.joli-first-time-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  margin-bottom: var(--space-5);
  border-radius: var(--radius-full);
  background: var(--status-success-bg);
  color: var(--brand-primary);
}

.joli-first-time-title { margin: 0 0 var(--space-2); font-size: var(--font-size-xl); font-weight: var(--font-weight-bold); }
.joli-first-time-subtitle { margin: 0 0 var(--space-6); font-size: var(--font-size-sm); color: var(--text-secondary); }

.joli-strength-track { height: 6px; margin-top: var(--space-1); border-radius: var(--radius-full); background: var(--bg-elevated); overflow: hidden; }
.joli-strength-bar { height: 100%; transition: width var(--transition-base); }
.joli-strength-bar.is-weak   { background: var(--status-error); }
.joli-strength-bar.is-medium { background: var(--status-warning); }
.joli-strength-bar.is-good   { background: var(--status-info); }
.joli-strength-bar.is-strong { background: var(--status-success); }
.joli-strength-label { font-weight: var(--font-weight-bold); }
.joli-strength-label.is-weak   { color: var(--status-error); }
.joli-strength-label.is-medium { color: var(--status-warning); }
.joli-strength-label.is-good   { color: var(--status-info); }
.joli-strength-label.is-strong { color: var(--status-success); }

@media (prefers-reduced-motion: reduce) { .joli-strength-bar { transition: none; } }
```
