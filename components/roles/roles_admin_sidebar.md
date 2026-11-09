# Especificación de Componente: Panel Lateral de Administración de Roles y Permisos (`RolesAdminSidebar`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de tiendita (administración de roles y permisos). Aquí se describe de forma genérica.

`RolesAdminSidebar` es un panel lateral derecho (*Right Drawer*) para que los administradores gestionen los roles de la plataforma y sus permisos sin reiniciar el servidor ni crear migraciones. Se monta sobre el componente canónico [`Drawer`](../drawer/drawer.md) (ancho `lg` / 720px), por lo que hereda su cabecera fija, cuerpo con scroll, pie fijo, cierre con `Escape` y manejo de foco.

---

## 0. Implementación de referencia (Pandora, «Definición de roles»)

> Patrón completo de la pantalla: [`admin_table_screen.md`](../data_table/admin_table_screen.md). Lo de esta sección manda sobre el resto del documento cuando se contradicen; lo marcado **«Deuda en la referencia»** es lo que el código aún no cumple y NO se copia.

Diseño vigente (reemplaza al del resto de este documento donde se contradicen):
- `RightDrawer size="md"`, título «Definición de roles», subtítulo «Elige qué secciones del menú puede usar cada rol». Se abre desde un botón con texto en la barra de Usuarios, solo con el permiso de sección correspondiente.
- **Selector de rol:** botonera segmentada centrada (`div.role-btn-group role="radiogroup"`, `button.role-btn role="radio" aria-checked`, 34 px, activo con `--brand-solid`). Al abrir se elige el primer rol.
- **Buscador de secciones** y barra con «**N** de M secciones permitidas» + «Colapsar todo» / «Expandir todo».
- **Catálogo desde el backend** (secciones del menú), agrupado por categoría y subgrupo en acordeones accesibles (`role="button" tabIndex=0 aria-expanded`, `Enter` y espacio), con contador «x/y» y «Activar todos» / «Quitar todos». Si una categoría tiene una sola sección, no lleva acordeón.
- **Cada sección** es una fila con texto y descripción y un `ToggleSwitch size="sm"`; clic en la fila también cambia el permiso.
- **Guardado automático en cola:** el cambio se ve al instante, se envía el estado completo del rol y los cambios se procesan en orden. El pie muestra el estado (`role="status"`): «Los cambios se guardan al instante» / «Guardando…» / «Cambios guardados» / «No se guardó el último cambio», y un botón «Cerrar». Si falla, toast de error y se vuelve a lo que tiene el servidor. Al guardar se emite el evento `<app>:permisos-actualizados` para refrescar el menú.
- Las secciones protegidas (administración) las protege el **backend** (BP-19), no una lista fija en el frontend.
- Sondeo de 30 s mientras está abierto, sin consultar si hay guardados pendientes. Primera carga con esqueleto.

---

## 1. Principio de arquitectura: permisos como datos

Los roles y permisos se modelan como **datos administrables**, no como código.

- Los roles NO DEBERÍAN definirse como `Enum` ni como listas quemadas en frontend o backend.
  - **Por qué:** cada rol nuevo obligaría a desplegar código; como datos, el administrador lo crea desde la interfaz.
- Modelo recomendado:
  1. Tabla de **roles** con un campo `JSONField` `permisos` (banderas booleanas por clave de permiso).
  2. Relación **muchos a muchos** (`ManyToManyField`) entre usuarios y roles.
  3. El backend combina los permisos de todos los roles del usuario (basta un rol con la bandera en `true`) y los entrega como lista de claves en la respuesta de `ENDPOINTS.AUTH.ME` (`user.permisos: string[]`).
- **Seguridad (DEBE):** la autorización real se hace en el backend en cada endpoint. El panel solo edita configuración; el servidor DEBE:
  - exigir permiso de administración para `PATCH` de roles;
  - rechazar claves de permiso desconocidas (validar contra el catálogo);
  - impedir quitar los permisos bloqueados del rol super administrador (la regla del frontend es solo de UX);
  - registrar en auditoría quién cambió qué y cuándo.
- **Propagación:** el usuario que edita ve el cambio al refrescar su perfil (`AUTH.ME`). Los demás usuarios lo reciben en su siguiente renovación de sesión o consulta de perfil. Si se requiere efecto inmediato para todos, el backend DEBE validar permisos contra la base de datos en cada petición (no solo contra el token).

---

## 2. Contrato de datos (TypeScript)

```typescript
// src/types/roles.types.ts
import type { ReactNode } from 'react';

export interface PermissionItem {
  key: string;
  label: string;
  description: string;
}

export interface PermissionGroup {
  category: string;
  icon: ReactNode;
  items: PermissionItem[];
}

export interface Rol {
  id: number;
  nombre: string;
  permisos: Record<string, boolean>;
  /** Calculado en el backend con annotate(Count('usuarios')): evita descargar todos los usuarios. */
  usuarios_count: number;
}
```

---

## 3. Catálogo de permisos del sistema

Las claves DEBEN coincidir con el catálogo del backend. Al usar JSX, el archivo es `.tsx`.

```tsx
// src/config/permissionGroups.tsx
import { Bell, Package, FileText, Users } from 'lucide-react';
import type { PermissionGroup } from '@/types/roles.types';

export const PERMISSION_GROUPS: PermissionGroup[] = [
  {
    category: 'Acceso general e interfaz',
    icon: <Bell size={16} aria-hidden="true" />,
    items: [
      { key: 'ver_administracion_home', label: 'Ver botón "Administración" en inicio', description: 'Muestra el acceso al panel de administración.' },
      { key: 'ver_notificaciones_topheader', label: 'Ver notificaciones en el TopHeader', description: 'Muestra la campana de alertas en la barra superior.' },
      { key: 'ver_admin_roles_button', label: 'Ver botón "Administración de roles"', description: 'Permite abrir este panel.' },
    ],
  },
  {
    category: 'Módulos operativos',
    icon: <Package size={16} aria-hidden="true" />,
    items: [
      { key: 'modulo_operaciones_crear', label: 'Crear registros', description: 'Habilita formularios de captura.' },
      { key: 'modulo_operaciones_editar', label: 'Editar registros', description: 'Permite modificar registros desde el panel lateral.' },
      { key: 'modulo_operaciones_anular', label: 'Anular registros', description: 'Permite anular exigiendo motivo en ConfirmModal.' },
    ],
  },
  {
    category: 'Informes y actas',
    icon: <FileText size={16} aria-hidden="true" />,
    items: [
      { key: 'informes_generales', label: 'Consultar y exportar informes', description: 'Reportes históricos y exportación a Excel y PDF.' },
    ],
  },
  {
    category: 'Administración global',
    icon: <Users size={16} aria-hidden="true" />,
    items: [
      { key: 'admin_colaboradores', label: 'Administrar usuarios y cuentas', description: 'Perfiles, activación/desactivación y asignación de roles.' },
    ],
  },
];

/** Permisos que el rol super administrador no puede perder (el backend aplica la misma regla). */
export const SUPERADMIN_ROLE_NAME = 'SA';
export const SUPERADMIN_LOCKED_KEYS = ['ver_administracion_home', 'ver_admin_roles_button', 'admin_colaboradores'];
```

---

## 4. Implementación (`RolesAdminSidebar.tsx`)

```tsx
import React, { useCallback, useEffect, useState } from 'react';
import { Users, Save, Loader2, Lock } from 'lucide-react';
import { Drawer } from '@/components/ui/Drawer';
import { showToast } from '@/components/ui/ToastNotification';
import { api } from '@services/api';
import { ENDPOINTS } from '@services/endpoints';
import { PERMISSION_GROUPS, SUPERADMIN_ROLE_NAME, SUPERADMIN_LOCKED_KEYS } from '@/config/permissionGroups';
import type { Rol } from '@/types/roles.types';
import './RolesAdminSidebar.css';

interface RolesAdminSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  /** Se llama tras guardar, para que el contenedor refresque el perfil del usuario actual (AUTH.ME). */
  onSaved?: (rol: Rol) => void;
}

const isSuperAdmin = (rol?: Rol) => rol?.nombre.trim().toUpperCase() === SUPERADMIN_ROLE_NAME;

function buildPermisosState(rol: Rol): Record<string, boolean> {
  const state: Record<string, boolean> = {};
  for (const group of PERMISSION_GROUPS) {
    for (const item of group.items) {
      state[item.key] =
        (isSuperAdmin(rol) && SUPERADMIN_LOCKED_KEYS.includes(item.key)) || Boolean(rol.permisos?.[item.key]);
    }
  }
  return state;
}

export const RolesAdminSidebar: React.FC<RolesAdminSidebarProps> = ({ isOpen, onClose, onSaved }) => {
  const [roles, setRoles] = useState<Rol[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [permisosState, setPermisosState] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const currentRole = roles.find((r) => r.id === selectedRoleId);
  const lockedForCurrent = (key: string) => isSuperAdmin(currentRole) && SUPERADMIN_LOCKED_KEYS.includes(key);

  const selectRole = useCallback((rol: Rol) => {
    setSelectedRoleId(rol.id);
    setPermisosState(buildPermisosState(rol));
  }, []);

  // Carga al abrir, cancelable si el panel se cierra antes de responder.
  useEffect(() => {
    if (!isOpen) return;
    const controller = new AbortController();
    setLoading(true);
    api
      .get<Rol[]>(ENDPOINTS.ROLES.LISTA, { signal: controller.signal })
      .then((res) => {
        setRoles(res.data);
        if (res.data.length > 0) selectRole(res.data[0]);
      })
      .catch(() => {
        if (!controller.signal.aborted) showToast.error('Error al cargar la configuración de roles');
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [isOpen, selectRole]);

  const togglePermission = (key: string) => {
    if (lockedForCurrent(key)) return;
    setPermisosState((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const setGroup = (keys: string[], value: boolean) => {
    setPermisosState((prev) => {
      const next = { ...prev };
      for (const key of keys) if (!lockedForCurrent(key)) next[key] = value;
      return next;
    });
  };

  const handleSave = async () => {
    if (!currentRole) return;
    setSaving(true);
    try {
      // Agregar ROLES.DETALLE(id) al catálogo de endpoints (frontend y endpoints_registry.json).
      const res = await api.patch<Rol>(ENDPOINTS.ROLES.DETALLE(currentRole.id), { permisos: permisosState });
      setRoles((prev) => prev.map((r) => (r.id === res.data.id ? res.data : r)));
      showToast.success(`Permisos actualizados para el rol "${res.data.nombre}"`);
      onSaved?.(res.data);
    } catch {
      showToast.error('No fue posible guardar los permisos');
    } finally {
      setSaving(false);
    }
  };

  const footer = (
    <>
      <button type="button" className="btn btn-outline-secondary" onClick={onClose} disabled={saving}>
        Cancelar
      </button>
      <button type="button" className="btn btn-primary roles-btn-save" onClick={handleSave} disabled={saving || loading || !currentRole}>
        {saving ? <Loader2 size={16} className="spin" aria-hidden="true" /> : <Save size={16} aria-hidden="true" />}
        <span>{saving ? 'Guardando…' : 'Guardar permisos'}</span>
      </button>
    </>
  );

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title="Roles y permisos"
      subtitle="Los cambios aplican sin reiniciar el servidor"
      size="lg"
      footer={footer}
    >
      {loading ? (
        <div className="roles-loading-state" role="status">
          <Loader2 size={28} className="spin" aria-hidden="true" />
          <span>Cargando matriz de permisos…</span>
        </div>
      ) : (
        <>
          {/* Selector de rol */}
          <section className="roles-selector-section" aria-labelledby="roles-selector-title">
            <h6 id="roles-selector-title" className="roles-section-label">Rol a configurar</h6>
            <div className="roles-pill-list" role="radiogroup" aria-labelledby="roles-selector-title">
              {roles.map((rol) => {
                const selected = rol.id === selectedRoleId;
                return (
                  <button
                    key={rol.id}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    className={`role-pill-item ${selected ? 'active' : ''}`}
                    onClick={() => selectRole(rol)}
                  >
                    <span className="role-pill-name">{rol.nombre}</span>
                    <span className="role-pill-badge" title={`${rol.usuarios_count} usuarios con este rol`}>
                      <Users size={11} aria-hidden="true" /> {rol.usuarios_count}
                    </span>
                  </button>
                );
              })}
            </div>
          </section>

          {/* Matriz de permisos por grupo: checkboxes nativos => teclado y lector de pantalla */}
          {PERMISSION_GROUPS.map((group) => {
            const keys = group.items.map((i) => i.key);
            const allActive = keys.every((k) => permisosState[k]);
            return (
              <fieldset key={group.category} className="permission-group-card">
                <legend className="group-header">
                  <span className="group-title-box">
                    {group.icon}
                    <span>{group.category}</span>
                  </span>
                  <button type="button" className="btn-group-toggle-all" onClick={() => setGroup(keys, !allActive)}>
                    {allActive ? 'Desmarcar todos' : 'Marcar todos'}
                  </button>
                </legend>

                {group.items.map((item) => {
                  const locked = lockedForCurrent(item.key);
                  const inputId = `perm-${item.key}`;
                  return (
                    <label key={item.key} htmlFor={inputId} className={`permission-item-row ${locked ? 'locked' : ''}`}>
                      <input
                        id={inputId}
                        type="checkbox"
                        className="form-check-input"
                        checked={Boolean(permisosState[item.key])}
                        disabled={locked}
                        onChange={() => togglePermission(item.key)}
                        aria-describedby={`${inputId}-desc`}
                      />
                      <span className="item-info-box">
                        <span className="item-label">
                          {item.label}
                          {locked && (
                            <span className="item-locked-tag" title="Permiso obligatorio del super administrador">
                              <Lock size={12} aria-hidden="true" /> Obligatorio
                            </span>
                          )}
                        </span>
                        <span id={`${inputId}-desc`} className="item-description">{item.description}</span>
                      </span>
                    </label>
                  );
                })}
              </fieldset>
            );
          })}
        </>
      )}
    </Drawer>
  );
};
```

---

## 5. Estilos (`RolesAdminSidebar.css`)

El contenedor, la cabecera, el overlay y el pie los aporta `Drawer`. Aquí solo va el contenido, con tokens de `variables.css`.

```css
.roles-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-8) 0;
  color: var(--text-muted);
}

.roles-section-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--label-color);
  margin: 0 0 var(--space-2);
}

.roles-pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}

.role-pill-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 7px 14px;
  border-radius: var(--radius-full);
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
}

.role-pill-item:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.role-pill-item.active {
  background-color: var(--status-success-bg);
  border-color: var(--brand-primary);
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
}

.role-pill-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: var(--font-size-2xs);
  color: var(--text-muted);
}

.permission-group-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background-color: var(--bg-card);
  margin: 0 0 var(--space-4);
  padding: 0;
  overflow: hidden;
}

.group-header {
  float: left; /* hace que el <legend> ocupe el ancho como una cabecera */
  width: 100%;
  padding: 10px 14px;
  margin: 0;
  background-color: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-header + * {
  clear: both;
}

.group-title-box {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: var(--font-weight-semibold);
  font-size: 13px;
  color: var(--text-primary);
}

.btn-group-toggle-all {
  background: transparent;
  border: none;
  font-size: var(--font-size-2xs);
  color: var(--brand-primary);
  cursor: pointer;
  text-decoration: underline;
}

.permission-item-row {
  clear: both;
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.permission-item-row:last-child {
  border-bottom: none;
}

.permission-item-row:hover {
  background-color: var(--bg-hover);
}

.permission-item-row.locked {
  cursor: not-allowed;
}

.item-info-box {
  display: flex;
  flex-direction: column;
}

.item-label {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 13px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.item-locked-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: var(--font-size-2xs);
  font-weight: var(--font-weight-bold);
  color: var(--status-warning);
}

.item-description {
  font-size: 11.5px;
  color: var(--text-muted);
  margin-top: 2px;
}

.roles-btn-save {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}
```
