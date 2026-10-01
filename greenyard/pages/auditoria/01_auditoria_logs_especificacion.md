# 01. Especificación del Módulo de Bitácora de Auditoría y Trazabilidad
## Ecosistema Jolifoods — Spec-Driven Development (SDD)

Esta especificación describe el módulo corporativo de **Bitácora de Auditoría**, encargado de registrar y auditar de forma **inmutable** todos los eventos de autenticación, cambios de datos críticos y transacciones operativas del sistema.

Es una herramienta obligatoria para cumplir con los estándares de seguridad corporativa y los pasos de auditoría de Jolifoods.

---

## 1. Modelo de Datos Inmutable (Registro de Auditoría)

Cada registro de auditoría almacena:
- `id`: UUID único inmutable.
- `usuario`: ForeignKey indexada al usuario (o `None` si fue un intento anónimo fallido).
- `numero_documento`: Cédula capturada para trazabilidad incluso si el usuario es eliminado.
- `tipo_evento`: `LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOGOUT`, `CREATE`, `UPDATE`, `DELETE`, `PASSWORD_RESET`.
- `modulo`: Nombre del módulo afectado (`AUTENTICACION`, `USUARIOS`, `INVENTARIO`, `DESPACHOS`).
- `ip_origen`: Dirección IP extraída de `HTTP_X_FORWARDED_FOR` / `REMOTE_ADDR`.
- `user_agent`: Navegador y sistema operativo del cliente.
- `payload_antes`: JSON serializado con el estado previo (en modificaciones).
- `payload_despues`: JSON serializado con el nuevo estado.
- `fecha_hora`: Marca de tiempo UTC indexada (`db_index=True`).

---

## 2. Implementación de la Vista en React 19 + TypeScript (`AuditoriaLogsPage.tsx`)

```tsx
import React, { useState } from 'react';
import { DataTable, ColumnDef } from '../../components/data_table/DataTable';
import { Modal } from '../../components/modal/Modal';
import { Badge } from '../../components/badge/Badge';
import { ShieldAlert, FileText, Eye, CheckCircle2, XCircle } from 'lucide-react';
import '../../styles/variables.css';

interface LogItem {
  id: string;
  fecha_hora: string;
  documento: string;
  usuario_nombre: string;
  tipo_evento: string;
  modulo: string;
  ip_origen: string;
  resultado: 'EXITO' | 'FALLO';
  detalles: string;
}

export const AuditoriaLogsPage: React.FC = () => {
  const [selectedLog, setSelectedLog] = useState<LogItem | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  const logs: LogItem[] = [
    {
      id: 'log-001',
      fecha_hora: '30/09/2026 12:14:22',
      documento: '1020405060',
      usuario_nombre: 'Joan Montoya',
      tipo_evento: 'LOGIN_SUCCESS',
      modulo: 'AUTENTICACIÓN',
      ip_origen: '190.14.85.120',
      resultado: 'EXITO',
      detalles: 'Inicio de sesión exitoso mediante credenciales y cookie HttpOnly emitida.'
    },
    {
      id: 'log-002',
      fecha_hora: '30/09/2026 12:10:05',
      documento: '1099887766',
      usuario_nombre: 'Desconocido',
      tipo_evento: 'LOGIN_FAILED',
      modulo: 'AUTENTICACIÓN',
      ip_origen: '186.28.14.90',
      resultado: 'FALLO',
      detalles: 'Contraseña inválida. Intento 1 de 5 registrado en Redis Rate Limiter.'
    },
    {
      id: 'log-003',
      fecha_hora: '30/09/2026 11:45:10',
      documento: '10203040',
      usuario_nombre: 'Administrador Jolifoods',
      tipo_evento: 'UPDATE',
      modulo: 'USUARIOS',
      ip_origen: '10.0.1.5',
      resultado: 'EXITO',
      detalles: 'Modificación de rol para el usuario con documento 1010203040 (OPERADOR -> ADMIN).'
    }
  ];

  const columns: ColumnDef<LogItem>[] = [
    {
      key: 'fecha_hora',
      header: 'Fecha y Hora',
      width: '180px'
    },
    {
      key: 'documento',
      header: 'Documento / Usuario',
      render: (row) => (
        <div>
          <div className="font-monospace fw-bold text-primary">{row.documento}</div>
          <div className="text-muted small">{row.usuario_nombre}</div>
        </div>
      )
    },
    {
      key: 'tipo_evento',
      header: 'Evento',
      render: (row) => {
        const isLogin = row.tipo_evento.startsWith('LOGIN');
        const isFailed = row.resultado === 'FALLO';
        return (
          <Badge variant={isFailed ? 'danger' : isLogin ? 'info' : 'warning'}>
            {row.tipo_evento}
          </Badge>
        );
      }
    },
    {
      key: 'modulo',
      header: 'Módulo',
      render: (row) => <span className="small text-secondary fw-semibold">{row.modulo}</span>
    },
    {
      key: 'ip_origen',
      header: 'IP Origen',
      render: (row) => <span className="font-monospace small text-muted">{row.ip_origen}</span>
    },
    {
      key: 'resultado',
      header: 'Resultado',
      render: (row) => (
        <span className={`d-inline-flex align-items-center gap-1 small fw-bold ${row.resultado === 'EXITO' ? 'text-success' : 'text-danger'}`}>
          {row.resultado === 'EXITO' ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
          {row.resultado}
        </span>
      )
    }
  ];

  return (
    <div className="joli-page-container">
      {/* CABECERA */}
      <div className="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-3">
        <div>
          <h1 className="h4 fw-bold mb-1 text-primary-emphasis">Bitácora de Auditoría y Trazabilidad</h1>
          <p className="text-muted small mb-0">Registro inmutable de accesos, modificaciones y eventos de seguridad.</p>
        </div>
      </div>

      {/* TABLA DE AUDITORÍA */}
      <DataTable
        columns={columns}
        data={logs}
        totalRows={logs.length}
        currentPage={currentPage}
        pageSize={15}
        onPageChange={(page) => setCurrentPage(page)}
        onSearchChange={(q) => console.log('Buscar log:', q)}
        onExportExcel={() => console.log('Exportar auditoría a Excel')}
        onExportPdf={() => console.log('Exportar auditoría a PDF')}
        actions={(row) => (
          <button 
            type="button" 
            className="btn btn-sm btn-outline-secondary p-1"
            title="Ver detalles completos del evento"
            onClick={() => setSelectedLog(row)}
          >
            <Eye size={14} />
          </button>
        )}
      />

      {/* MODAL DE DETALLE DEL LOG */}
      {selectedLog && (
        <Modal
          isOpen={!!selectedLog}
          onClose={() => setSelectedLog(null)}
          title={`Detalle de Evento #${selectedLog.id}`}
          subtitle={`Registrado el ${selectedLog.fecha_hora}`}
          size="md"
          footer={
            <button type="button" className="btn btn-outline-secondary" onClick={() => setSelectedLog(null)}>
              Cerrar
            </button>
          }
        >
          <div className="row g-3">
            <div className="col-6">
              <label className="text-muted small fw-bold text-uppercase">Tipo de Evento</label>
              <div><strong>{selectedLog.tipo_evento}</strong></div>
            </div>
            <div className="col-6">
              <label className="text-muted small fw-bold text-uppercase">Resultado</label>
              <div><span className={selectedLog.resultado === 'EXITO' ? 'text-success' : 'text-danger'}>{selectedLog.resultado}</span></div>
            </div>
            <div className="col-6">
              <label className="text-muted small fw-bold text-uppercase">Usuario / Cédula</label>
              <div>{selectedLog.usuario_nombre} ({selectedLog.documento})</div>
            </div>
            <div className="col-6">
              <label className="text-muted small fw-bold text-uppercase">Dirección IP</label>
              <div className="font-monospace">{selectedLog.ip_origen}</div>
            </div>
            <div className="col-12">
              <label className="text-muted small fw-bold text-uppercase">Detalle Técnico</label>
              <div className="p-3 bg-body-tertiary rounded small border font-monospace">
                {selectedLog.detalles}
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
```
