# Especificación de Utilidad y Componente: Exportación a Excel
## SDD Joli Foods — Guía de implementación

La utilidad `exportToExcel` y el botón `ExportExcelButton` permiten descargar listados en `.xlsx` con nombre de archivo estandarizado y respetando los filtros aplicados (incluidos los filtros tipo Excel por columna).

---

### 1. Requisitos de negocio

1. **Nombre de archivo**: `[Modulo]_[AAAAMMDD]_[HHmmss].xlsx` (hora local). Ej.: `Usuarios_20260930_123000.xlsx`.
2. **Respeto a filtros**: si el usuario filtró (buscador o `ChecklistPopover`), se exporta **solo el subconjunto filtrado**, salvo que se ofrezca explícitamente "Exportar todo".
3. **Formato de celdas**:
   - Ancho de columna ajustado al contenido (evita `###`).
   - Fechas como `AAAA-MM-DD HH:mm:ss`; booleanos y estados en español (`Activo` / `Inactivo`).
   - Los estilos de celda (negrita, centrado, colores) **no** están disponibles en la edición comunitaria de SheetJS; si se requieren, la exportación DEBE hacerse en el backend con `openpyxl`.
4. **Seguridad — inyección de fórmulas (DEBE)**: un texto que empiece por `=`, `+`, `-`, `@`, tabulador o retorno de carro se ejecuta como fórmula al abrir el archivo (*CSV/Formula Injection*). Todo valor de texto se exporta neutralizado con un apóstrofo inicial.
5. **Dos estrategias**:
   - **Navegador (hasta ~5.000 filas)**: biblioteca SheetJS (`xlsx`).
   - **Backend (más de ~5.000 filas o con estilos)**: FastAPI con `StreamingResponse` y `openpyxl` en modo `write_only`, lanzado como tarea si tarda (ver [`js_polling_architecture.md`](../realtime/js_polling_architecture.md)).
6. **Dependencia (DEBE)**: el paquete `xlsx` publicado en el registro público de npm quedó congelado en la versión 0.18.5, que tiene vulnerabilidades conocidas (CVE-2023-30533, contaminación de prototipo, y CVE-2024-22363, ReDoS). Se instala desde la distribución oficial de SheetJS:
   ```bash
   npm install https://cdn.sheetjs.com/xlsx-0.20.3/xlsx-0.20.3.tgz
   ```

---

### 2. Utilidad TypeScript (`excelExport.ts`)

```typescript
// src/utils/excelExport.ts
import * as XLSX from 'xlsx';

export type CellValue = string | number | boolean | Date | null | undefined;

export interface ExportColumn<T> {
  header: string;
  /** Lectura del valor; usar una función si el dato está anidado o calculado. */
  value: keyof T | ((row: T) => CellValue);
  /** Formato de presentación (ej. estado legible). Recibe el valor ya leído. */
  formatter?: (value: CellValue, row: T) => CellValue;
  width?: number;
}

export interface ExportOptions<T> {
  filenamePrefix: string;
  sheetName?: string;
  columns: ExportColumn<T>[];
  data: T[];
}

const FORMULA_PREFIX = /^[=+\-@\t\r]/;

/** Neutraliza textos que Excel interpretaría como fórmula. */
function sanitizeCell(value: CellValue): CellValue {
  if (typeof value === 'string' && FORMULA_PREFIX.test(value)) return `'${value}`;
  return value;
}

const pad = (n: number) => String(n).padStart(2, '0');

function formatDate(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function readValue<T>(row: T, col: ExportColumn<T>): CellValue {
  const raw = typeof col.value === 'function' ? col.value(row) : (row[col.value] as CellValue);
  const formatted = col.formatter ? col.formatter(raw, row) : raw;
  if (formatted instanceof Date) return formatDate(formatted);
  return sanitizeCell(formatted ?? '');
}

export function exportToExcel<T>({ filenamePrefix, sheetName = 'Datos', columns, data }: ExportOptions<T>): void {
  // 1. Matriz de celdas (encabezado + filas) ya formateadas y saneadas
  const header = columns.map((c) => c.header);
  const rows = data.map((row) => columns.map((col) => readValue(row, col)));
  const worksheet = XLSX.utils.aoa_to_sheet([header, ...rows]);

  // 2. Ancho de columnas a partir de los valores ya formateados (muestra de 200 filas)
  worksheet['!cols'] = columns.map((col, idx) => {
    if (col.width) return { wch: col.width };
    const maxLen = rows.slice(0, 200).reduce((max, r) => Math.max(max, String(r[idx] ?? '').length), col.header.length);
    return { wch: Math.min(Math.max(maxLen + 2, 10), 50) };
  });

  // 3. Libro y descarga
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName.slice(0, 31)); // Excel limita el nombre a 31 caracteres

  const now = new Date();
  const timestamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  XLSX.writeFile(workbook, `${filenamePrefix}_${timestamp}.xlsx`);
}
```

---

### 3. Botón `ExportExcelButton.tsx`

En barras de herramientas compactas se usa el icono `FileSpreadsheet` dentro del grupo de acciones de 28px (ver `button/icon_action_group.md`); este botón con texto es para vistas donde la exportación es la acción principal.

```tsx
// src/components/ui/ExportExcelButton.tsx
import React, { useState } from 'react';
import { FileSpreadsheet, Loader2 } from 'lucide-react';
import { exportToExcel, type ExportColumn } from '@/utils/excelExport';
import { showToast } from '@/components/ui/ToastNotification';
import './ExportExcelButton.css';

interface ExportExcelButtonProps<T> {
  filenamePrefix: string;
  columns: ExportColumn<T>[];
  /** Devuelve las filas filtradas a exportar (puede consultar al backend). */
  getData: () => T[] | Promise<T[]>;
  totalCount?: number;
  className?: string;
}

export function ExportExcelButton<T>({ filenamePrefix, columns, getData, totalCount, className = '' }: ExportExcelButtonProps<T>) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const data = await getData();
      if (data.length === 0) {
        showToast.warning('Sin datos para exportar', {
          description: 'No hay registros que cumplan con los filtros aplicados.',
        });
        return;
      }
      exportToExcel({ filenamePrefix, columns, data });
      showToast.success('Archivo generado', {
        description: `Se exportaron ${data.length.toLocaleString('es-CO')} registros.`,
      });
    } catch (err: unknown) {
      console.error('[ExportExcelButton] Error al exportar:', err);
      showToast.error('No fue posible generar el archivo Excel');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      type="button"
      className={`btn-export-excel ${className}`}
      onClick={handleExport}
      disabled={isExporting}
      aria-busy={isExporting}
      title="Exportar los registros filtrados a Excel"
    >
      {isExporting ? <Loader2 size={16} className="btn-spinner" aria-hidden="true" /> : <FileSpreadsheet size={16} aria-hidden="true" />}
      <span>Exportar Excel{totalCount !== undefined ? ` (${totalCount.toLocaleString('es-CO')})` : ''}</span>
    </button>
  );
}
```

---

### 4. Estilos (`ExportExcelButton.css`)

El verde de Excel se toma del token `--accent-excel` de `variables.css`.

```css
.btn-export-excel {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 8px 14px;
  font-size: 13px;
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-sm);
  border: 1px solid var(--accent-excel);
  background: var(--accent-excel);
  color: var(--text-on-brand);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast);
}

.btn-export-excel:hover:not(:disabled) {
  background: var(--accent-excel-hover);
  border-color: var(--accent-excel-hover);
}

.btn-export-excel:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.btn-export-excel:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-export-excel .btn-spinner {
  animation: joliSpin 1s linear infinite;
}

@keyframes joliSpin {
  to { transform: rotate(360deg); }
}
```
