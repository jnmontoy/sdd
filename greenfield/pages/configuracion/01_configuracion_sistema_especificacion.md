# Especificación de Página: Configuración del Sistema
## Joli Foods — Parametrización Global y Políticas de Seguridad

Interfaz y contratos para administrar parámetros institucionales, políticas de sesión, prueba del canal de correo y modo mantenimiento.

---

## 1. Requisitos

1. **Acceso por permiso:** ver requiere `configuracion.ver`; guardar requiere `configuracion.editar` (BP-19). No se valida por nombre de rol.
2. **Pestañas:**
   - **General:** nombre visible de la aplicación, correo de contacto y logotipo (archivo validado según [`model/archivos`](../../../model/archivos/spec_model_archivos_media.md)).
   - **Seguridad:** cierre por inactividad (15–120 min), intentos fallidos antes de bloqueo (3–10) y duración del bloqueo (15–60 min).
   - **Correo:** muestra el servidor y puerto configurados (solo lectura) y permite **enviar un correo de prueba**.
   - **Mantenimiento:** modo mantenimiento con mensaje para usuarios sin permiso `configuracion.editar`.
3. **Secretos fuera de la interfaz (DEBE):** usuario y contraseña SMTP, claves de firma y credenciales de Azure se configuran por variables de entorno o gestor de secretos, nunca en la base de datos ni en esta pantalla. **Por qué:** una pantalla web que lee o escribe secretos los expone a cualquier XSS o cuenta administrativa comprometida.
4. **Límites en el servidor (DEBE):** el backend rechaza valores fuera de rango (p. ej. 0 intentos o 24 h de inactividad). **Por qué:** la configuración no debe poder desactivar los controles de seguridad.
5. **Política de contraseñas:** no se configura aquí; la definen `AUTH_PASSWORD_VALIDATORS` en código (ver login, BR-01).
6. **Bitácora:** cada cambio registra `CONFIG_UPDATED` con `payload_antes`/`payload_despues` en [`RegistroBitacoraAuditoria`](../../../model/auditoria/spec_model_bitacora.md).

### Contrato
| Método y ruta | Descripción |
| :--- | :--- |
| `GET /api/v1/configuracion/` | Devuelve `{ general, seguridad, correo: { host, puerto, tls }, mantenimiento }`. |
| `PATCH /api/v1/configuracion/` | Actualiza las secciones enviadas. 400 con detalle por campo si un valor está fuera de rango. |
| `POST /api/v1/configuracion/correo/prueba/` | Envía un correo de prueba al correo del usuario autenticado. Límite: 3 por hora. |

---

## 2. Implementación (`ConfiguracionPage.tsx`)

```tsx
import { useEffect, useId, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Settings, ShieldAlert, Mail, Wrench, Save, Send } from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { ENDPOINTS } from '../services/endpoints';
import { useAuth } from '../context/AuthContext';
import { showToast } from '../components/ToastNotification';
import { ConfirmModal } from '../components/modal/ConfirmModal';

const schema = z.object({
  general: z.object({
    nombre_aplicacion: z.string().trim().min(3).max(80),
    correo_contacto: z.string().email('Correo inválido.'),
  }),
  seguridad: z.object({
    inactividad_minutos: z.coerce.number().int().min(15).max(120),
    intentos_bloqueo: z.coerce.number().int().min(3).max(10),
    bloqueo_minutos: z.coerce.number().int().min(15).max(60),
  }),
  mantenimiento: z.object({
    activo: z.boolean(),
    mensaje: z.string().max(300),
  }),
});
type ConfigForm = z.infer<typeof schema>;
interface ConfigResponse extends ConfigForm { correo: { host: string; puerto: number; tls: boolean } }

type Tab = 'general' | 'seguridad' | 'correo' | 'mantenimiento';
const TABS: { id: Tab; label: string; icon: JSX.Element }[] = [
  { id: 'general', label: 'General', icon: <Settings size={15} aria-hidden="true" /> },
  { id: 'seguridad', label: 'Seguridad y sesiones', icon: <ShieldAlert size={15} aria-hidden="true" /> },
  { id: 'correo', label: 'Correo', icon: <Mail size={15} aria-hidden="true" /> },
  { id: 'mantenimiento', label: 'Mantenimiento', icon: <Wrench size={15} aria-hidden="true" /> },
];

export function ConfiguracionPage() {
  const { hasPermission } = useAuth();
  const puedeEditar = hasPermission('configuracion.editar');
  const baseId = useId();
  const [tab, setTab] = useState<Tab>('general');
  const [correo, setCorreo] = useState<ConfigResponse['correo'] | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  const { register, handleSubmit, reset, formState: { errors, isSubmitting, isDirty } } =
    useForm<ConfigForm>({ resolver: zodResolver(schema) });

  useEffect(() => {
    const controller = new AbortController();
    apiClient
      .get<ConfigResponse>(ENDPOINTS.CONFIGURACION.GENERAL, { signal: controller.signal })
      .then(({ data }) => { reset(data); setCorreo(data.correo); })
      .catch(() => { if (!controller.signal.aborted) showToast.error('No fue posible cargar la configuración.'); });
    return () => controller.abort();
  }, [reset]);

  const guardar = handleSubmit(async (values) => {
    try {
      const { data } = await apiClient.patch<ConfigResponse>(ENDPOINTS.CONFIGURACION.GENERAL, values);
      reset(data);
      showToast.success('Configuración guardada.');
    } catch {
      showToast.error('No fue posible guardar. Revisa los valores.');
    } finally {
      setIsConfirmOpen(false);
    }
  });

  const enviarPrueba = async () => {
    try {
      await apiClient.post(ENDPOINTS.CONFIGURACION.CORREO_PRUEBA);
      showToast.success('Correo de prueba enviado a tu buzón.');
    } catch {
      showToast.error('No fue posible enviar el correo de prueba.');
    }
  };

  const campo = (id: string, label: string, input: JSX.Element, error?: string) => (
    <div className="col-12 col-md-6">
      <label htmlFor={id} className="form-label fw-semibold">{label}</label>
      {input}
      {error && <div className="invalid-feedback d-block">{error}</div>}
    </div>
  );

  return (
    <div className="joli-page-container w-100">
      <div className="d-flex align-items-center justify-content-between flex-wrap gap-3 mb-4">
        <div>
          <h1 className="joli-page-title">Configuración del sistema</h1>
          <p className="text-muted small mb-0">Parámetros operativos, políticas de sesión y canal de correo.</p>
        </div>
        {puedeEditar && (
          <button type="button" className="btn btn-primary d-inline-flex align-items-center gap-2"
                  onClick={() => setIsConfirmOpen(true)} disabled={isSubmitting || !isDirty}>
            <Save size={16} aria-hidden="true" /><span>Guardar cambios</span>
          </button>
        )}
      </div>

      <div className="nav nav-tabs mb-4" role="tablist" aria-label="Secciones de configuración">
        {TABS.map((t) => (
          <button key={t.id} type="button" role="tab" id={`${baseId}-tab-${t.id}`}
                  aria-selected={tab === t.id} aria-controls={`${baseId}-panel-${t.id}`}
                  className={`nav-link d-inline-flex align-items-center gap-1 ${tab === t.id ? 'active' : ''}`}
                  onClick={() => setTab(t.id)}>
            {t.icon}<span>{t.label}</span>
          </button>
        ))}
      </div>

      <form className="joli-panel-card p-4" onSubmit={(e) => e.preventDefault()} noValidate>
        <fieldset disabled={!puedeEditar} className="border-0 p-0 m-0">
          <div role="tabpanel" id={`${baseId}-panel-general`} aria-labelledby={`${baseId}-tab-general`} hidden={tab !== 'general'} className="row g-3">
            {campo('cfg-nombre', 'Nombre de la aplicación',
              <input id="cfg-nombre" className="form-control input-control" {...register('general.nombre_aplicacion')} />,
              errors.general?.nombre_aplicacion?.message)}
            {campo('cfg-contacto', 'Correo de contacto',
              <input id="cfg-contacto" type="email" className="form-control input-control" {...register('general.correo_contacto')} />,
              errors.general?.correo_contacto?.message)}
          </div>

          <div role="tabpanel" id={`${baseId}-panel-seguridad`} aria-labelledby={`${baseId}-tab-seguridad`} hidden={tab !== 'seguridad'} className="row g-3">
            {campo('cfg-inactividad', 'Cierre por inactividad (minutos, 15–120)',
              <input id="cfg-inactividad" type="number" min={15} max={120} className="form-control input-control" {...register('seguridad.inactividad_minutos')} />,
              errors.seguridad?.inactividad_minutos?.message)}
            {campo('cfg-intentos', 'Intentos fallidos antes de bloqueo (3–10)',
              <input id="cfg-intentos" type="number" min={3} max={10} className="form-control input-control" {...register('seguridad.intentos_bloqueo')} />,
              errors.seguridad?.intentos_bloqueo?.message)}
            {campo('cfg-bloqueo', 'Duración del bloqueo (minutos, 15–60)',
              <input id="cfg-bloqueo" type="number" min={15} max={60} className="form-control input-control" {...register('seguridad.bloqueo_minutos')} />,
              errors.seguridad?.bloqueo_minutos?.message)}
          </div>

          <div role="tabpanel" id={`${baseId}-panel-correo`} aria-labelledby={`${baseId}-tab-correo`} hidden={tab !== 'correo'}>
            <dl className="row mb-3">
              <dt className="col-sm-3">Servidor</dt><dd className="col-sm-9">{correo?.host ?? '—'}</dd>
              <dt className="col-sm-3">Puerto</dt><dd className="col-sm-9">{correo?.puerto ?? '—'}</dd>
              <dt className="col-sm-3">TLS</dt><dd className="col-sm-9">{correo?.tls ? 'Sí' : 'No'}</dd>
            </dl>
            <p className="text-muted small">Las credenciales del servidor de correo se configuran por variables de entorno.</p>
            <button type="button" className="btn btn-outline-secondary d-inline-flex align-items-center gap-2" onClick={enviarPrueba}>
              <Send size={14} aria-hidden="true" /><span>Enviar correo de prueba</span>
            </button>
          </div>

          <div role="tabpanel" id={`${baseId}-panel-mantenimiento`} aria-labelledby={`${baseId}-tab-mantenimiento`} hidden={tab !== 'mantenimiento'}>
            <div className="form-check form-switch mb-3">
              <input id="cfg-mant" className="form-check-input" type="checkbox" {...register('mantenimiento.activo')} />
              <label className="form-check-label fw-semibold" htmlFor="cfg-mant">Activar modo mantenimiento</label>
            </div>
            <label htmlFor="cfg-mant-msg" className="form-label fw-semibold">Mensaje para los usuarios</label>
            <textarea id="cfg-mant-msg" rows={3} className="form-control input-control" {...register('mantenimiento.mensaje')} />
            <p className="text-muted small mt-2">
              Con el modo activo, los usuarios sin permiso de configuración ven una pantalla de servicio temporal y no pueden escribir datos.
            </p>
          </div>
        </fieldset>
      </form>

      <ConfirmModal
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={guardar}
        type="warning"
        isLoading={isSubmitting}
        title="¿Guardar cambios de configuración?"
        message="Las políticas de seguridad y los parámetros se aplican de inmediato a todos los usuarios."
        confirmText="Guardar"
      />
    </div>
  );
}
```

`ENDPOINTS.CONFIGURACION.GENERAL` (`/api/v1/configuracion/`) y `ENDPOINTS.CONFIGURACION.CORREO_PRUEBA` DEBEN agregarse al registro de endpoints.
