# 01. Especificación del Módulo de Gestión de Usuarios y Roles (CRUD)
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Esta especificación formaliza la pantalla administrativa de **Gestión de Usuarios**, donde los administradores del sistema pueden listar, crear, editar, asignar roles corporativos y suspender accesos.

Cumple rigurosamente con la **Normativa de Auditoría (Anti-N+1 en backend, paginación server-side, validación Zod en cliente)**.

---

## 1. Arquitectura de Endpoints (Backend Django ORM + FastAPI ASGI)

### 1.1. Consulta Optimizada de Usuarios (Anti-N+1 Estricto)
- **Ruta**: `GET /api/v1/usuarios/?page=1&page_size=10&search=&rol=&estado=`
- **Optimización Obligatoria**:
  ```python
  # backend/apps/auth_core/queries.py
  def obtener_usuarios_paginados(page=1, page_size=10, search="", rol=None):
      queryset = Usuario.objects.select_related('rol', 'sede')\
                                .only('id', 'numero_documento', 'username', 'first_name', 
                                      'last_name', 'email', 'is_active', 'rol__nombre', 'sede__nombre')
      if search:
          queryset = queryset.filter(
              Q(numero_documento__icontains=search) | 
              Q(first_name__icontains=search) | 
              Q(last_name__icontains=search) |
              Q(email__icontains=search)
          )
      if rol:
          queryset = queryset.filter(rol__nombre=rol)
          
      paginator = Paginator(queryset.order_by('-fecha_registro'), page_size)
      return paginator.get_page(page)
  ```

---

## 2. Implementación de la Vista en React 19 + TypeScript (`UsuariosPage.tsx`)

```tsx
import React, { useState } from 'react';
import { DataTable, ColumnDef } from '../../components/data_table/DataTable';
import { Modal } from '../../components/modal/Modal';
import { ConfirmModal } from '../../components/modal/ConfirmModal';
import { Badge } from '../../components/badge/Badge';
import { SelectFilter } from '../../components/dropdown/SelectFilter';
import { UserPlus, Edit2, UserX, UserCheck, KeyRound, Download } from 'lucide-react';
import '../../styles/variables.css';

interface UsuarioRow {
  id: string;
  numero_documento: string;
  nombre_completo: string;
  email: string;
  rol: string;
  sede: string;
  is_active: boolean;
}

export const UsuariosPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UsuarioRow | null>(null);
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    user: UsuarioRow | null;
    action: 'toggle_status' | 'reset_password';
  }>({ isOpen: false, user: null, action: 'toggle_status' });
  const [selectedRol, setSelectedRol] = useState('OPERADOR');
  const [currentPage, setCurrentPage] = useState(1);

  // Opciones para SelectFilter tipo búsqueda
  const rolesOptions = [
    { value: 'ADMIN', label: 'Administrador (Total)' },
    { value: 'OPERADOR', label: 'Operador de Módulo' },
    { value: 'AUDITOR', label: 'Auditor de Calidad' },
    { value: 'CONSULTA', label: 'Solo Consulta' }
  ];

  // Datos simulados de referencia
  const [usuarios] = useState<UsuarioRow[]>([
    {
      id: '1',
      numero_documento: '10203040',
      nombre_completo: 'Administrador Jolifoods',
      email: 'admin@jolifoods.com',
      rol: 'ADMIN',
      sede: 'Sede Principal',
      is_active: true
    },
    {
      id: '2',
      numero_documento: '1020405060',
      nombre_completo: 'Joan Montoya',
      email: 'j.montoya@jolifoods.com',
      rol: 'ADMIN',
      sede: 'Sede Principal',
      is_active: true
    },
    {
      id: '3',
      numero_documento: '1010203040',
      nombre_completo: 'Operador Báscula',
      email: 'operador1@jolifoods.com',
      rol: 'OPERADOR',
      sede: 'Planta Procesamiento',
      is_active: true
    },
    {
      id: '4',
      numero_documento: '71203040',
      nombre_completo: 'Auditor Calidad',
      email: 'auditor@jolifoods.com',
      rol: 'AUDITOR',
      sede: 'Centro Logístico',
      is_active: false
    }
  ]);

  const columns: ColumnDef<UsuarioRow>[] = [
    {
      key: 'numero_documento',
      header: 'Cédula / Documento',
      render: (row) => <strong className="font-monospace text-primary">{row.numero_documento}</strong>
    },
    {
      key: 'nombre_completo',
      header: 'Nombre del Colaborador'
    },
    {
      key: 'email',
      header: 'Correo Institucional'
    },
    {
      key: 'rol',
      header: 'Rol Asignado',
      render: (row) => (
        <Badge variant={row.rol === 'ADMIN' ? 'admin' : row.rol === 'OPERADOR' ? 'operator' : 'neutral'}>
          {row.rol}
        </Badge>
      )
    },
    {
      key: 'sede',
      header: 'Sede'
    },
    {
      key: 'is_active',
      header: 'Estado',
      render: (row) => (
        <Badge variant={row.is_active ? 'success' : 'danger'} dot>
          {row.is_active ? 'Activo' : 'Suspendido'}
        </Badge>
      )
    }
  ];

  const handleExecuteConfirm = async () => {
    if (!confirmDialog.user) return;
    // Ejecutar mutación en backend
    setConfirmDialog({ isOpen: false, user: null, action: 'toggle_status' });
  };

  return (
    <div className="joli-page-container">
      {/* CABECERA DE LA PÁGINA */}
      <div className="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="h4 fw-bold mb-1 text-primary-emphasis">Gestión de Usuarios y Roles</h1>
          <p className="text-muted small mb-0">Control centralizado de colaboradores, permisos y sedes.</p>
        </div>
        <button 
          type="button" 
          className="btn btn-primary d-inline-flex align-items-center gap-2"
          onClick={() => { setSelectedUser(null); setSelectedRol('OPERADOR'); setIsModalOpen(true); }}
        >
          <UserPlus size={16} />
          <span>Nuevo Usuario</span>
        </button>
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
          <div className="d-flex align-items-center gap-1 justify-content-end">
            <button 
              type="button" 
              className="btn btn-sm btn-outline-secondary p-1"
              title="Editar usuario"
              onClick={() => { 
                setSelectedUser(row); 
                setSelectedRol(row.rol);
                setIsModalOpen(true); 
              }}
            >
              <Edit2 size={14} />
            </button>
            <button 
              type="button" 
              className="btn btn-sm btn-outline-warning p-1"
              title="Restablecer contraseña"
              onClick={() => setConfirmDialog({ isOpen: true, user: row, action: 'reset_password' })}
            >
              <KeyRound size={14} />
            </button>
            <button 
              type="button" 
              className={`btn btn-sm ${row.is_active ? 'btn-outline-danger' : 'btn-outline-success'} p-1`}
              title={row.is_active ? 'Suspender usuario' : 'Habilitar usuario'}
              onClick={() => setConfirmDialog({ isOpen: true, user: row, action: 'toggle_status' })}
            >
              {row.is_active ? <UserX size={14} /> : <UserCheck size={14} />}
            </button>
          </div>
        )}
      />

      {/* MODAL DE CREACIÓN / EDICIÓN (CON SELECTOR DE BÚSQUEDA) */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedUser ? "Editar Usuario" : "Registrar Nuevo Colaborador"}
        subtitle="Especifique los datos de identidad y permisos correspondientes"
        size="md"
        footer={
          <>
            <button type="button" className="btn btn-outline-secondary" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </button>
            <button type="button" className="btn btn-primary">
              {selectedUser ? "Guardar Cambios" : "Crear Usuario"}
            </button>
          </>
        }
      >
        <form className="row g-3">
          <div className="col-12 col-md-6">
            <label className="form-label small fw-semibold">Número de Documento / Cédula</label>
            <input 
              type="text" 
              className="form-control form-control-sm" 
              defaultValue={selectedUser?.numero_documento || ''}
              disabled={!!selectedUser}
              placeholder="Ej. 1020405060"
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label small fw-semibold">Correo Institucional</label>
            <input 
              type="email" 
              className="form-control form-control-sm" 
              defaultValue={selectedUser?.email || ''}
              placeholder="colaborador@jolifoods.com"
            />
          </div>
          <div className="col-12 col-md-6">
            <label className="form-label small fw-semibold">Nombre Completo</label>
            <input 
              type="text" 
              className="form-control form-control-sm" 
              defaultValue={selectedUser?.nombre_completo || ''}
              placeholder="Ej. Joan Montoya"
            />
          </div>
          <div className="col-12 col-md-6">
            {/* SELECTOR TIPO BÚSQUEDA EN LUGAR DE SELECT NATIVO */}
            <SelectFilter
              label="Rol Corporativo Asignado"
              options={rolesOptions}
              value={selectedRol}
              onChange={(val) => setSelectedRol(val)}
              withSearch={true}
              placeholder="Buscar rol..."
            />
          </div>
        </form>
      </Modal>

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
            ? `Se enviará un correo a ${confirmDialog.user?.email} con un token efímero de 15 minutos para que redefina su clave.`
            : confirmDialog.user?.is_active
              ? `El colaborador con cédula ${confirmDialog.user?.numero_documento} perderá de inmediato el acceso a todos los módulos y sus sesiones activas serán invalidadas.`
              : `El colaborador con cédula ${confirmDialog.user?.numero_documento} podrá iniciar sesión normalmente con sus credenciales.`
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
