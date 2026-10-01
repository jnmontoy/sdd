# Especificación Funcional y Técnica: Matriz de Roles y Permisos (RBAC)
## Ecosistema Jolifoods — Control de Acceso Granular por Módulo

Esta especificación detalla la interfaz gráfica y los contratos de backend para la administración centralizada de perfiles y la asignación matricial de permisos sobre las entidades del sistema.

---

### 1. Requisitos de Negocio
1. **Listado de Roles**: Visualización de los roles existentes (`ADMINISTRADOR`, `OPERADOR`, `AUDITOR`, `CONSULTOR`, etc.) con conteo de usuarios vinculados.
2. **Matriz Matricial de Permisos**:
   - Por cada módulo (`usuarios`, `auditoria`, `dashboard`, `reportes`, `configuracion`), se configuran permisos atómicos:
     - `ver` (lectura).
     - `crear` (inserción).
     - `editar` (actualización).
     - `eliminar` (baja física o lógica).
     - `exportar` (descarga a Excel o PDF).
3. **Protección de Rol Superadministrador**: Los permisos del rol `ADMINISTRADOR` o `SUPERADMIN` están bloqueados para edición con el fin de evitar bloqueos accidentales del sistema.
4. **Auditoría Inmutable**: Cualquier cambio en la matriz de permisos genera un registro obligatorio en la bitácora (`accion: 'ACTUALIZAR_ROL'`).

---

### 2. Contrato de API (FastAPI / Django)

- **GET `/api/roles/`**: Lista de roles con conteo de usuarios y estado.
- **GET `/api/roles/{id}/permisos/`**: Retorna la estructura de permisos agrupada por módulos.
- **PUT `/api/roles/{id}/permisos/`**: Actualización en lote de la matriz de permisos.

#### Payload de Actualización:
```json
{
  "rol_id": 2,
  "permisos": [
    { "modulo": "usuarios", "acciones": ["ver", "crear", "editar"] },
    { "modulo": "auditoria", "acciones": ["ver", "exportar"] },
    { "modulo": "dashboard", "acciones": ["ver"] }
  ]
}
```

---

### 3. Código JSX / React 19 Canónico (`RolesPage.tsx`)

```tsx
import React, { useState, useEffect } from 'react';
import { Shield, Plus, Check, Save, RotateCcw, AlertTriangle } from 'lucide-react';
import { api } from '../../services/api';
import { showToast } from '../../components/ui/ToastNotification';
import { ConfirmModal } from '../../components/ui/ConfirmModal';

interface PermisoModulo {
  modulo: string;
  nombre_modulo: string;
  ver: boolean;
  crear: boolean;
  editar: boolean;
  eliminar: boolean;
  exportar: boolean;
}

interface RolItem {
  id: number;
  codigo: string;
  nombre: string;
  es_sistema: boolean;
  usuarios_count: number;
}

export const RolesPage: React.FC = () => {
  const [roles, setRoles] = useState<RolItem[]>([]);
  const [selectedRol, setSelectedRol] = useState<RolItem | null>(null);
  const [permisos, setPermisos] = useState<PermisoModulo[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  useEffect(() => {
    // Carga de roles
    setRoles([
      { id: 1, codigo: 'ADMIN', nombre: 'Administrador General', es_sistema: true, usuarios_count: 3 },
      { id: 2, codigo: 'OPERADOR', nombre: 'Operador de Planta', es_sistema: false, usuarios_count: 14 },
      { id: 3, codigo: 'AUDITOR', nombre: 'Auditor de Seguridad', es_sistema: false, usuarios_count: 2 },
    ]);
    setSelectedRol({ id: 2, codigo: 'OPERADOR', nombre: 'Operador de Planta', es_sistema: false, usuarios_count: 14 });
    
    // Matriz de permisos de ejemplo
    setPermisos([
      { modulo: 'usuarios', nombre_modulo: 'Gestión de Usuarios', ver: true, crear: true, editar: true, eliminar: false, exportar: true },
      { modulo: 'auditoria', nombre_modulo: 'Bitácora de Auditoría', ver: true, crear: false, editar: false, eliminar: false, exportar: true },
      { modulo: 'dashboard', nombre_modulo: 'Tablero de Control', ver: true, crear: false, editar: false, eliminar: false, exportar: true },
      { modulo: 'configuracion', nombre_modulo: 'Parámetros del Sistema', ver: false, crear: false, editar: false, eliminar: false, exportar: false },
    ]);
  }, []);

  const handleTogglePermiso = (modulo: string, accion: 'ver' | 'crear' | 'editar' | 'eliminar' | 'exportar') => {
    if (selectedRol?.es_sistema) return;

    setPermisos((prev) =>
      prev.map((p) => {
        if (p.modulo === modulo) {
          const newVal = !p[accion];
          // Si activa crear o editar, automáticamente debe activar ver
          const updated = { ...p, [accion]: newVal };
          if (newVal && (accion === 'crear' || accion === 'editar' || accion === 'eliminar')) {
            updated.ver = true;
          }
          return updated;
        }
        return p;
      })
    );
  };

  const handleSavePermisos = async () => {
    setIsSaving(true);
    try {
      // Simulación de guardado en API
      await new Promise((r) => setTimeout(r, 600));
      showToast.success('Permisos actualizados con éxito', {
        description: `Los cambios para el rol ${selectedRol?.nombre} han sido aplicados.`
      });
      setIsConfirmOpen(false);
    } catch (err) {
      showToast.error('Fallo al guardar permisos');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="joli-page-container">
      <div className="joli-page-header">
        <div>
          <h2 className="joli-page-title">Roles y Permisos (RBAC)</h2>
          <p className="joli-page-subtitle">Configure los perfiles de usuario y asigne permisos específicos por módulo.</p>
        </div>
      </div>

      <div className="row g-4">
        {/* Selector de Roles */}
        <div className="col-12 col-md-4">
          <div className="joli-card p-3">
            <h6 className="fw-bold mb-3 d-flex align-items-center gap-2">
              <Shield size={18} className="text-primary" />
              <span>Roles Registrados</span>
            </h6>
            <div className="list-group">
              {roles.map((r) => (
                <button
                  key={r.id}
                  type="button"
                  className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center ${
                    selectedRol?.id === r.id ? 'active' : ''
                  }`}
                  onClick={() => setSelectedRol(r)}
                >
                  <div>
                    <div className="fw-semibold">{r.nombre}</div>
                    <small className="text-muted">{r.codigo}</small>
                  </div>
                  <span className="badge bg-secondary rounded-pill">{r.usuarios_count} usuarios</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Matriz de Permisos */}
        <div className="col-12 col-md-8">
          <div className="joli-card p-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 className="fw-bold mb-0">Permisos para: {selectedRol?.nombre}</h5>
                {selectedRol?.es_sistema && (
                  <small className="text-warning d-flex align-items-center gap-1 mt-1">
                    <AlertTriangle size={13} />
                    <span>Este rol es del sistema y sus permisos son inmutables.</span>
                  </small>
                )}
              </div>
              {!selectedRol?.es_sistema && (
                <button
                  type="button"
                  className="joli-btn-primary"
                  onClick={() => setIsConfirmOpen(true)}
                  disabled={isSaving}
                >
                  <Save size={16} className="me-1" />
                  <span>Guardar Matriz</span>
                </button>
              )}
            </div>

            <div className="table-responsive">
              <table className="table joli-table">
                <thead>
                  <tr>
                    <th>Módulo</th>
                    <th className="text-center">Ver</th>
                    <th className="text-center">Crear</th>
                    <th className="text-center">Editar</th>
                    <th className="text-center">Eliminar</th>
                    <th className="text-center">Exportar</th>
                  </tr>
                </thead>
                <tbody>
                  {permisos.map((p) => (
                    <tr key={p.modulo}>
                      <td className="fw-semibold">{p.nombre_modulo}</td>
                      {(['ver', 'crear', 'editar', 'eliminar', 'exportar'] as const).map((acc) => (
                        <td key={acc} className="text-center">
                          <input
                            type="checkbox"
                            className="form-check-input"
                            checked={p[acc]}
                            disabled={selectedRol?.es_sistema}
                            onChange={() => handleTogglePermiso(p.modulo, acc)}
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* ConfirmModal para aplicar cambios de permisos */}
      <ConfirmModal
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleSavePermisos}
        title="¿Confirmar actualización de permisos?"
        description={`Los usuarios con el rol ${selectedRol?.nombre} recibirán inmediatamente los nuevos privilegios en su siguiente acción.`}
        confirmText="Aplicar Permisos"
        variant="warning"
        isLoading={isSaving}
      />
    </div>
  );
};
```
