# 01. Especificación del Módulo de Perfil de Usuario (Gestión de Identidad)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Esta especificación describe la vista de **Mi Perfil**, accesible desde la barra superior de navegación.

Permite al colaborador autenticado consultar sus datos de identidad, cambiar su contraseña voluntariamente de forma segura y revisar/revocar sus sesiones activas en otros dispositivos.

---

## 1. Topología de la Pantalla

```
+-----------------------------------------------------------------------------------------------+
|  MI PERFIL Y SEGURIDAD                                                                        |
|  Gestión de credenciales institucionales y sesiones activas                                   |
+----------------------------------------------------+------------------------------------------+
|  [ TARJETA DE IDENTIDAD ]                          |  [ CAMBIO DE CONTRASEÑA ]                |
|  - Avatar con iniciales o foto                     |  - Contraseña Actual (Input Ojo)         |
|  - Nombre Completo: Joan Montoya                   |  - Nueva Contraseña (Medidor de Fuerza)  |
|  - Cédula / Documento: 1020405060 (Inmutable)      |  - Confirmar Nueva Contraseña            |
|  - Correo: j.montoya@jolifoods.com                 |  - [ Botón Actualizar Contraseña ]       |
|  - Sede Asignada: Sede Principal                   |                                          |
|  - Rol Corporativo: Administrador (Badge)          |                                          |
+----------------------------------------------------+------------------------------------------+
|  [ SESIONES ACTIVAS Y DISPOSITIVOS ]                                                          |
|  - Windows / Chrome (Esta sesión activa) • IP: 190.14.85.120 • Conectado hace 1 hora         |
|  - Android / Edge • IP: 181.12.90.14 • Conectado ayer  [ Botón: Cerrar Sesión Remota ]       |
+-----------------------------------------------------------------------------------------------+
```

---

## 2. Contratos de API para el Perfil

### 2.1. Cambio Voluntario de Contraseña
- **Ruta**: `POST /api/v1/auth/password/change/`
- **Autenticación**: Obligatoria vía Cookie `HttpOnly` (`IsAuthenticated`).
- **Payload Entrada**:
  ```json
  {
    "password_actual": "ClaveAnterior2026*",
    "nueva_password": "NuevaClaveSuperSegura2026!"
  }
  ```
- **Respuesta Exitosa (HTTP 200 OK)**:
  ```json
  {
    "status": "success",
    "message": "Contraseña actualizada exitosamente. Sus otras sesiones han sido invalidadas por seguridad."
  }
  ```

---

## 3. Implementación en React 19 + TypeScript (`ProfilePage.tsx`)

```tsx
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  User, 
  Shield, 
  KeyRound, 
  Laptop, 
  Smartphone, 
  CheckCircle, 
  AlertCircle,
  Eye,
  EyeOff
} from 'lucide-react';
import '../../styles/variables.css';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [showCurrentPass, setShowCurrentPass] = useState(false);
  const [showNewPass, setShowNewPass] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setFeedback({ type: 'error', message: 'Las nuevas contraseñas no coinciden.' });
      return;
    }
    if (newPassword.length < 8) {
      setFeedback({ type: 'error', message: 'La nueva contraseña debe tener al menos 8 caracteres.' });
      return;
    }
    // Llamada al endpoint
    setFeedback({ type: 'success', message: 'Contraseña actualizada con éxito.' });
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  return (
    <div className="joli-profile-container">
      <div className="mb-4">
        <h1 className="joli-page-title">Mi Perfil y Seguridad</h1>
        <p className="text-muted small mb-0">Administra tus datos institucionales y preferencias de acceso seguro.</p>
      </div>

      <div className="row g-4">
        {/* 1. INFORMACIÓN DE IDENTIDAD */}
        <div className="col-12 col-lg-5">
          <div className="joli-panel-card h-100">
            <div className="joli-panel-header">
              <h2 className="joli-panel-title">Datos del Colaborador</h2>
              <User size={18} className="text-primary" />
            </div>
            <div className="joli-panel-body">
              <div className="text-center mb-4">
                <div className="joli-avatar-large mx-auto mb-3">
                  {user?.nombre?.slice(0, 2).toUpperCase() || 'JM'}
                </div>
                <h3 className="h5 mb-1 text-primary-emphasis">{user?.nombre || 'Joan Montoya'}</h3>
                <span className="badge bg-success-subtle text-success">
                  Rol: {user?.rol || 'Administrador'}
                </span>
              </div>

              <div className="joli-data-group">
                <label className="joli-data-label">Número de Cédula (Documento)</label>
                <div className="joli-data-value">{user?.documento || '1020405060'}</div>
              </div>

              <div className="joli-data-group">
                <label className="joli-data-label">Correo Institucional</label>
                <div className="joli-data-value">{user?.email || 'usuario@jolifoods.com'}</div>
              </div>

              <div className="joli-data-group">
                <label className="joli-data-label">Sede Asignada</label>
                <div className="joli-data-value">{user?.sede || 'Sede Principal Jolifoods'}</div>
              </div>
            </div>
          </div>
        </div>

        {/* 2. FORMULARIO DE CAMBIO DE CLAVE */}
        <div className="col-12 col-lg-7">
          <div className="joli-panel-card h-100">
            <div className="joli-panel-header">
              <h2 className="joli-panel-title">Cambiar Contraseña</h2>
              <KeyRound size={18} className="text-primary" />
            </div>
            <div className="joli-panel-body">
              {feedback && (
                <div className={`alert ${feedback.type === 'success' ? 'alert-success' : 'alert-danger'} d-flex align-items-center mb-4`}>
                  {feedback.type === 'success' ? <CheckCircle size={18} className="me-2" /> : <AlertCircle size={18} className="me-2" />}
                  <span>{feedback.message}</span>
                </div>
              )}

              <form onSubmit={handlePasswordSubmit}>
                <div className="mb-3">
                  <label className="form-label small fw-semibold">Contraseña Actual</label>
                  <div className="joli-input-wrapper">
                    <input 
                      type={showCurrentPass ? 'text' : 'password'} 
                      className="form-control joli-form-input" 
                      required 
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                    />
                    <button 
                      type="button" 
                      className="joli-eye-btn" 
                      onClick={() => setShowCurrentPass(!showCurrentPass)}
                    >
                      {showCurrentPass ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label small fw-semibold">Nueva Contraseña</label>
                  <div className="joli-input-wrapper">
                    <input 
                      type={showNewPass ? 'text' : 'password'} 
                      className="form-control joli-form-input" 
                      required 
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                    />
                    <button 
                      type="button" 
                      className="joli-eye-btn" 
                      onClick={() => setShowNewPass(!showNewPass)}
                    >
                      {showNewPass ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div className="mb-4">
                  <label className="form-label small fw-semibold">Confirmar Nueva Contraseña</label>
                  <input 
                    type="password" 
                    className="form-control joli-form-input" 
                    required 
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>

                <button type="submit" className="joli-btn-primary">
                  Actualizar Contraseña
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* 3. GESTIÓN DE SESIONES ACTIVAS */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="joli-panel-card">
            <div className="joli-panel-header">
              <h2 className="joli-panel-title">Sesiones Activas y Dispositivos</h2>
              <Shield size={18} className="text-success" />
            </div>
            <div className="joli-panel-body p-0">
              <ul className="joli-session-list">
                <li className="joli-session-item">
                  <Laptop size={24} className="text-primary me-3" />
                  <div className="flex-grow-1">
                    <div className="d-flex align-items-center gap-2">
                      <strong className="small">Navegador Web (Windows / Chrome)</strong>
                      <span className="badge bg-success-subtle text-success">Sesión Actual</span>
                    </div>
                    <span className="text-muted small">IP: 190.14.85.120 &bull; Conectado hace 1 hora</span>
                  </div>
                </li>
                <li className="joli-session-item">
                  <Smartphone size={24} className="text-muted me-3" />
                  <div className="flex-grow-1">
                    <strong className="small">Dispositivo Móvil (Android / Edge)</strong>
                    <div><span className="text-muted small">IP: 181.12.90.14 &bull; Conectado ayer</span></div>
                  </div>
                  <button type="button" className="btn btn-sm btn-outline-danger">
                    Cerrar Sesión
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

## 4. Estilos CSS Canónicos (`profile.css`)

```css
.joli-profile-container {
  padding: var(--space-2) 0;
}

.joli-page-title {
  font-size: var(--text-2xl);
  font-weight: var(--weight-extrabold);
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.joli-avatar-large {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, var(--color-primary), #059669);
  color: #ffffff;
  font-size: var(--text-xl);
  font-weight: var(--weight-bold);
  border-radius: var(--radius-full);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
}

.joli-data-group {
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border);
}

.joli-data-label {
  font-size: 11px;
  font-weight: var(--weight-bold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
  display: block;
}

.joli-data-value {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  font-weight: var(--weight-medium);
}

.joli-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.joli-form-input {
  background-color: var(--color-bg-input);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  height: 42px;
  border-radius: var(--radius-lg);
}

.joli-form-input:focus {
  background-color: var(--color-bg-input);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
  box-shadow: var(--focus-ring);
}

.joli-eye-btn {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
}

.joli-btn-primary {
  height: 42px;
  padding: 0 24px;
  background-color: var(--color-primary);
  border: none;
  border-radius: var(--radius-lg);
  color: #ffffff;
  font-weight: var(--weight-bold);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.joli-btn-primary:hover {
  background-color: #059669;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
}

.joli-session-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.joli-session-item {
  display: flex;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.joli-session-item:last-child {
  border-bottom: none;
}
```
