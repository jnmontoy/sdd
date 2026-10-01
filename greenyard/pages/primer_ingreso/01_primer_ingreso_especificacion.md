# Especificación de Página: Cambio Obligatorio de Contraseña (Primer Ingreso)
## Ecosistema Jolifoods — Flujo de Activación Forzada de Credenciales

Esta especificación detalla el flujo de seguridad que se activa cuando un usuario recién creado o con contraseña restablecida por un administrador ingresa al sistema con la bandera `debe_cambiar_password = true`. El sistema restringe el acceso a cualquier otra vista hasta que establezca una clave personal robusta.

---

### 1. Requisitos de Negocio y Seguridad
1. **Intercepción Inmediata**: Si la respuesta del endpoint de login devuelve `debe_cambiar_password: true`, el frontend bloquea la navegación al Dashboard y redirige forzosamente a `/primer-ingreso`.
2. **Medidor de Fortaleza en Tiempo Real (Entropy Score 1-4)**:
   - Longitud mínima de 8 caracteres.
   - Al menos una letra mayúscula (`A-Z`).
   - Al menos un número (`0-9`).
   - Al menos un carácter especial (`!@#$%^&*`).
   - Escala cromática visual: Débil (rojo), Media (ámbar), Buena (azul), Fuerte (esmeralda).
3. **Validación de Coincidencia**: Confirmación idéntica de la nueva contraseña.
4. **Prohibición de Contraseñas Anteriores**: El backend valida que la nueva contraseña no coincida con la temporal.
5. **Transición a Sesión Plena**: Tras el éxito, se actualiza el token, se marca `debe_cambiar_password = false` y se redirige con un Toast de bienvenida al Dashboard.

---

### 2. Implementación TypeScript Canónica (`FirstTimePasswordPage.tsx`)

```tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, ShieldCheck, CheckCircle2, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { showToast } from '../../components/ui/ToastNotification';
import '../../styles/variables.css';

export const FirstTimePasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, login } = useAuth();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // 1. Medidor de fortaleza
  const [strength, setStrength] = useState({ score: 0, label: 'Muy débil', color: '#EF4444' });

  useEffect(() => {
    if (!password) {
      setStrength({ score: 0, label: '', color: '#E5E7EB' });
      return;
    }

    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    let label = 'Débil';
    let color = '#EF4444'; // Rojo

    if (score === 2) {
      label = 'Media';
      color = '#F59E0B'; // Ámbar
    } else if (score === 3) {
      label = 'Buena';
      color = '#3B82F6'; // Azul
    } else if (score >= 4) {
      label = 'Fuerte y Segura';
      color = '#10B981'; // Esmeralda
    }

    setStrength({ score, label, color });
  }, [password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (password.length < 8) {
      setErrorMsg('La contraseña debe tener mínimo 8 caracteres.');
      return;
    }

    if (strength.score < 3) {
      setErrorMsg('Por favor seleccione una contraseña más segura (incluya mayúsculas, números y símbolos).');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg('Las contraseñas ingresadas no coinciden.');
      return;
    }

    setIsLoading(true);

    try {
      const response = await api.post('/auth/change-first-password/', {
        nueva_password: password
      });

      showToast.success('Contraseña actualizada con éxito', {
        description: 'Bienvenido al ecosistema Jolifoods. Su cuenta ha sido activada.'
      });

      // Redirigir al inicio o dashboard
      navigate('/');
    } catch (err: any) {
      const errorText = err.response?.data?.detail || 'Error al cambiar la contraseña. Intente de nuevo.';
      setErrorMsg(errorText);
      showToast.error('Fallo en la activación', { description: errorText });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="joli-first-time-container">
      <div className="joli-first-time-card">
        <div className="first-time-icon-box">
          <ShieldCheck size={44} className="text-primary" />
        </div>

        <h3 className="first-time-title">Activación de Cuenta</h3>
        <p className="first-time-subtitle">
          Por motivos de seguridad corporativa, es obligatorio definir una nueva contraseña personal para el usuario <strong>{user?.nombre || user?.cedula}</strong>.
        </p>

        {errorMsg && (
          <div className="alert alert-danger py-2 px-3 small d-flex align-items-center gap-2 mb-3">
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="first-time-form">
          {/* Nueva Contraseña */}
          <div className="mb-3 text-start">
            <label className="form-label small fw-bold">Nueva Contraseña</label>
            <div className="position-relative">
              <input
                type={showPassword ? 'text' : 'password'}
                className="form-control"
                placeholder="Mínimo 8 caracteres, números y símbolos"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="btn-toggle-eye"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            {/* Medidor de barra */}
            {password && (
              <div className="mt-2">
                <div className="d-flex justify-content-between small text-muted mb-1">
                  <span>Seguridad:</span>
                  <span style={{ color: strength.color, fontWeight: 700 }}>{strength.label}</span>
                </div>
                <div className="progress" style={{ height: 6 }}>
                  <div
                    className="progress-bar"
                    style={{
                      width: `${(strength.score / 4) * 100}%`,
                      backgroundColor: strength.color,
                      transition: 'width 0.3s'
                    }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Confirmar Contraseña */}
          <div className="mb-4 text-start">
            <label className="form-label small fw-bold">Confirmar Nueva Contraseña</label>
            <input
              type={showPassword ? 'text' : 'password'}
              className="form-control"
              placeholder="Vuelva a escribir su nueva contraseña"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="joli-btn-primary w-100"
            disabled={isLoading || strength.score < 3 || password !== confirmPassword}
          >
            {isLoading ? 'Guardando credenciales...' : 'Establecer Contraseña y Continuar'}
          </button>
        </form>
      </div>
    </div>
  );
};
```

---

### 3. Estilos CSS (`first_time_password.css`)

```css
.joli-first-time-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background-color: var(--color-bg-body, #0F172A);
}

.joli-first-time-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 460px;
  width: 100%;
  padding: 36px 30px;
  background: var(--color-bg-card, #FFFFFF);
  border: 1px solid var(--color-border, #E5E7EB);
  border-radius: var(--radius-xl, 14px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
}

[data-theme="dark"] .joli-first-time-card {
  background: #1E293B;
  border-color: #334155;
}

.first-time-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(45, 106, 79, 0.12);
  margin-bottom: 20px;
}

.first-time-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  margin-bottom: 8px;
}

[data-theme="dark"] .first-time-title {
  color: #F8FAFC;
}

.first-time-subtitle {
  font-size: 13.5px;
  color: var(--color-text-secondary, #6B7280);
  line-height: 1.5;
  margin-bottom: 24px;
}

[data-theme="dark"] .first-time-subtitle {
  color: #94A3B8;
}

.first-time-form {
  width: 100%;
}

.btn-toggle-eye {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--color-text-muted, #9CA3AF);
  cursor: pointer;
  padding: 4px;
}
```
