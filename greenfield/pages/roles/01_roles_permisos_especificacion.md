# Especificación Funcional y Técnica: Matriz de Roles y Permisos (RBAC)
## Joli Foods — Control de Acceso por Módulo

Interfaz y contratos para administrar roles y asignar permisos por módulo. Modelo: [`../../../model/roles/spec_model_roles_permisos.md`](../../../model/roles/spec_model_roles_permisos.md) (BP-19).

---

## 1. Requisitos

1. **Listado de roles** (tabla `Rol`) con número de usuarios vinculados. Los roles son datos, no código: se crean y editan sin desplegar.
2. **Matriz de permisos:** por cada módulo del catálogo (`backend/config/permisos.py`) se marcan las acciones `ver`, `crear`, `editar`, `eliminar`, `exportar`. Cada casilla corresponde a una clave `modulo.accion` guardada en `Rol.permisos`.
3. **Coherencia:** marcar `crear`, `editar`, `eliminar` o `exportar` activa `ver` automáticamente (no tiene sentido editar lo que no se puede ver).
4. **Roles de sistema** (`es_sistema = true`) no se editan desde la interfaz. **Por qué:** evita quitarle por error los permisos al único rol administrador y bloquear el sistema.
5. **Permisos de la pantalla:** `roles.ver` para consultar, `roles.editar` para guardar.
6. **Bitácora:** cada guardado registra `ROLE_PERMISSIONS_UPDATED` con permisos antes y después.
7. **Efecto inmediato:** los usuarios afectados reciben los permisos nuevos en su siguiente consulta a `GET /api/v1/mis-permisos/`, sin cerrar sesión.

---

## 2. Contrato de API

| Método y ruta | Descripción |
| :--- | :--- |
| `GET /api/v1/roles/` (`ENDPOINTS.ROLES.LISTA`) | `[{ "id": 2, "codigo": "OPERADOR", "nombre": "Operador", "es_sistema": false, "usuarios_count": 14 }]` (conteo con `annotate(Count("usuarios"))`, sin N+1). |
| `GET /api/v1/roles/matriz-permisos/` (`ENDPOINTS.ROLES.MATRIZ_RBAC`) | Catálogo de módulos y acciones: `[{ "modulo": "usuarios", "nombre": "Gestión de usuarios", "acciones": ["ver","crear","editar","eliminar","exportar"] }]`. |
| `GET /api/v1/roles/{id}/` | Rol con `permisos: ["usuarios.ver", "usuarios.editar", ...]`. |
| `PATCH /api/v1/roles/{id}/` | `{ "permisos": ["usuarios.ver", "auditoria.ver", "auditoria.exportar"] }`. 400 si hay claves fuera del catálogo; 403 si el rol es de sistema. |

---

## 3. Vista (`RolesPage.tsx`)

```tsx
import { useEffect, useMemo, useState } from 'react';
import { Shield, Save, AlertTriangle } from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { ENDPOINTS } from '../services/endpoints';
import { useAuth } from '../context/AuthContext';
import { showToast } from '../components/ToastNotification';
import { ConfirmModal } from '../components/modal/ConfirmModal';

const ACCIONES = ['ver', 'crear', 'editar', 'eliminar', 'exportar'] as const;
type Accion = (typeof ACCIONES)[number];

interface RolItem { id: number; codigo: string; nombre: string; es_sistema: boolean; usuarios_count: number }
interface ModuloCatalogo { modulo: string; nombre: string; acciones: Accion[] }
interface RolDetalle extends RolItem { permisos: string[] }

export function RolesPage() {
  const { hasPermission } = useAuth();
  const puedeEditar = hasPermission('roles.editar');
  const [roles, setRoles] = useState<RolItem[]>([]);
  const [catalogo, setCatalogo] = useState<ModuloCatalogo[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [rol, setRol] = useState<RolDetalle | null>(null);
  const [permisos, setPermisos] = useState<Set<string>>(new Set());
  const [isSaving, setIsSaving] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  // Roles y catálogo
  useEffect(() => {
    const controller = new AbortController();
    const { signal } = controller;
    Promise.all([
      apiClient.get<RolItem[]>(ENDPOINTS.ROLES.LISTA, { signal }),
      apiClient.get<ModuloCatalogo[]>(ENDPOINTS.ROLES.MATRIZ_RBAC, { signal }),
    ])
      .then(([r, c]) => {
        setRoles(r.data);
        setCatalogo(c.data);
        setSelectedId((prev) => prev ?? r.data[0]?.id ?? null);
      })
      .catch(() => { if (!signal.aborted) showToast.error('No fue posible cargar los roles.'); });
    return () => controller.abort();
  }, []);

  // Detalle del rol seleccionado
  useEffect(() => {
    if (selectedId === null) return;
    const controller = new AbortController();
    apiClient
      .get<RolDetalle>(`${ENDPOINTS.ROLES.LISTA}${selectedId}/`, { signal: controller.signal })
      .then(({ data }) => { setRol(data); setPermisos(new Set(data.permisos)); })
      .catch(() => { if (!controller.signal.aborted) showToast.error('No fue posible cargar el rol.'); });
    return () => controller.abort();
  }, [selectedId]);

  const bloqueado = !puedeEditar || Boolean(rol?.es_sistema);
  const cambios = useMemo(
    () => rol !== null && (rol.permisos.length !== permisos.size || rol.permisos.some((p) => !permisos.has(p))),
    [rol, permisos]
  );

  const alternar = (modulo: string, accion: Accion) => {
    if (bloqueado) return;
    setPermisos((prev) => {
      const next = new Set(prev);
      const clave = `${modulo}.${accion}`;
      if (next.has(clave)) {
        next.delete(clave);
        if (accion === 'ver') ACCIONES.forEach((a) => next.delete(`${modulo}.${a}`)); // sin "ver" no hay otras
      } else {
        next.add(clave);
        if (accion !== 'ver') next.add(`${modulo}.ver`);
      }
      return next;
    });
  };

  const guardar = async () => {
    if (!rol) return;
    setIsSaving(true);
    try {
      const { data } = await apiClient.patch<RolDetalle>(`${ENDPOINTS.ROLES.LISTA}${rol.id}/`, { permisos: [...permisos].sort() });
      setRol(data);
      setPermisos(new Set(data.permisos));
      showToast.success('Permisos actualizados', { description: `Rol ${data.nombre}.` });
    } catch {
      showToast.error('No fue posible guardar los permisos.');
    } finally {
      setIsSaving(false);
      setIsConfirmOpen(false);
    }
  };

  return (
    <div className="joli-page-container w-100">
      <div className="mb-4">
        <h1 className="joli-page-title">Roles y permisos</h1>
        <p className="text-muted small mb-0">Define qué puede hacer cada rol en cada módulo.</p>
      </div>

      <div className="row g-4">
        <div className="col-12 col-lg-3">
          <section className="joli-panel-card p-3" aria-labelledby="roles-lista">
            <h2 id="roles-lista" className="h6 fw-bold mb-3 d-flex align-items-center gap-2">
              <Shield size={18} aria-hidden="true" /><span>Roles</span>
            </h2>
            <div className="list-group">
              {roles.map((r) => (
                <button key={r.id} type="button" aria-current={selectedId === r.id ? 'true' : undefined}
                        className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center ${selectedId === r.id ? 'active' : ''}`}
                        onClick={() => setSelectedId(r.id)}>
                  <span>
                    <span className="d-block fw-semibold">{r.nombre}</span>
                    <small className="font-monospace">{r.codigo}</small>
                  </span>
                  <span className="badge text-bg-secondary rounded-pill">{r.usuarios_count}</span>
                </button>
              ))}
            </div>
          </section>
        </div>

        <div className="col-12 col-lg-9">
          <section className="joli-panel-card p-4" aria-labelledby="roles-matriz">
            <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
              <div>
                <h2 id="roles-matriz" className="h5 fw-bold mb-0">Permisos: {rol?.nombre ?? '—'}</h2>
                {rol?.es_sistema && (
                  <small className="d-flex align-items-center gap-1 mt-1">
                    <AlertTriangle size={13} aria-hidden="true" /><span>Rol de sistema: sus permisos no se editan desde aquí.</span>
                  </small>
                )}
              </div>
              {!bloqueado && (
                <button type="button" className="btn btn-primary d-inline-flex align-items-center gap-2"
                        onClick={() => setIsConfirmOpen(true)} disabled={isSaving || !cambios}>
                  <Save size={16} aria-hidden="true" /><span>Guardar matriz</span>
                </button>
              )}
            </div>

            <div className="table-responsive">
              <table className="table joli-table">
                <thead>
                  <tr>
                    <th scope="col">Módulo</th>
                    {ACCIONES.map((a) => <th key={a} scope="col" className="text-center text-capitalize">{a}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {catalogo.map((m) => (
                    <tr key={m.modulo}>
                      <th scope="row" className="fw-semibold">{m.nombre}</th>
                      {ACCIONES.map((a) => (
                        <td key={a} className="text-center">
                          {m.acciones.includes(a) ? (
                            <input type="checkbox" className="form-check-input"
                                   checked={permisos.has(`${m.modulo}.${a}`)} disabled={bloqueado}
                                   aria-label={`${m.nombre}: ${a}`} onChange={() => alternar(m.modulo, a)} />
                          ) : <span aria-hidden="true">—</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>

      <ConfirmModal
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={guardar}
        type="warning"
        isLoading={isSaving}
        title="¿Confirmar actualización de permisos?"
        message={`Los usuarios con el rol ${rol?.nombre ?? ''} recibirán los nuevos permisos en su siguiente acción.`}
        confirmText="Aplicar permisos"
      />
    </div>
  );
}
```
