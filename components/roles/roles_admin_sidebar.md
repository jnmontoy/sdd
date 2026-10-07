# Especificación de Componente: Panel Lateral de Administración de Roles y Permisos (`RolesAdminSidebar.tsx`)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)
### Basado en la Arquitectura de Estabilización de Permisos de `tiendita`

El componente `RolesAdminSidebar` es un panel lateral deslizante (Right Drawer) diseñado para que los Administradores y Super Administradores gestionen dinámicamente los roles de la plataforma y sus permisos asociados en tiempo real, sin requerir reinicios de servidor ni migraciones de base de datos.

---

## 1. Principio Arquitectónico: Estabilización de Permisos Desacoplada

> [!IMPORTANT]
> **REGLA DE ORO DE ARQUITECTURA**:
> Jamás se deben "preguntar" los roles de una plataforma en un Enum rígido ni quemar listas estáticas de roles en frontend o backend.
> En su lugar, el sistema implementa **Estabilización de Permisos**:
> 1. Existe una **tabla independiente para roles (`roles`)** con un campo `JSONField` donde se almacenan las banderas booleanas de permisos.
> 2. La tabla `usuarios` se cruza con `roles` mediante una relación **Muchos a Muchos (`ManyToManyField`)**.
> 3. Los permisos se agregan/combinan en el backend (`/api/mis-permisos/`), otorgando acceso si al menos un rol asignado tiene el permiso en `true`.
> 4. El frontend se sincroniza en caliente, de modo que cualquier ajuste en este panel se refleja en la interfaz del usuario inmediatamente sin cerrar sesión.

---

## 2. Contrato de Datos e Interfaces TypeScript

```typescript
// src/types/roles.types.ts

export interface PermissionItem {
  key: string;
  label: string;
  description: string;
}

export interface PermissionGroup {
  category: string;
  icon: React.ReactNode;
  items: PermissionItem[];
}

export interface Rol {
  id: number;
  nombre: string;
  permisos: Record<string, boolean>;
}

export interface Usuario {
  id?: number;
  documento: string;
  nombre: string;
  cargo: string;
  correo_electronico: string;
  roles: string[]; // o Rol[]
  is_active: boolean;
}
```

---

## 3. Grupos Canónicos de Permisos del Sistema

Los permisos se organizan en categorías funcionales legibles con iconos descriptivos:

```typescript
export const PERMISSION_GROUPS: PermissionGroup[] = [
  {
    category: 'Acceso General & Interfaz',
    icon: <Bell size={16} />,
    items: [
      {
        key: 'ver_administracion_home',
        label: 'Ver Botón "Administración" en Home',
        description: 'Muestra u oculta el botón de acceso al Panel de Administración principal.',
      },
      {
        key: 'ver_notificaciones_topheader',
        label: 'Ver icono de Notificaciones en el TopHeader',
        description: 'Permite visualizar el icono y campana de alertas en la barra superior.',
      },
      {
        key: 'ver_admin_roles_button',
        label: 'Ver Botón "Administración Roles"',
        description: 'Permite abrir el panel lateral de Administración de Roles y Permisos.',
      },
    ],
  },
  {
    category: 'Módulos Operativos y Transacciones',
    icon: <Package size={16} />,
    items: [
      {
        key: 'modulo_operaciones_crear',
        label: 'Creación y Registro de Transacciones',
        description: 'Habilita formularios de captura y entrega de bienes o registros.',
      },
      {
        key: 'modulo_operaciones_editar',
        label: 'Edición y Modificación',
        description: 'Permite modificar registros ya creados desde el Drawer de edición.',
      },
      {
        key: 'modulo_operaciones_anular',
        label: 'Anulación con ConfirmModal',
        description: 'Autoriza anular o dar de baja registros exigiendo motivo obligatorio.',
      },
    ],
  },
  {
    category: 'Informes y Actas',
    icon: <FileText size={16} />,
    items: [
      {
        key: 'informes_generales',
        label: 'Consulta y Exportación de Informes',
        description: 'Visualización de reportes históricos, exportación a Excel y PDF.',
      },
    ],
  },
  {
    category: 'Administración Global',
    icon: <Users size={16} />,
    items: [
      {
        key: 'admin_colaboradores',
        label: 'Administración de Usuarios y Cuentas',
        description: 'Gestión de perfiles de usuario, activación/desactivación y asignación de roles.',
      },
    ],
  },
];
```

---

## 4. Implementación del Componente (`RolesAdminSidebar.tsx`)

```tsx
import React, { useState, useEffect } from 'react';
import { 
  X, Shield, Users, CheckSquare, Square, Save, Loader2, 
  Lock, RefreshCw 
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'sonner';
import { PERMISSION_GROUPS, type Rol, type Usuario } from '../../types/roles.types';
import './RolesAdminSidebar.css';

interface RolesAdminSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onFilterRole?: (roleName: string) => void;
  theme?: 'light' | 'dark';
}

const SA_LOCKED_KEYS = [
  'ver_administracion_home',
  'ver_admin_roles_button',
  'admin_colaboradores',
];

export const RolesAdminSidebar: React.FC<RolesAdminSidebarProps> = ({
  isOpen,
  onClose,
  onFilterRole,
  theme,
}) => {
  const { updateRolePermissions } = useAuth();
  const [roles, setRoles] = useState<Rol[]>([]);
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [permisosState, setPermisosState] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);

  const currentRole = roles.find((r) => r.id === selectedRoleId);
  const isSARole = currentRole?.nombre.trim().toUpperCase() === 'SA';

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resRoles, resUsers] = await Promise.all([
        fetch('/api/v1/roles/').then((r) => r.json()),
        fetch('/api/v1/usuarios/').then((r) => r.json()),
      ]);
      setRoles(resRoles);
      setUsuarios(resUsers.results || resUsers);

      if (resRoles.length > 0) {
        setSelectedRoleId(resRoles[0].id);
        initPermisosState(resRoles[0].permisos, resRoles[0].nombre);
      }
    } catch (err) {
      toast.error('Error al cargar la configuración de roles');
    } finally {
      setLoading(false);
    }
  };

  const initPermisosState = (rawPermisos?: Record<string, boolean>, roleName?: string) => {
    const isSA = roleName?.trim().toUpperCase() === 'SA';
    const initialState: Record<string, boolean> = {};
    PERMISSION_GROUPS.forEach((group) => {
      group.items.forEach((item) => {
        if (isSA && SA_LOCKED_KEYS.includes(item.key)) {
          initialState[item.key] = true;
        } else {
          initialState[item.key] = rawPermisos ? Boolean(rawPermisos[item.key]) : false;
        }
      });
    });
    setPermisosState(initialState);
  };

  const handleSelectRole = (role: Rol) => {
    setSelectedRoleId(role.id);
    initPermisosState(role.permisos, role.nombre);
  };

  const handleTogglePermission = (key: string) => {
    if (isSARole && SA_LOCKED_KEYS.includes(key)) {
      toast.info('Este permiso es mandatorio e inmutable para el rol Super Administrador (SA)');
      return;
    }
    setPermisosState((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleSelectAllGroup = (items: { key: string }[], select: boolean) => {
    setPermisosState((prev) => {
      const updated = { ...prev };
      items.forEach((item) => {
        if (!(isSARole && SA_LOCKED_KEYS.includes(item.key))) {
          updated[item.key] = select;
        }
      });
      return updated;
    });
  };

  const handleSavePermisos = async () => {
    if (!selectedRoleId || !currentRole) return;
    setSaving(true);
    try {
      const res = await fetch(`/api/v1/roles/${selectedRoleId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ permisos: permisosState }),
      });
      if (!res.ok) throw new Error('Error al actualizar permisos en backend');

      const updatedRol = await res.json();
      setRoles((prev) =>
        prev.map((r) => (r.id === selectedRoleId ? { ...r, permisos: updatedRol.permisos } : r))
      );

      // Notificar al contexto para estabilización reactiva
      updateRolePermissions(currentRole.nombre, permisosState);

      toast.success(`Permisos actualizados para el rol "${currentRole.nombre}"`);
    } catch (err) {
      toast.error('No fue posible guardar los permisos');
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={`roles-sidebar-overlay ${isOpen ? 'active' : ''}`} onClick={onClose}>
      <aside 
        className="roles-sidebar-drawer" 
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="Panel de Administración de Roles y Permisos"
      >
        {/* Cabecera */}
        <div className="roles-sidebar-header">
          <div className="header-icon-box">
            <Shield size={20} className="text-primary" />
          </div>
          <div className="header-title-box">
            <h3 className="header-title">Gobernanza de Roles y Permisos</h3>
            <p className="header-subtitle">Estabilización dinámica de accesos sin reinicio</p>
          </div>
          <button type="button" className="btn-close-sidebar" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Contenido */}
        <div className="roles-sidebar-content">
          {loading ? (
            <div className="roles-loading-state">
              <Loader2 size={32} className="spin text-primary" />
              <span>Cargando matriz de permisos...</span>
            </div>
          ) : (
            <>
              {/* Selector de Rol */}
              <div className="roles-selector-section">
                <label className="section-label">Selecciona el Rol a Configurar:</label>
                <div className="roles-pill-list">
                  {roles.map((rol) => {
                    const isSelected = rol.id === selectedRoleId;
                    const usersCount = usuarios.filter((u) => 
                      u.roles?.some((r) => (typeof r === 'string' ? r : r.nombre) === rol.nombre)
                    ).length;

                    return (
                      <button
                        key={rol.id}
                        type="button"
                        className={`role-pill-item ${isSelected ? 'active' : ''}`}
                        onClick={() => handleSelectRole(rol)}
                      >
                        <span className="role-pill-name">{rol.nombre}</span>
                        <span className="role-pill-badge" title={`${usersCount} colaboradores con este rol`}>
                          <Users size={11} /> {usersCount}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Matriz de Permisos por Grupo */}
              <div className="permissions-matrix-section">
                {PERMISSION_GROUPS.map((group) => {
                  const allActive = group.items.every((item) => permisosState[item.key]);
                  return (
                    <div key={group.category} className="permission-group-card">
                      <div className="group-header">
                        <div className="group-title-box">
                          {group.icon}
                          <span className="group-title">{group.category}</span>
                        </div>
                        <button
                          type="button"
                          className="btn-group-toggle-all"
                          onClick={() => handleSelectAllGroup(group.items, !allActive)}
                        >
                          {allActive ? 'Desmarcar todos' : 'Marcar todos'}
                        </button>
                      </div>

                      <div className="group-items-list">
                        {group.items.map((item) => {
                          const isChecked = Boolean(permisosState[item.key]);
                          const isLocked = isSARole && SA_LOCKED_KEYS.includes(item.key);

                          return (
                            <div
                              key={item.key}
                              className={`permission-item-row ${isChecked ? 'checked' : ''} ${isLocked ? 'locked' : ''}`}
                              onClick={() => handleTogglePermission(item.key)}
                            >
                              <div className="item-checkbox-box">
                                {isLocked ? (
                                  <Lock size={16} className="text-warning" />
                                ) : isChecked ? (
                                  <CheckSquare size={17} className="text-primary" />
                                ) : (
                                  <Square size={17} className="text-muted" />
                                )}
                              </div>
                              <div className="item-info-box">
                                <span className="item-label">{item.label}</span>
                                <p className="item-description">{item.description}</p>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Footer de Acciones */}
        <div className="roles-sidebar-footer">
          <button type="button" className="btn-cancel-sidebar" onClick={onClose} disabled={saving}>
            Cerrar
          </button>
          <button
            type="button"
            className="btn-save-sidebar"
            onClick={handleSavePermisos}
            disabled={saving || loading}
          >
            {saving ? (
              <>
                <Loader2 size={16} className="spin" />
                <span>Guardando cambios...</span>
              </>
            ) : (
              <>
                <Save size={16} />
                <span>Guardar Permisos</span>
              </>
            )}
          </button>
        </div>
      </aside>
    </div>
  );
};
```

---

## 5. Estilos Canónicos (`RolesAdminSidebar.css`)

```css
.roles-sidebar-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  z-index: 1050;
  display: flex;
  justify-content: flex-end;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}

.roles-sidebar-overlay.active {
  opacity: 1;
  pointer-events: auto;
}

.roles-sidebar-drawer {
  width: 100%;
  max-width: 540px;
  height: 100vh;
  background-color: var(--color-bg-surface, #1E293B);
  border-left: 1px solid var(--color-border-subtle, #334155);
  box-shadow: -8px 0 24px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.roles-sidebar-overlay.active .roles-sidebar-drawer {
  transform: translateX(0);
}

.roles-sidebar-header {
  padding: 18px 24px;
  border-bottom: 1px solid var(--color-border-subtle, #334155);
  display: flex;
  align-items: center;
  gap: 14px;
  background-color: var(--color-bg-base, #0F172A);
}

.header-icon-box {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-md, 8px);
  background-color: rgba(45, 106, 79, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title-box {
  flex: 1;
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary, #F8FAFC);
  margin: 0;
}

.header-subtitle {
  font-size: 12px;
  color: var(--color-text-secondary, #94A3B8);
  margin: 2px 0 0;
}

.btn-close-sidebar {
  background: transparent;
  border: none;
  color: var(--color-text-secondary, #94A3B8);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: background 0.15s;
}

.btn-close-sidebar:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.roles-sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.roles-pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.role-pill-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  border-radius: 20px;
  background-color: var(--color-bg-base, #0F172A);
  border: 1px solid var(--color-border-subtle, #334155);
  color: var(--color-text-secondary, #94A3B8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.role-pill-item.active {
  background-color: rgba(45, 106, 79, 0.2);
  border-color: var(--color-primary, #2D6A4F);
  color: var(--color-primary-light, #52B788);
  font-weight: 600;
}

.permission-group-card {
  border: 1px solid var(--color-border-subtle, #334155);
  border-radius: var(--border-radius-md, 8px);
  background-color: var(--color-bg-base, #0F172A);
  overflow: hidden;
}

.group-header {
  padding: 10px 14px;
  background-color: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid var(--color-border-subtle, #334155);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-title-box {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 13px;
  color: var(--color-text-primary, #F8FAFC);
}

.btn-group-toggle-all {
  background: transparent;
  border: none;
  font-size: 11px;
  color: var(--color-primary-light, #52B788);
  cursor: pointer;
  text-decoration: underline;
}

.permission-item-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: background 0.15s;
}

.permission-item-row:last-child {
  border-bottom: none;
}

.permission-item-row:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.permission-item-row.checked {
  background-color: rgba(45, 106, 79, 0.05);
}

.item-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary, #F8FAFC);
  display: block;
}

.item-description {
  font-size: 11.5px;
  color: var(--color-text-secondary, #94A3B8);
  margin: 2px 0 0;
}

.roles-sidebar-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--color-border-subtle, #334155);
  background-color: var(--color-bg-base, #0F172A);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel-sidebar {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid var(--color-border-subtle, #334155);
  background: transparent;
  color: var(--color-text-secondary, #94A3B8);
  cursor: pointer;
}

.btn-save-sidebar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border-radius: 6px;
  border: none;
  background-color: var(--color-primary, #2D6A4F);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-save-sidebar:hover:not(:disabled) {
  background-color: var(--color-primary-dark, #1B4332);
}
```
