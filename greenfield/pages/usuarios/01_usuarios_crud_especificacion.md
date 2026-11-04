# 01. Especificación del Módulo de Gestión de Usuarios (CRUD)
## Joli Foods — Spec-Driven Development (SDD)

Pantalla administrativa para listar, crear, editar, asignar roles y suspender usuarios. Paginación en servidor, consultas sin N+1 y validación con Zod en el cliente.

> **Origen:** patrón tomado de tiendita (gestión de roles y permisos). Aquí se describe de forma genérica.

> [!IMPORTANT]
> **REGLAS DE INTERFAZ Y BOTONERAS EN GESTIÓN DE USUARIOS (PANDORA ADMIN)**:
> 1. **Botonera Agrupada de los Tres (`.view-switcher`: Tabla + Cards + Buscar — Solo Iconos)**:
>    En el extremo izquierdo del toolbar se ubica la botonera segmentada de **tres iconos sin texto**:
>    - **Tabla** (`Table2`): Activa la vista tabular `.joli-data-table`.
>    - **Cards** (`LayoutGrid`): Activa la cuadrícula de tarjetas `.users-cards-grid` / `.user-profile-card`.
>    - **Buscar** (`Search`): Al hacer clic en el icono de lupa, anima horizontalmente hacia la derecha el contenedor `.switcher-search-expanded` desplegando el `<input class="switcher-search-input">` de búsqueda en tiempo real.
> 2. **Grupo de Filtros Expandibles (`.expandable-filter-group`)**: A continuación de la botonera de los tres se ubica el grupo de filtros para `Rol` y `Estado`, que también se despliegan horizontalmente en línea al seleccionarlos, junto al botón dinámico `FilterX` para limpiar filtros.
> 3. **Diseño de Botoneras de Acciones de Solo Iconos (Cero Texto)**:
>    - **Botonera de Acciones del Toolbar (`.compact-action-box`)**: Botonera segmentada con solo los iconos `UserPlus` (Nuevo Usuario) y `RotateCcw` (Recargar), separados por `.compact-divider`, sin texto.
>    - **Botonera de Acciones en Filas y Cards (`.row-actions-group`)**: Botonera segmentada con solo los iconos `Edit2` (Editar) y `Power` (Activar/Desactivar), sin texto.
> 4. **Prohibición Estricta de Modales para Crear o Editar — Uso Obligatorio de Sidebar Derecho (`RightDrawer`)**:
>    Tanto la acción de **Agregar (Nuevo Colaborador)** como la de **Editar Colaborador** **DEBEN abrirse siempre en un Sidebar al lado derecho (`.joli-drawer-container` / `RightDrawer`)** deslizando desde el borde derecho (`translateX(100%) -> translateX(0)`), y **NUNCA** en un modal flotante centrado. En modo edición, el Sidebar Derecho muestra una fila superior de Mini-KPIs contextuales (`.drawer-kpi-grid`: Documento, Rol Actual y Último Acceso).
> 5. **Paginador Superior Integrado en Toolbar (`.joli-table-toolbar.pagination-container` — SDD `pagination.md`)**:
>    El paginador **NUNCA se ubica al pie de la tabla**. Se ubica **ARRIBA DE LA TABLA**, integrado directamente en la barra superior junto a la botonera de acciones, mostrando el selector de tamaño de página (`Mostrar [10 | 20 | 50 | 100]`), el resumen numérico (`Mostrando X a Y de Z Colaboradores`) y los controles de navegación (`<<`, `<`, números de página con elipsis, `>`, `>>`).
> 6. **Card Contenedora hasta Abajo de la Pantalla (`.joli-table-card` — SDD `data_table.md`)**:
>    La tarjeta principal de la tabla utiliza `flex: 1; min-height: 420px; display: flex; flex-direction: column; overflow: hidden;` dentro de un layout de altura completa (`height: 100vh; overflow: hidden;`), garantizando que el contenedor llegue hasta el borde inferior visible de la pantalla sin dejar huecos vacíos, mientras `.joli-table-wrapper` administra el scroll interno (`flex: 1; overflow: auto;`).

---

## 1. Modelo y Permisos

### 1.1. Modelo canónico
El modelo `Usuario` (`AbstractBaseUser` + `PermissionsMixin`, `USERNAME_FIELD = 'numero_documento'`) y el modelo `Rol` **no se redefinen aquí**: se usan los de [`../../../model/login/implementacion_django_orm.md`](../../../model/login/implementacion_django_orm.md) y [`../../../model/roles/spec_model_roles_permisos.md`](../../../model/roles/spec_model_roles_permisos.md). **Por qué:** dos definiciones del mismo modelo terminan divergiendo en campos y migraciones.

### 1.2. Roles y permisos (BP-19)
- Los roles viven en la tabla `Rol` y se asignan por M2M (`Usuario.roles`). Un usuario PUEDE tener varios roles; sus permisos efectivos son la unión.
- `Rol.permisos` es una lista de claves `modulo.accion` (p. ej. `["usuarios.ver", "usuarios.editar"]`).
- La UI y el backend autorizan por clave de permiso, nunca por nombre de rol. Este módulo requiere `usuarios.ver` para listar, `usuarios.crear`, `usuarios.editar` y `usuarios.eliminar` (suspender) para las acciones.
- `GET /api/v1/mis-permisos/` devuelve los permisos del usuario autenticado (ver implementación en el modelo de roles).

### 1.3. Listado paginado sin N+1
- **Ruta:** `GET /api/v1/usuarios/?page=1&page_size=10&search=&rol_id=&is_active=`
```python
# backend/apps/usuarios/queries.py
from django.core.paginator import Paginator
from django.db.models import Q

from apps.auth_core.models import Usuario

PAGE_SIZE_MAX = 100


def obtener_usuarios_paginados(page: int = 1, page_size: int = 10, search: str = "",
                               rol_id: int | None = None, is_active: bool | None = None):
    page_size = max(1, min(page_size, PAGE_SIZE_MAX))
    queryset = (
        Usuario.objects.select_related("sede")
        .prefetch_related("roles")  # M2M en una sola consulta adicional
        .only("id", "numero_documento", "first_name", "last_name", "email", "cargo",
              "is_active", "last_login", "sede__nombre")
    )
    if search:
        queryset = queryset.filter(
            Q(numero_documento__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(cargo__icontains=search)
        )
    if rol_id:
        queryset = queryset.filter(roles__id=rol_id).distinct()
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    return Paginator(queryset.order_by("first_name", "last_name", "id"), page_size).get_page(page)
```

### 1.4. Suspender / reactivar
- **Ruta:** `PATCH /api/v1/usuarios/{id}/toggle-status/` (`ENDPOINTS.USUARIOS.TOGGLE_STATUS`).
- **Permiso:** `usuarios.eliminar`. Un usuario NO DEBE poder suspenderse a sí mismo ni suspender al último usuario con rol `es_sistema`.
- Al suspender (`is_active = False`), en una misma `transaction.atomic()` (BP-12): se ponen en lista negra todos sus refresh tokens, se cierran sus `SesionUsuario` y se registra el evento en la bitácora con la justificación del `ConfirmModal`.
- Al reactivar: solo cambia `is_active`; el usuario DEBE iniciar sesión de nuevo.

### 1.5. Restablecer contraseña de otro usuario
- **Ruta:** `POST /api/v1/usuarios/{id}/password-reset/` (permiso `usuarios.editar`).
- Reutiliza el flujo de [`../login/09_flujo_restablecimiento_contrasena.md`](../login/09_flujo_restablecimiento_contrasena.md): se envía un enlace de un solo uso al correo del usuario. El administrador NUNCA ve ni define la contraseña.

---

## 2. Vista (`UsuariosPage.tsx`)

Composición: tabla [`DataTable`](../../../components/data_table/data_table.md) a todo lo ancho con paginador arriba, creación/edición en [`Drawer`](../../../components/drawer/drawer.md) derecho, confirmaciones con [`ConfirmModal`](../../../components/modal/confirm_modal.md) y gobierno de roles en [`RolesAdminSidebar`](../../../components/roles/roles_admin_sidebar.md). Estas convenciones son DEBERÍA (ver `AGENTS.md` del entorno); se pueden cambiar con un ADR o pedido explícito del usuario.

```tsx
import { useCallback, useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { UserPlus, Edit2, KeyRound, ShieldCheck } from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { ENDPOINTS } from '../services/endpoints';
import { useAuth } from '../context/AuthContext';
import { DataTable, type ColumnDef } from '../components/data_table/DataTable';
import { Drawer } from '../components/drawer/Drawer';
import { ConfirmModal } from '../components/modal/ConfirmModal';
import { Badge } from '../components/badge/Badge';
import { ToggleSwitch } from '../components/toggle/ToggleSwitch';
import { RolesAdminSidebar } from '../components/roles/RolesAdminSidebar';
import { showToast } from '../components/ToastNotification';

interface RolItem { id: number; codigo: string; nombre: string }
interface UsuarioRow {
  id: number;
  numero_documento: string;
  nombre_completo: string;
  first_name: string;
  last_name: string;
  email: string;
  cargo: string | null;
  roles: RolItem[];
  is_active: boolean;
}
interface Paginado<T> { count: number; results: T[] }

const usuarioSchema = z.object({
  numero_documento: z.string().regex(/^[0-9]{5,15}$/, 'Entre 5 y 15 dígitos.'),
  first_name: z.string().trim().min(1, 'Obligatorio.').max(150),
  last_name: z.string().trim().min(1, 'Obligatorio.').max(150),
  email: z.string().email('Correo inválido.'),
  cargo: z.string().max(120).optional(),
  roles: z.array(z.number()).min(1, 'Asigna al menos un rol.'),
});
type UsuarioForm = z.infer<typeof usuarioSchema>;

type Confirmacion = { user: UsuarioRow; action: 'toggle_status' | 'reset_password' } | null;

export function UsuariosPage() {
  const { hasPermission } = useAuth();
  const [rows, setRows] = useState<UsuarioRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const [roles, setRoles] = useState<RolItem[]>([]);
  const [editing, setEditing] = useState<UsuarioRow | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isRolesOpen, setIsRolesOpen] = useState(false);
  const [confirmacion, setConfirmacion] = useState<Confirmacion>(null);

  const form = useForm<UsuarioForm>({
    resolver: zodResolver(usuarioSchema),
    defaultValues: { numero_documento: '', first_name: '', last_name: '', email: '', cargo: '', roles: [] },
  });

  // Carga del listado (cancelable)
  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    apiClient
      .get<Paginado<UsuarioRow>>(ENDPOINTS.USUARIOS.LISTA, {
        params: { page, page_size: pageSize, search },
        signal: controller.signal,
      })
      .then((r) => { setRows(r.data.results); setTotal(r.data.count); })
      .catch(() => { if (!controller.signal.aborted) showToast.error('No fue posible cargar los usuarios.'); })
      .finally(() => { if (!controller.signal.aborted) setIsLoading(false); });
    return () => controller.abort();
  }, [page, pageSize, search, reloadKey]);

  // Catálogo de roles (cancelable)
  useEffect(() => {
    const controller = new AbortController();
    apiClient
      .get<RolItem[]>(ENDPOINTS.ROLES.LISTA, { signal: controller.signal })
      .then((r) => setRoles(r.data))
      .catch(() => { if (!controller.signal.aborted) showToast.error('No fue posible cargar los roles.'); });
    return () => controller.abort();
  }, []);

  const abrirDrawer = useCallback((user: UsuarioRow | null) => {
    setEditing(user);
    form.reset(user
      ? { numero_documento: user.numero_documento, first_name: user.first_name, last_name: user.last_name, email: user.email,
          cargo: user.cargo ?? '', roles: user.roles.map((r) => r.id) }
      : { numero_documento: '', first_name: '', last_name: '', email: '', cargo: '', roles: [] });
    setIsDrawerOpen(true);
  }, [form]);

  const guardar = form.handleSubmit(async (values) => {
    try {
      if (editing) await apiClient.patch(ENDPOINTS.USUARIOS.DETALLE(editing.id), values);
      else await apiClient.post(ENDPOINTS.USUARIOS.LISTA, values);
      showToast.success(editing ? 'Usuario actualizado.' : 'Usuario creado. Se envió el enlace de activación.');
      setIsDrawerOpen(false);
      setReloadKey((k) => k + 1);
    } catch {
      showToast.error('No fue posible guardar. Revisa los datos.');
    }
  });

  const confirmar = async (justificacion?: string) => {
    if (!confirmacion) return;
    const { user, action } = confirmacion;
    try {
      if (action === 'toggle_status') {
        await apiClient.patch(ENDPOINTS.USUARIOS.TOGGLE_STATUS(user.id), { justificacion });
      } else {
        await apiClient.post(`${ENDPOINTS.USUARIOS.DETALLE(user.id)}password-reset/`);
      }
      showToast.success('Acción aplicada.');
      setReloadKey((k) => k + 1);
    } catch {
      showToast.error('No fue posible completar la acción.');
    } finally {
      setConfirmacion(null);
    }
  };

  const columns: ColumnDef<UsuarioRow>[] = [
    { key: 'numero_documento', header: 'Documento',
      render: (row) => <span className="font-monospace">{row.numero_documento}</span> },
    { key: 'nombre_completo', header: 'Nombre' },
    { key: 'cargo', header: 'Cargo' },
    { key: 'email', header: 'Correo' },
    { key: 'roles', header: 'Roles',
      render: (row) => (
        <div className="d-flex flex-wrap gap-1">
          {row.roles.map((r) => <Badge key={r.id} variant="neutral">{r.nombre}</Badge>)}
        </div>
      ) },
    { key: 'is_active', header: 'Estado',
      render: (row) => (
        <ToggleSwitch
          size="sm"
          checked={row.is_active}
          disabled={!hasPermission('usuarios.eliminar')}
          onChange={() => setConfirmacion({ user: row, action: 'toggle_status' })}
          labelActive="Activo"
          labelInactive="Inactivo"
        />
      ) },
  ];

  const suspendiendo = confirmacion?.action === 'toggle_status' && confirmacion.user.is_active;

  return (
    <div className="joli-page-container w-100">
      <div className="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="h4 fw-bold mb-1">Gestión de usuarios</h1>
          <p className="text-muted small mb-0">Colaboradores, roles asignados y estado de acceso.</p>
        </div>
        <div className="btn-group" role="group" aria-label="Acciones del módulo">
          <button type="button" className="btn btn-outline-secondary d-inline-flex align-items-center gap-2"
                  onClick={() => setIsRolesOpen(true)} disabled={!hasPermission('roles.editar')}>
            <ShieldCheck size={16} aria-hidden="true" /><span>Administrar roles</span>
          </button>
          <button type="button" className="btn btn-primary d-inline-flex align-items-center gap-2"
                  onClick={() => abrirDrawer(null)} disabled={!hasPermission('usuarios.crear')}>
            <UserPlus size={16} aria-hidden="true" /><span>Nuevo usuario</span>
          </button>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={rows}
        totalRows={total}
        currentPage={page}
        pageSize={pageSize}
        isLoading={isLoading}
        onPageChange={setPage}
        onPageSizeChange={(size) => { setPageSize(size); setPage(1); }}
        onSearchChange={(q) => { setSearch(q); setPage(1); }}
        actions={(row) => (
          <div className="btn-group btn-group-sm row-actions-group" role="group" aria-label="Acciones de fila">
            <button type="button" className="btn btn-outline-secondary" title="Editar usuario" aria-label="Editar usuario"
                    onClick={() => abrirDrawer(row)} disabled={!hasPermission('usuarios.editar')}>
              <Edit2 size={14} aria-hidden="true" />
            </button>
            <button type="button" className="btn btn-outline-secondary" title="Enviar enlace de restablecimiento"
                    aria-label="Enviar enlace de restablecimiento de contraseña"
                    onClick={() => setConfirmacion({ user: row, action: 'reset_password' })}
                    disabled={!hasPermission('usuarios.editar')}>
              <KeyRound size={14} aria-hidden="true" />
            </button>
          </div>
        )}
      />

      <Drawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        title={editing ? 'Editar usuario' : 'Nuevo usuario'}
        subtitle="Datos de identidad y roles"
        size="md"
        footer={
          <div className="d-flex justify-content-end gap-2 w-100">
            <button type="button" className="btn btn-outline-secondary" onClick={() => setIsDrawerOpen(false)}>Cancelar</button>
            <button type="submit" form="form-usuario" className="btn btn-primary" disabled={form.formState.isSubmitting}>
              Guardar
            </button>
          </div>
        }
      >
        <form id="form-usuario" className="row g-3" onSubmit={guardar} noValidate>
          {([
            ['numero_documento', 'Número de documento', 'text', '1000000001'],
            ['email', 'Correo', 'email', 'usuario@ejemplo.com'],
            ['first_name', 'Nombres', 'text', ''],
            ['last_name', 'Apellidos', 'text', ''],
            ['cargo', 'Cargo', 'text', ''],
          ] as const).map(([name, label, type, placeholder]) => (
            <div key={name} className="col-12 col-md-6">
              <label htmlFor={`usuario-${name}`} className="form-label small fw-semibold">{label}</label>
              <input
                id={`usuario-${name}`}
                type={type}
                className={`form-control form-control-sm input-control ${form.formState.errors[name] ? 'is-invalid' : ''}`}
                placeholder={placeholder}
                disabled={name === 'numero_documento' && editing !== null}
                aria-invalid={Boolean(form.formState.errors[name])}
                {...form.register(name)}
              />
              {form.formState.errors[name] && (
                <div className="invalid-feedback">{form.formState.errors[name]?.message}</div>
              )}
            </div>
          ))}

          <fieldset className="col-12">
            <legend className="form-label small fw-semibold">Roles asignados</legend>
            <Controller
              control={form.control}
              name="roles"
              render={({ field }) => (
                <div className="d-flex flex-wrap gap-2">
                  {roles.map((r) => {
                    const checked = field.value.includes(r.id);
                    return (
                      <label key={r.id} className="form-check form-check-inline">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          checked={checked}
                          onChange={() => field.onChange(checked ? field.value.filter((id) => id !== r.id) : [...field.value, r.id])}
                        />
                        <span className="form-check-label">{r.nombre}</span>
                      </label>
                    );
                  })}
                </div>
              )}
            />
            {form.formState.errors.roles && <div className="text-danger small">{form.formState.errors.roles.message}</div>}
            <small className="text-muted d-block mt-1">Los permisos finales son la unión de los roles asignados.</small>
          </fieldset>
        </form>
      </Drawer>

      <RolesAdminSidebar isOpen={isRolesOpen} onClose={() => setIsRolesOpen(false)} />

      <ConfirmModal
        isOpen={confirmacion !== null}
        onClose={() => setConfirmacion(null)}
        onConfirm={confirmar}
        type={confirmacion?.action === 'reset_password' ? 'warning' : suspendiendo ? 'danger' : 'success'}
        emphasizeCancel={suspendiendo}
        requiresJustification={suspendiendo}
        title={
          confirmacion?.action === 'reset_password'
            ? '¿Enviar enlace de restablecimiento?'
            : suspendiendo ? '¿Suspender el acceso del usuario?' : '¿Reactivar el acceso del usuario?'
        }
        message={
          confirmacion?.action === 'reset_password'
            ? 'Se enviará al correo registrado un enlace de un solo uso válido por 15 minutos.'
            : suspendiendo
              ? 'El usuario perderá el acceso de inmediato y sus sesiones activas se cerrarán.'
              : 'El usuario podrá iniciar sesión de nuevo con sus credenciales.'
        }
        confirmText={confirmacion?.action === 'reset_password' ? 'Enviar enlace' : suspendiendo ? 'Suspender' : 'Reactivar'}
      />
    </div>
  );
}
```

Contrato de respuesta del listado: `{ "count": 150, "results": [ { "id": 1, "numero_documento": "1000000001", "nombre_completo": "Usuario Ejemplo", "first_name": "Usuario", "last_name": "Ejemplo", "email": "usuario@ejemplo.com", "cargo": "Analista", "roles": [{ "id": 2, "codigo": "OPERADOR", "nombre": "Operador" }], "is_active": true } ] }`.
