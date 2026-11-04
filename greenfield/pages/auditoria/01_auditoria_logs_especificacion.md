# 01. Especificación del Módulo de Bitácora de Auditoría
## Joli Foods — Spec-Driven Development (SDD)

Pantalla para consultar y exportar la bitácora: cambios de datos, operaciones y eventos de seguridad. Los registros son **solo-inserción**; esta pantalla solo lee.

---

## 1. Fuentes de Datos

| Fuente | Modelo | Ruta |
| :--- | :--- | :--- |
| Operaciones (crear, editar, eliminar, exportar, permisos, configuración) | [`RegistroBitacoraAuditoria`](../../../model/auditoria/spec_model_bitacora.md) | `GET /api/v1/auditoria/` (`ENDPOINTS.AUDITORIA.LOGS`) |
| Accesos (login, logout, bloqueos, restablecimientos) | [`RegistroAuditoriaAcceso`](../../../model/login/spec_model_sesion_auditoria.md) | `GET /api/v1/auditoria/accesos/` |
| Exportación | Ambos | `GET /api/v1/auditoria/exportar-excel/?<filtros>` (`ENDPOINTS.AUDITORIA.EXPORTAR_EXCEL`) |

- **Permisos:** `auditoria.ver` para consultar; `auditoria.exportar` para exportar. La exportación se registra a su vez en la bitácora (`EXPORT`).
- **Paginación en servidor** con filtros por rango de fechas (obligatorio, máximo 92 días por consulta), usuario/documento, módulo, tipo de evento y resultado. **Por qué:** la bitácora crece sin límite; sin rango obligatorio una consulta puede recorrer millones de filas.
- **Consulta sin N+1:** `RegistroBitacoraAuditoria.objects.select_related("usuario").only(...)`.
- Los payloads ya llegan sin campos sensibles (el modelo los limpia al insertar).

---

## 2. Vista (`AuditoriaLogsPage.tsx`)

Tabla a todo lo ancho con paginador arriba ([`DataTable`](../../../components/data_table/data_table.md)); el detalle de un evento se abre en el panel lateral derecho de solo lectura ([`Drawer`](../../../components/drawer/drawer.md)) para no perder el contexto de la tabla.

```tsx
import { useEffect, useState } from 'react';
import { Eye, CheckCircle2, XCircle } from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { ENDPOINTS } from '../services/endpoints';
import { useAuth } from '../context/AuthContext';
import { DataTable, type ColumnDef } from '../components/data_table/DataTable';
import { Drawer } from '../components/drawer/Drawer';
import { Badge } from '../components/badge/Badge';
import { showToast } from '../components/ToastNotification';

interface LogItem {
  id: string;
  fecha_hora: string; // ISO 8601
  numero_documento: string;
  usuario_nombre: string | null;
  tipo_evento: string;
  modulo: string;
  ip_origen: string | null;
  resultado: 'EXITO' | 'FALLO';
  detalles: string;
  payload_antes: Record<string, unknown> | null;
  payload_despues: Record<string, unknown> | null;
}
interface Paginado<T> { count: number; results: T[] }

const formatoFecha = new Intl.DateTimeFormat('es-CO', { dateStyle: 'short', timeStyle: 'medium' });

function hace30Dias(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().slice(0, 10);
}

export function AuditoriaLogsPage() {
  const { hasPermission } = useAuth();
  const [rows, setRows] = useState<LogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [search, setSearch] = useState('');
  const [desde] = useState(hace30Dias);
  const [isLoading, setIsLoading] = useState(false);
  const [selected, setSelected] = useState<LogItem | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    apiClient
      .get<Paginado<LogItem>>(ENDPOINTS.AUDITORIA.LOGS, {
        params: { page, page_size: pageSize, search, desde },
        signal: controller.signal,
      })
      .then((r) => { setRows(r.data.results); setTotal(r.data.count); })
      .catch(() => { if (!controller.signal.aborted) showToast.error('No fue posible cargar la bitácora.'); })
      .finally(() => { if (!controller.signal.aborted) setIsLoading(false); });
    return () => controller.abort();
  }, [page, pageSize, search, desde]);

  const exportarExcel = async () => {
    try {
      const { data } = await apiClient.get<Blob>(ENDPOINTS.AUDITORIA.EXPORTAR_EXCEL, {
        params: { search, desde }, responseType: 'blob',
      });
      const url = URL.createObjectURL(data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bitacora_${desde}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      showToast.error('No fue posible exportar la bitácora.');
    }
  };

  const columns: ColumnDef<LogItem>[] = [
    { key: 'fecha_hora', header: 'Fecha y hora', width: '180px',
      render: (row) => <time dateTime={row.fecha_hora}>{formatoFecha.format(new Date(row.fecha_hora))}</time> },
    { key: 'numero_documento', header: 'Documento / usuario',
      render: (row) => (
        <div>
          <div className="font-monospace">{row.numero_documento || '—'}</div>
          <div className="text-muted small">{row.usuario_nombre ?? 'Sistema / desconocido'}</div>
        </div>
      ) },
    { key: 'tipo_evento', header: 'Evento',
      render: (row) => <Badge variant={row.resultado === 'FALLO' ? 'danger' : 'neutral'}>{row.tipo_evento}</Badge> },
    { key: 'modulo', header: 'Módulo' },
    { key: 'ip_origen', header: 'IP', render: (row) => <span className="font-monospace small">{row.ip_origen ?? '—'}</span> },
    { key: 'resultado', header: 'Resultado',
      render: (row) => (
        <span className="d-inline-flex align-items-center gap-1 small fw-semibold">
          {row.resultado === 'EXITO' ? <CheckCircle2 size={14} aria-hidden="true" /> : <XCircle size={14} aria-hidden="true" />}
          {row.resultado === 'EXITO' ? 'Éxito' : 'Fallo'}
        </span>
      ) },
  ];

  return (
    <div className="joli-page-container w-100">
      <div className="mb-4">
        <h1 className="joli-page-title">Bitácora de auditoría</h1>
        <p className="text-muted small mb-0">Registro de accesos, cambios y eventos de seguridad (solo lectura).</p>
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
        onExportExcel={hasPermission('auditoria.exportar') ? exportarExcel : undefined}
        actions={(row) => (
          <button type="button" className="btn btn-sm btn-outline-secondary"
                  title="Ver detalle del evento" aria-label="Ver detalle del evento" onClick={() => setSelected(row)}>
            <Eye size={14} aria-hidden="true" />
          </button>
        )}
      />

      <Drawer
        isOpen={selected !== null}
        onClose={() => setSelected(null)}
        title="Detalle del evento"
        subtitle={selected ? formatoFecha.format(new Date(selected.fecha_hora)) : ''}
        size="md"
      >
        {selected && (
          <dl className="row g-2 small">
            <dt className="col-4 text-muted">Evento</dt><dd className="col-8">{selected.tipo_evento}</dd>
            <dt className="col-4 text-muted">Resultado</dt><dd className="col-8">{selected.resultado}</dd>
            <dt className="col-4 text-muted">Usuario</dt>
            <dd className="col-8">{selected.usuario_nombre ?? '—'} ({selected.numero_documento || '—'})</dd>
            <dt className="col-4 text-muted">IP</dt><dd className="col-8 font-monospace">{selected.ip_origen ?? '—'}</dd>
            <dt className="col-12 text-muted">Detalle</dt><dd className="col-12">{selected.detalles}</dd>
            {selected.payload_antes && (<>
              <dt className="col-12 text-muted">Antes</dt>
              <dd className="col-12"><pre className="joli-code-block">{JSON.stringify(selected.payload_antes, null, 2)}</pre></dd>
            </>)}
            {selected.payload_despues && (<>
              <dt className="col-12 text-muted">Después</dt>
              <dd className="col-12"><pre className="joli-code-block">{JSON.stringify(selected.payload_despues, null, 2)}</pre></dd>
            </>)}
          </dl>
        )}
      </Drawer>
    </div>
  );
}
```

Los payloads se muestran como texto (`<pre>` + `JSON.stringify`), nunca con `dangerouslySetInnerHTML`. Estilo del bloque:

```css
.joli-code-block {
  margin: 0;
  padding: var(--space-3);
  max-height: 320px;
  overflow: auto;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
}
```
