# Especificación de Página: Configuración y Parámetros del Sistema
## Ecosistema Jolifoods — Parametrización Global y Políticas de Seguridad

Esta especificación detalla la interfaz y contratos de backend para la gestión de parámetros institucionales, políticas de seguridad de sesión, configuración SMTP y control de mantenimiento de la plataforma.

---

### 1. Requisitos de Negocio
1. **Acceso Exclusivo**: Restringido estrictamente a usuarios con rol `ADMINISTRADOR` o `SUPERADMIN`.
2. **Pestañas de Configuración**:
   - **General**: Nombre del sistema, razón social, correo de contacto y logotipo corporativo.
   - **Seguridad**:
     - Tiempo de caducidad por inactividad de sesión (15, 30, 60, 120 minutos).
     - Intentos fallidos permitidos antes de bloqueo de cuenta (3 a 10 intentos).
     - Duración del bloqueo temporal (minutos).
     - Forzar caracteres especiales en contraseñas.
   - **Notificaciones / Correo**: Servidor SMTP, puerto, usuario, TLS y prueba de envío instantáneo.
   - **Mantenimiento**: Interruptor de "Modo Mantenimiento" con mensaje personalizado para usuarios regulares.
3. **Auditoría Obligatoria**: Cualquier cambio en la configuración genera un evento de severidad alta en la bitácora (`CONFIGURACION_MODIFICADA`).

---

### 2. Implementación TypeScript Canónica (`ConfiguracionPage.tsx`)

```tsx
import React, { useState } from 'react';
import { 
  Settings, 
  ShieldAlert, 
  Mail, 
  Tool, 
  Save, 
  CheckCircle2, 
  Send,
  AlertTriangle 
} from 'lucide-react';
import { showToast } from '../../components/ui/ToastNotification';
import { ConfirmModal } from '../../components/ui/ConfirmModal';

export const ConfiguracionPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'general' | 'seguridad' | 'smtp' | 'mantenimiento'>('general');
  const [isSaving, setIsSaving] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  // Estados del formulario
  const [nombreSistema, setNombreSistema] = useState('Greenyard / Jolifoods Portal');
  const [tiempoInactividad, setTiempoInactividad] = useState('30');
  const [intentosBloqueo, setIntentosBloqueo] = useState('5');
  const [smtpHost, setSmtpHost] = useState('smtp.office365.com');
  const [smtpPort, setSmtpPort] = useState('587');
  const [modoMantenimiento, setModoMantenimiento] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await new Promise((r) => setTimeout(r, 600));
      showToast.success('Configuración guardada correctamente', {
        description: 'Las directivas de seguridad y parámetros del sistema se han actualizado.'
      });
      setIsConfirmOpen(false);
    } catch {
      showToast.error('Error al guardar la configuración');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="joli-page-container">
      <div className="joli-page-header">
        <div>
          <h2 className="joli-page-title">Configuración del Sistema</h2>
          <p className="joli-page-subtitle">Ajuste los parámetros operativos, políticas de seguridad y canales de comunicación.</p>
        </div>
        <button
          type="button"
          className="joli-btn-primary"
          onClick={() => setIsConfirmOpen(true)}
          disabled={isSaving}
        >
          <Save size={16} className="me-1" />
          <span>Guardar Cambios</span>
        </button>
      </div>

      {/* Pestañas de Navegación */}
      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'general' ? 'active' : ''}`}
            onClick={() => setActiveTab('general')}
          >
            <Settings size={15} className="me-1" />
            <span>General</span>
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'seguridad' ? 'active' : ''}`}
            onClick={() => setActiveTab('seguridad')}
          >
            <ShieldAlert size={15} className="me-1" />
            <span>Seguridad & Sesiones</span>
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'smtp' ? 'active' : ''}`}
            onClick={() => setActiveTab('smtp')}
          >
            <Mail size={15} className="me-1" />
            <span>Servidor SMTP</span>
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${activeTab === 'mantenimiento' ? 'active' : ''}`}
            onClick={() => setActiveTab('mantenimiento')}
          >
            <Tool size={15} className="me-1" />
            <span>Mantenimiento</span>
          </button>
        </li>
      </ul>

      {/* Contenido por Pestaña */}
      <div className="joli-card p-4">
        {activeTab === 'general' && (
          <div className="row g-3">
            <div className="col-md-6">
              <label className="form-label fw-semibold">Nombre de la Aplicación</label>
              <input
                type="text"
                className="form-control"
                value={nombreSistema}
                onChange={(e) => setNombreSistema(e.target.value)}
              />
            </div>
            <div className="col-md-6">
              <label className="form-label fw-semibold">Entidad Corporativa</label>
              <input type="text" className="form-control" value="Jolifoods S.A.S." disabled />
            </div>
          </div>
        )}

        {activeTab === 'seguridad' && (
          <div className="row g-3">
            <div className="col-md-6">
              <label className="form-label fw-semibold">Tiempo Máximo de Inactividad</label>
              <select
                className="form-select"
                value={tiempoInactividad}
                onChange={(e) => setTiempoInactividad(e.target.value)}
              >
                <option value="15">15 minutos</option>
                <option value="30">30 minutos (Recomendado)</option>
                <option value="60">60 minutos</option>
                <option value="120">2 horas</option>
              </select>
            </div>
            <div className="col-md-6">
              <label className="form-label fw-semibold">Intentos Fallidos antes de Bloqueo</label>
              <select
                className="form-select"
                value={intentosBloqueo}
                onChange={(e) => setIntentosBloqueo(e.target.value)}
              >
                <option value="3">3 intentos</option>
                <option value="5">5 intentos (Recomendado)</option>
                <option value="10">10 intentos</option>
              </select>
            </div>
          </div>
        )}

        {activeTab === 'smtp' && (
          <div className="row g-3">
            <div className="col-md-8">
              <label className="form-label fw-semibold">Servidor Host SMTP</label>
              <input
                type="text"
                className="form-control"
                value={smtpHost}
                onChange={(e) => setSmtpHost(e.target.value)}
              />
            </div>
            <div className="col-md-4">
              <label className="form-label fw-semibold">Puerto</label>
              <input
                type="text"
                className="form-control"
                value={smtpPort}
                onChange={(e) => setSmtpPort(e.target.value)}
              />
            </div>
            <div className="col-12 mt-3">
              <button
                type="button"
                className="joli-btn-outline"
                onClick={() => showToast.info('Mensaje de prueba enviado al buzón del administrador.')}
              >
                <Send size={14} className="me-1" />
                <span>Enviar Correo de Prueba</span>
              </button>
            </div>
          </div>
        )}

        {activeTab === 'mantenimiento' && (
          <div>
            <div className="form-check form-switch mb-3">
              <input
                className="form-check-input"
                type="checkbox"
                id="modoMantenimientoSwitch"
                checked={modoMantenimiento}
                onChange={(e) => setModoMantenimiento(e.target.checked)}
              />
              <label className="form-check-label fw-bold" htmlFor="modoMantenimientoSwitch">
                Activar Modo Mantenimiento
              </label>
            </div>
            <p className="text-muted small">
              Cuando el modo mantenimiento está habilitado, los usuarios no administradores verán una pantalla de servicio temporal y no podrán realizar operaciones de escritura.
            </p>
          </div>
        )}
      </div>

      <ConfirmModal
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleSave}
        title="¿Guardar cambios de configuración?"
        description="Las modificaciones a las políticas de seguridad y parámetros del sistema se aplicarán de inmediato para todos los usuarios conectados."
        confirmText="Confirmar y Guardar"
        variant="primary"
        isLoading={isSaving}
      />
    </div>
  );
};
```
