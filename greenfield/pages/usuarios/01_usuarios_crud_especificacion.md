# 01. Especificación del Módulo de Gestión de Usuarios y Roles (CRUD)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Esta especificación formaliza la pantalla administrativa de **Gestión de Usuarios**, donde los administradores del sistema pueden listar, crear, editar, asignar roles corporativos y suspender accesos.

Cumple rigurosamente con la **Normativa de Auditoría (Anti-N+1 en backend, paginación server-side, validación Zod en cliente)**.

---

## 1. Arquitectura de Endpoints y Modelos (Estabilización de Permisos Desacoplada)

> [!IMPORTANT]
> **ESTÁNDAR CANÓNICO DE PERMISOS (Arquitectura de Referencia: `tiendita`)**:
> En el ecosistema Jolifoods **nunca se preguntan roles fijos ni se queman listas estáticas en un Enum o formulario cerrado**.
> Los roles poseen su **propia tabla independiente (`roles`)** con un campo `permisos: JSONField`, cruzada con los usuarios mediante una relación **Muchos a Muchos (`ManyToManyField`)**:
>
> 1. **Modelo `Rol`**: Almacena `nombre` (dinámico) y `permisos` (`models.JSONField(default=dict)`), donde cada clave es un permiso booleano granular (`{"inventario_elementos": true, "admin_colaboradores": false, ...}`).
> 2. **Modelo `Usuario`**: Campo `roles = models.ManyToManyField(Rol, related_name='usuarios', blank=True)`. Un usuario puede tener múltiples roles combinados.
> 3. **Endpoint Universal de Permisos (`GET /api/mis-permisos/`)**: Cualquier usuario autenticado consulta sus permisos consolidados sin requerir rol de administrador. El backend itera sobre todos los roles del usuario y consolida la unión booleana de permisos.
> 4. **Panel Lateral de Gobernanza (`RolesAdminSidebar`)**: Desplegable desde Right Drawer para editar interactivamente la matriz de permisos de cualquier rol en tiempo real sin requerir despliegues ni migraciones.

### 1.1. Modelos Django ORM Canónicos

```python
# backend/apps/usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Rol")
    permisos = models.JSONField(default=dict, blank=True, verbose_name="Permisos del Rol")

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre

class Usuario(AbstractBaseUser):
    documento = models.CharField(max_length=50, unique=True, verbose_name="Documento")
    nombre = models.CharField(max_length=150, default='', verbose_name="Nombre Completo")
    cargo = models.CharField(max_length=100, default='', verbose_name="Cargo")
    correo_electronico = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    
    # Cruce Many-to-Many estricto con la tabla de roles
    roles = models.ManyToManyField(Rol, related_name='usuarios', blank=True, verbose_name="Roles")
    
    is_active = models.BooleanField(default=True, verbose_name="Estado Activo")
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'documento'
    REQUIRED_FIELDS = ['nombre', 'correo_electronico']

    class Meta:
        db_table = 'usuarios'
```

### 1.2. Consulta Optimizada de Usuarios (Anti-N+1 con Prefetch)
- **Ruta**: `GET /api/v1/usuarios/?page=1&page_size=10&search=&rol_id=&estado=`
- **Optimización Obligatoria**:
  ```python
  # backend/apps/usuarios/queries.py
  from django.db.models import Q
  from django.core.paginator import Paginator

  def obtener_usuarios_paginados(page=1, page_size=10, search="", rol_id=None):
      # Uso mandatorio de prefetch_related para la relación Many-to-Many con roles
      queryset = Usuario.objects.prefetch_related('roles')\
                                .only('id', 'documento', 'nombre', 'cargo', 
                                      'correo_electronico', 'is_active', 'last_login')
      if search:
          queryset = queryset.filter(
              Q(documento__icontains=search) | 
              Q(nombre__icontains=search) | 
              Q(correo_electronico__icontains=search) |
              Q(cargo__icontains=search)
          )
      if rol_id:
          queryset = queryset.filter(roles__id=rol_id)
          
      paginator = Paginator(queryset.order_by('nombre'), page_size)
      return paginator.get_page(page)
  ```

### 1.3. Endpoint de Estabilización de Permisos del Usuario Activo
- **Ruta**: `GET /api/mis-permisos/`
- **Permisos**: `IsAuthenticated` (Cualquier usuario autenticado puede consultarlo)
- **Implementación**:
  ```python
  # backend/apps/usuarios/views.py
  from rest_framework.views import APIView
  from rest_framework.response import Response
  from rest_framework.permissions import IsAuthenticated

  class MisPermisosView(APIView):
      permission_classes = [IsAuthenticated]

      def get(self, request):
          user_roles = request.user.roles.all()
          permisos_combinados = {}
          for rol in user_roles:
              if rol.permisos and isinstance(rol.permisos, dict):
                  for key, valor in rol.permisos.items():
                      if valor:
                          permisos_combinados[key] = True
          return Response(permisos_combinados)
  ```

### 1.4. Endpoint de Activación / Desactivación Inmediata (Toggle Active)
- **Ruta**: `PATCH /api/v1/usuarios/{id}/toggle-active/`
- **Permisos**: Requiere rol administrativo o permiso `admin_colaboradores`.
- **Comportamiento**:
  - Si `is_active` pasa a `False` (desactivación): Invalida de inmediato tokens JWT emitidos y purga sesiones activas en Redis.
  - Si `is_active` pasa a `True` (activación): Habilita credenciales para inicio de sesión inmediato.
  - Registra el evento en `RegistroActividad` con IP, actor y timestamp.

---

## 2. Implementación de la Vista en React 19 + TypeScript (`UsuariosPage.tsx`)

```tsx
import React, { useState, useEffect } from 'react';
import { DataTable, ColumnDef } from '../../components/data_table/DataTable';
import { Drawer } from '../../components/drawer/Drawer';
import { ConfirmModal } from '../../components/modal/ConfirmModal';
import { Badge } from '../../components/badge/Badge';
import { ToggleSwitch } from '../../components/toggle/ToggleSwitch';
import { SelectFilter } from '../../components/dropdown/SelectFilter';
import { RolesAdminSidebar } from '../../components/roles/RolesAdminSidebar';
import { UserPlus, Edit2, KeyRound, ShieldCheck } from 'lucide-react';
import '../../styles/variables.css';

interface RolItem {
  id: number;
  nombre: string;
}

interface UsuarioRow {
  id: string;
  documento: string;
  nombre: string;
  cargo: string;
  correo_electronico: string;
  roles: string[];
  is_active: boolean;
}

export const UsuariosPage: React.FC = () => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isRolesSidebarOpen, setIsRolesSidebarOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UsuarioRow | null>(null);
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    user: UsuarioRow | null;
    action: 'toggle_status' | 'reset_password';
  }>({ isOpen: false, user: null, action: 'toggle_status' });
  const [rolesDisponibles, setRolesDisponibles] = useState<RolItem[]>([]);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

  // Cargar roles disponibles desde backend dinámicamente
  useEffect(() => {
    fetch('/api/v1/roles/')
      .then((res) => res.json())
      .then((data) => setRolesDisponibles(data))
      .catch(() => console.error('Error al cargar roles'));
  }, []);

  // Datos simulados de referencia con múltiples roles dinámicos
  const [usuarios] = useState<UsuarioRow[]>([
    {
      id: '1',
      documento: '10203040',
      nombre: 'Administrador Jolifoods',
      cargo: 'Líder de Tecnología',
      correo_electronico: 'admin@jolifoods.com',
      roles: ['Administrador', 'SA'],
      is_active: true
    },
    {
      id: '2',
      documento: '1020405060',
      nombre: 'Joan Montoya',
      cargo: 'Ingeniero de Software Senior',
      correo_electronico: 'j.montoya@jolifoods.com',
      roles: ['Administrador'],
      is_active: true
    },
    {
      id: '3',
      documento: '1010203040',
      nombre: 'Operador Báscula',
      cargo: 'Operario de Planta',
      correo_electronico: 'operador1@jolifoods.com',
      roles: ['Operador Planta'],
      is_active: true
    },
    {
      id: '4',
      documento: '71203040',
      nombre: 'Auditor Calidad',
      cargo: 'Coordinador SGI',
      correo_electronico: 'auditor@jolifoods.com',
      roles: ['Auditor Calidad', 'Talento Humano'],
      is_active: false
    }
  ]);

  const columns: ColumnDef<UsuarioRow>[] = [
    {
      key: 'documento',
      header: 'Cédula / Documento',
      render: (row) => <strong className="font-monospace text-primary">{row.documento}</strong>
    },
    {
      key: 'nombre',
      header: 'Nombre del Colaborador'
    },
    {
      key: 'cargo',
      header: 'Cargo Corporativo'
    },
    {
      key: 'correo_electronico',
      header: 'Correo Institucional'
    },
    {
      key: 'roles',
      header: 'Roles Asignados',
      render: (row) => (
        <div className="d-flex flex-wrap gap-1">
          {row.roles.map((rolNombre) => (
            <Badge 
              key={rolNombre} 
              variant={rolNombre.toUpperCase() === 'SA' ? 'danger' : rolNombre.toUpperCase().includes('ADMIN') ? 'admin' : 'neutral'}
            >
              {rolNombre}
            </Badge>
          ))}
        </div>
      )
    },
    {
      key: 'is_active',
      header: 'Estado / Activar',
      render: (row) => (
        <ToggleSwitch
          size="sm"
          checked={row.is_active}
          onChange={() => {
            if (row.is_active) {
              setConfirmDialog({ isOpen: true, user: row, action: 'toggle_status' });
            } else {
              handleDirectReactivate(row);
            }
          }}
          labelActive="Activo"
          labelInactive="Inactivo"
        />
      )
    }
  ];

  const handleExecuteConfirm = async () => {
    if (!confirmDialog.user) return;
    setConfirmDialog({ isOpen: false, user: null, action: 'toggle_status' });
  };

  const handleDirectReactivate = async (user: UsuarioRow) => {
    // Llamada PATCH /api/v1/usuarios/{id}/toggle-active/
  };

  return (
    <div className="joli-page-container w-100">
      {/* CABECERA DE LA PÁGINA */}
      <div className="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="h4 fw-bold mb-1 text-primary-emphasis">Gestión de Usuarios y Roles</h1>
          <p className="text-muted small mb-0">Control centralizado de colaboradores, asignación de roles y estabilización de permisos.</p>
        </div>
        <div className="d-flex align-items-center gap-2">
          {/* BOTÓN CANÓNICO DE GOBERNANZA DE ROLES Y PERMISOS */}
          <button
            type="button"
            className="btn btn-outline-primary d-inline-flex align-items-center gap-2"
            onClick={() => setIsRolesSidebarOpen(true)}
            title="Abrir panel lateral de configuración de permisos por rol"
          >
            <ShieldCheck size={16} />
            <span>Administrar Roles</span>
          </button>

          <button 
            type="button" 
            className="btn btn-primary d-inline-flex align-items-center gap-2"
            onClick={() => { setSelectedUser(null); setSelectedRoles([]); setIsDrawerOpen(true); }}
          >
            <UserPlus size={16} />
            <span>Nuevo Usuario</span>
          </button>
        </div>
      </div>

      {/* TABLA PRINCIPAL DE DATOS CON FILTROS TIPO EXCEL */}
      <DataTable
        columns={columns}
        data={usuarios}
        totalRows={usuarios.length}
        currentPage={currentPage}
        pageSize={10}
        onPageChange={(page) => setCurrentPage(page)}
        onSearchChange={(query) => console.log('Búsqueda:', query)}
        onExportExcel={() => console.log('Exportar Excel')}
        onExportPdf={() => console.log('Exportar PDF')}
        actions={(row) => (
          <div className="btn-group btn-group-sm row-actions-group" role="group" aria-label="Acciones de usuario">
            <button 
              type="button" 
              className="btn btn-outline-secondary btn-action-view"
              title="Editar usuario en Sidebar Derecho"
              onClick={() => { 
                setSelectedUser(row); 
                setSelectedRoles(row.roles);
                setIsDrawerOpen(true); 
              }}
            >
              <Edit2 size={14} />
            </button>
            <button 
              type="button" 
              className="btn btn-outline-warning btn-action-key"
              title="Restablecer contraseña (envío de token seguro por email)"
              onClick={() => setConfirmDialog({ isOpen: true, user: row, action: 'reset_password' })}
            >
              <KeyRound size={14} />
            </button>
          </div>
        )}
      />

      {/* PANEL LATERAL DERECHO (RIGHT DRAWER) OBLIGATORIO PARA CREACIÓN Y EDICIÓN CRUD */}
      <Drawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        title={selectedUser ? "Editar Usuario" : "Registrar Nuevo Colaborador"}
        subtitle="Especifique los datos de identidad y seleccione los roles dinámicos"
        size="md"
        footer={
          <div className="d-flex align-items-center justify-content-end gap-2 w-100">
            <button type="button" className="btn btn-outline-secondary" onClick={() => setIsDrawerOpen(false)}>
              Cancelar
            </button>
            <button type="button" className="btn btn-primary">
              {selectedUser ? "Guardar Cambios" : "Crear Usuario"}
            </button>
          </div>
        }
      >
        <form className="row g-3">
          <div className="col-12 col-md-6">
            <label className="form-label small fw-semibold">Número de Documento / Cédula</label>
            <input 
              type="text" 
              className="form-control form-control-sm" 
              defaultValue={selectedUser?.documento || ''}
              disabled={!!selectedUser}
              placeholder="Ej. 1020405060"
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label small fw-semibold">Correo Institucional</label>
            <input 
              type="email" 
              className="form-control form-control-sm" 
              defaultValue={selectedUser?.correo_electronico || ''}
              placeholder="colaborador@jolifoods.com"
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label small fw-semibold">Nombre Completo</label>
            <input 
              type="text" 
              className="form-control form-control-sm" 
              defaultValue={selectedUser?.nombre || ''}
              placeholder="Ej. Joan Montoya"
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label small fw-semibold">Cargo Corporativo</label>
            <input 
              type="text" 
              className="form-control form-control-sm" 
              defaultValue={selectedUser?.cargo || ''}
              placeholder="Ej. Ingeniero de Software"
            />
          </div>
          <div className="col-12">
            {/* SELECTOR DINÁMICO DE ROLES ALIMENTADO DESDE LA TABLA ROLES */}
            <label className="form-label small fw-semibold">Roles Corporativos Asignados</label>
            <div className="d-flex flex-wrap gap-2 p-2 border rounded" style={{ backgroundColor: 'var(--color-bg-base)' }}>
              {rolesDisponibles.map((r) => {
                const isSelected = selectedRoles.includes(r.nombre);
                return (
                  <button
                    key={r.id}
                    type="button"
                    className={`btn btn-sm ${isSelected ? 'btn-primary' : 'btn-outline-secondary'}`}
                    onClick={() => {
                      if (isSelected) {
                        setSelectedRoles(selectedRoles.filter((name) => name !== r.nombre));
                      } else {
                        setSelectedRoles([...selectedRoles, r.nombre]);
                      }
                    }}
                  >
                    {r.nombre}
                  </button>
                );
              })}
            </div>
            <small className="text-muted d-block mt-1">
              Un colaborador puede acumular múltiples roles. Sus permisos finales serán la unión de todos ellos.
            </small>
          </div>
        </form>
      </Drawer>

      {/* PANEL LATERAL DE GOBERNANZA DE ROLES Y PERMISOS (Arquitectura Tiendita) */}
      <RolesAdminSidebar
        isOpen={isRolesSidebarOpen}
        onClose={() => setIsRolesSidebarOpen(false)}
      />

      {/* CONFIRM MODAL CORPORATIVO (EN LUGAR DE WINDOW.CONFIRM) */}
      <ConfirmModal
        isOpen={confirmDialog.isOpen}
        onClose={() => setConfirmDialog({ isOpen: false, user: null, action: 'toggle_status' })}
        onConfirm={handleExecuteConfirm}
        type={confirmDialog.action === 'reset_password' ? 'warning' : confirmDialog.user?.is_active ? 'danger' : 'success'}
        emphasizeCancel={confirmDialog.action !== 'reset_password' && confirmDialog.user?.is_active}
        title={
          confirmDialog.action === 'reset_password'
            ? "¿Generar enlace de restablecimiento de contraseña?"
            : confirmDialog.user?.is_active
              ? "¿Suspender acceso del usuario?"
              : "¿Reactivar acceso del usuario?"
        }
        message={
          confirmDialog.action === 'reset_password'
            ? `Se enviará un correo a ${confirmDialog.user?.correo_electronico} con un token efímero de 15 minutos (SHA-256) para que redefina su clave.`
            : confirmDialog.user?.is_active
              ? `El colaborador con cédula ${confirmDialog.user?.documento} perderá de inmediato el acceso a todos los módulos y sus sesiones activas serán invalidadas.`
              : `El colaborador con cédula ${confirmDialog.user?.documento} podrá iniciar sesión normalmente con sus credenciales.`
        }
        confirmText={
          confirmDialog.action === 'reset_password'
            ? "Enviar Correo"
            : confirmDialog.user?.is_active
              ? "Sí, Suspender"
              : "Sí, Reactivar"
        }
      />
    </div>
  );
};
```
