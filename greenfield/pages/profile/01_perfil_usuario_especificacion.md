# 01. Especificación del Perfil de Usuario y Seguridad
## Joli Foods — Spec-Driven Development (SDD)

Vista **Mi perfil**, accesible desde el menú de perfil de la barra superior. El colaborador consulta sus datos, cambia su contraseña y revisa o cierra sus sesiones activas. Ocupa el 100% del ancho del área de contenido (DEBERÍA).

---

## 1. Topología

```
+-----------------------------------------------------------------------------------------------+
|  Mi perfil y seguridad                                                                        |
+----------------------------------------------------+------------------------------------------+
|  Datos del colaborador                             |  Cambiar contraseña                      |
|  - Avatar (foto o iniciales)                       |  - Contraseña actual (ver/ocultar)       |
|  - Nombre: Usuario Ejemplo                         |  - Nueva contraseña (medidor de fuerza)  |
|  - Documento: 1000000001 (solo lectura)            |  - Confirmar nueva contraseña            |
|  - Correo: usuario@ejemplo.com                     |  - [ Actualizar contraseña ]             |
|  - Sede y roles (badges)                           |                                          |
+----------------------------------------------------+------------------------------------------+
|  Sesiones activas                                                                             |
|  - Escritorio • Chrome en Windows (esta sesión) • inició hace 1 hora                          |
|  - Móvil • Edge en Android • inició ayer                         [ Cerrar sesión ]            |
+-----------------------------------------------------------------------------------------------+
```

---

## 2. Contratos de API

### 2.1. Cambio de contraseña — `POST /api/v1/auth/change-password/` (`ENDPOINTS.AUTH.CHANGE_PASSWORD`)
- **Autenticación:** `Authorization: Bearer <access>` + cookie de refresh (para rotarla) y `X-CSRFToken`.
- **Límite:** 5 intentos fallidos de `password_actual` cada 15 min por usuario.
- **Petición:**
  ```json
  { "password_actual": "<CONTRASEÑA_ACTUAL>", "nueva_password": "<NUEVA_CONTRASEÑA>" }
  ```
- **Proceso (en `transaction.atomic()`):** verifica `password_actual` con `check_password`, aplica `validate_password` (mismos validadores que el login), `set_password`, pone en lista negra **todos** los refresh tokens del usuario, cierra sus `SesionUsuario`, emite un refresh nuevo para la sesión actual (cookie rotada) y registra `PASSWORD_CHANGED` en la bitácora.
- **200:** `{ "access": "<JWT>", "expires_in": 900, "message": "Contraseña actualizada. Se cerraron tus otras sesiones." }`
- **400:** `PASSWORD_POLICY` (con reglas incumplidas) o `PASSWORD_REUSED` (igual a la actual). **401:** `INVALID_CURRENT_PASSWORD`.

### 2.2. Sesiones activas
| Método y ruta | Respuesta |
| :--- | :--- |
| `GET /api/v1/auth/sesiones/` | `[{ "id": "uuid", "dispositivo": "Desktop", "navegador": "Chrome en Windows", "fecha_inicio": "...", "es_actual": true }]` — sin IP completa. |
| `DELETE /api/v1/auth/sesiones/{id}/` | 204. Pone en lista negra el refresh de esa sesión y la marca inactiva. No permite cerrar la sesión actual (para eso está "Salir"). |

Solo se listan sesiones del propio usuario; un `id` ajeno responde 404 (no 403) para no confirmar su existencia.

---

## 3. Implementación (`ProfilePage.tsx`)

```tsx
import { useCallback, useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { isAxiosError } from 'axios';
import { User, KeyRound, Laptop, Smartphone, Shield, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiClient, setAccessToken } from '../services/apiClient';
import { ENDPOINTS } from '../services/endpoints';
import { showToast } from '../components/ToastNotification';
import { ConfirmModal } from '../components/modal/ConfirmModal';
import './profile.css';

const cambioSchema = z
  .object({
    password_actual: z.string().min(1, 'Ingresa tu contraseña actual.'),
    nueva_password: z.string().min(10, 'Mínimo 10 caracteres.').max(128),
    confirmar: z.string(),
  })
  .refine((v) => v.nueva_password === v.confirmar, { path: ['confirmar'], message: 'Las contraseñas no coinciden.' })
  .refine((v) => v.nueva_password !== v.password_actual, { path: ['nueva_password'], message: 'Debe ser distinta de la actual.' });
type CambioForm = z.infer<typeof cambioSchema>;

interface Sesion { id: string; dispositivo: string | null; navegador: string; fecha_inicio: string; es_actual: boolean }

export function ProfilePage() {
  const { user } = useAuth();
  const [verActual, setVerActual] = useState(false);
  const [verNueva, setVerNueva] = useState(false);
  const [sesiones, setSesiones] = useState<Sesion[]>([]);
  const [sesionACerrar, setSesionACerrar] = useState<Sesion | null>(null);
  const [recargar, setRecargar] = useState(0);

  const { register, handleSubmit, reset, setError, formState: { errors, isSubmitting } } =
    useForm<CambioForm>({ resolver: zodResolver(cambioSchema) });

  useEffect(() => {
    const controller = new AbortController();
    apiClient
      .get<Sesion[]>(ENDPOINTS.AUTH.SESIONES, { signal: controller.signal })
      .then((r) => setSesiones(r.data))
      .catch(() => { if (!controller.signal.aborted) showToast.error('No fue posible cargar tus sesiones.'); });
    return () => controller.abort();
  }, [recargar]);

  const onCambiar = handleSubmit(async ({ password_actual, nueva_password }) => {
    try {
      const { data } = await apiClient.post<{ access: string }>(ENDPOINTS.AUTH.CHANGE_PASSWORD, { password_actual, nueva_password });
      setAccessToken(data.access); // la sesión actual continúa con el token nuevo
      reset();
      showToast.success('Contraseña actualizada. Se cerraron tus otras sesiones.');
      setRecargar((n) => n + 1);
    } catch (err: unknown) {
      const code = isAxiosError<{ error_code?: string; message?: string }>(err) ? err.response?.data?.error_code : undefined;
      if (code === 'INVALID_CURRENT_PASSWORD') setError('password_actual', { message: 'La contraseña actual no es correcta.' });
      else showToast.error('No fue posible cambiar la contraseña.');
    }
  });

  const cerrarSesion = useCallback(async () => {
    if (!sesionACerrar) return;
    try {
      await apiClient.delete(ENDPOINTS.AUTH.SESION(sesionACerrar.id));
      showToast.success('Sesión cerrada.');
      setRecargar((n) => n + 1);
    } catch {
      showToast.error('No fue posible cerrar la sesión.');
    } finally {
      setSesionACerrar(null);
    }
  }, [sesionACerrar]);

  const iniciales = `${user?.nombre ?? ''}`.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0]).join('').toUpperCase();

  return (
    <div className="joli-page-container w-100">
      <header className="mb-4">
        <h1 className="joli-page-title">Mi perfil y seguridad</h1>
        <p className="text-muted small mb-0">Tus datos institucionales, contraseña y sesiones abiertas.</p>
      </header>

      <div className="row g-4">
        <div className="col-12 col-xl-5">
          <section className="joli-panel-card h-100" aria-labelledby="perfil-datos">
            <header className="joli-panel-header">
              <h2 id="perfil-datos" className="joli-panel-title">Datos del colaborador</h2>
              <User size={18} aria-hidden="true" />
            </header>
            <div className="joli-panel-body">
              <div className="d-flex align-items-center gap-3 mb-4">
                {user?.avatar_url
                  ? <img src={user.avatar_url} alt="" className="joli-avatar-large" />
                  : <span className="joli-avatar-large" aria-hidden="true">{iniciales || '?'}</span>}
                <div>
                  <p className="h5 mb-1">{user?.nombre}</p>
                  <span className="d-inline-flex flex-wrap gap-1">{user?.roles.map((r) => <span key={r} className="badge text-bg-secondary">{r}</span>)}</span>
                </div>
              </div>
              <dl className="joli-data-list">
                <dt>Documento</dt><dd>{user?.numero_documento}</dd>
                <dt>Correo</dt><dd>{user?.email}</dd>
              </dl>
            </div>
          </section>
        </div>

        <div className="col-12 col-xl-7">
          <section className="joli-panel-card h-100" aria-labelledby="perfil-clave">
            <header className="joli-panel-header">
              <h2 id="perfil-clave" className="joli-panel-title">Cambiar contraseña</h2>
              <KeyRound size={18} aria-hidden="true" />
            </header>
            <form className="joli-panel-body" onSubmit={onCambiar} noValidate>
              <div className="mb-3">
                <label htmlFor="pwd-actual" className="form-label small fw-semibold">Contraseña actual</label>
                <div className="input-group">
                  <input id="pwd-actual" type={verActual ? 'text' : 'password'} autoComplete="current-password"
                         className={`form-control input-control ${errors.password_actual ? 'is-invalid' : ''}`}
                         aria-invalid={Boolean(errors.password_actual)} {...register('password_actual')} />
                  <button type="button" className="btn btn-outline-secondary" onClick={() => setVerActual((v) => !v)}
                          aria-label={verActual ? 'Ocultar contraseña actual' : 'Mostrar contraseña actual'} aria-pressed={verActual}>
                    {verActual ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
                  </button>
                  {errors.password_actual && <div className="invalid-feedback">{errors.password_actual.message}</div>}
                </div>
              </div>

              <div className="mb-3">
                <label htmlFor="pwd-nueva" className="form-label small fw-semibold">Nueva contraseña</label>
                <div className="input-group">
                  <input id="pwd-nueva" type={verNueva ? 'text' : 'password'} autoComplete="new-password"
                         className={`form-control input-control ${errors.nueva_password ? 'is-invalid' : ''}`}
                         aria-invalid={Boolean(errors.nueva_password)} {...register('nueva_password')} />
                  <button type="button" className="btn btn-outline-secondary" onClick={() => setVerNueva((v) => !v)}
                          aria-label={verNueva ? 'Ocultar nueva contraseña' : 'Mostrar nueva contraseña'} aria-pressed={verNueva}>
                    {verNueva ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
                  </button>
                  {errors.nueva_password && <div className="invalid-feedback">{errors.nueva_password.message}</div>}
                </div>
              </div>

              <div className="mb-4">
                <label htmlFor="pwd-confirmar" className="form-label small fw-semibold">Confirmar nueva contraseña</label>
                <input id="pwd-confirmar" type="password" autoComplete="new-password"
                       className={`form-control input-control ${errors.confirmar ? 'is-invalid' : ''}`}
                       aria-invalid={Boolean(errors.confirmar)} {...register('confirmar')} />
                {errors.confirmar && <div className="invalid-feedback">{errors.confirmar.message}</div>}
              </div>

              <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Actualizando…' : 'Actualizar contraseña'}
              </button>
            </form>
          </section>
        </div>
      </div>

      <section className="joli-panel-card mt-4" aria-labelledby="perfil-sesiones">
        <header className="joli-panel-header">
          <h2 id="perfil-sesiones" className="joli-panel-title">Sesiones activas</h2>
          <Shield size={18} aria-hidden="true" />
        </header>
        <ul className="joli-session-list">
          {sesiones.map((s) => (
            <li key={s.id} className="joli-session-item">
              {s.dispositivo === 'Mobile' ? <Smartphone size={22} aria-hidden="true" /> : <Laptop size={22} aria-hidden="true" />}
              <div className="flex-grow-1">
                <strong className="small">{s.navegador}</strong>
                {s.es_actual && <span className="badge text-bg-success ms-2">Esta sesión</span>}
                <div className="text-muted small">Inició el {new Date(s.fecha_inicio).toLocaleString('es-CO')}</div>
              </div>
              {!s.es_actual && (
                <button type="button" className="btn btn-sm btn-outline-danger" onClick={() => setSesionACerrar(s)}>
                  Cerrar sesión
                </button>
              )}
            </li>
          ))}
        </ul>
      </section>

      <ConfirmModal
        isOpen={sesionACerrar !== null}
        onClose={() => setSesionACerrar(null)}
        onConfirm={cerrarSesion}
        type="warning"
        title="¿Cerrar esta sesión?"
        message={`Se cerrará la sesión de ${sesionACerrar?.navegador ?? 'ese dispositivo'}.`}
        confirmText="Cerrar sesión"
      />
    </div>
  );
}
```

`ENDPOINTS.AUTH.SESIONES` (`/api/v1/auth/sesiones/`) y `ENDPOINTS.AUTH.SESION(id)` DEBEN agregarse al registro de endpoints si no existen; `setAccessToken` es la función del cliente HTTP que guarda el access token en memoria ([`api_client.md`](../../../components/services/api_client.md)).

---

## 4. Estilos (`profile.css`)

Solo tokens de [`variables.css`](../../../components/variables.css). `joli-panel-card` y `joli-page-title` se comparten con el tablero.

```css
.joli-page-title {
  margin: 0 0 var(--space-1);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-extrabold);
  color: var(--text-primary);
}

.joli-avatar-large {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  object-fit: cover;
  border-radius: var(--radius-full);
  background: var(--brand-primary);
  color: var(--text-on-brand);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}

.joli-data-list { margin: 0; }
.joli-data-list dt {
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}
.joli-data-list dd {
  margin: 0 0 var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--border-subtle);
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.joli-session-list { list-style: none; margin: 0; padding: 0; }
.joli-session-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}
.joli-session-item:last-child { border-bottom: none; }
```
