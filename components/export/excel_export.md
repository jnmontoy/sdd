# Especificación de Utilidad y Componente: Exportación a Excel
## Ecosistema Jolifoods — Guía de Implementación SDD

La utilidad y botón de exportación `ExcelExport` permite a los usuarios corporativos descargar listados tabulares con formato limpio, nombres de archivo estandarizados y respeto estricto a los filtros aplicados (incluyendo los filtros tipo Excel).

---

### 1. Requisitos de Negocio
1. **Nomenclatura Estandarizada**:
   - Formato obligatorio: `[Modulo]_[YYYYMMDD]_[HHmmss].xlsx`
   - Ejemplo: `Usuarios_20260930_123000.xlsx` o `Bitacora_Auditoria_20260930_123000.xlsx`.
2. **Respeto a Filtros Activos**: Si el usuario aplicó filtros mediante el `ChecklistPopover` o el buscador general, la exportación debe procesar **únicamente el subconjunto de datos filtrados**, a menos que se ofrezca explícitamente "Exportar Todo".
3. **Formato Automático de Celdas**:
   - Cabeceras en negrita y centradas.
   - Ajuste automático de ancho de columna (*Auto-fit column widths*) para evitar texto truncado (`###`).
   - Fechas en formato `YYYY-MM-DD HH:mm:ss`.
   - Valores booleanos o estados exportados en español legible (`Activo` / `Inactivo`, `Exitoso` / `Fallido`).
4. **Doble Estrategia (Frontend / Backend)**:
   - **Frontend (< 5,000 registros)**: Generación instantánea en el navegador usando la biblioteca `xlsx` (SheetJS).
   - **Backend (> 5,000 registros)**: Streaming asíncrono desde FastAPI mediante `StreamingResponse` y `openpyxl`.

---

### 2. Implementación TypeScript / Frontend (`excelExport.ts`)

```tsx
// src/utils/excelExport.ts
import * as XLSX from 'xlsx';

export interface ExportColumn<T> {
  header: string;
  key: keyof T | string;
  formatter?: (value: any, row: T) => string | number | boolean;
  width?: number;
}

export interface ExportOptions<T> {
  filenamePrefix: string;
  sheetName?: string;
  columns: ExportColumn<T>[];
  data: T[];
}

export function exportToExcel<T>({
  filenamePrefix,
  sheetName = 'Datos',
  columns,
  data
}: ExportOptions<T>): void {
  // 1. Mapeo de datos con formateadores
  const formattedRows = data.map((row) => {
    const rowObj: Record<string, any> = {};
    columns.forEach((col) => {
      const rawValue = (row as any)[col.key];
      rowObj[col.header] = col.formatter ? col.formatter(rawValue, row) : (rawValue ?? '');
    });
    return rowObj;
  });

  // 2. Creación de la hoja de cálculo
  const worksheet = XLSX.utils.json_to_sheet(formattedRows);

  // 3. Ajuste de ancho de columnas
  const colWidths = columns.map((col) => {
    if (col.width) return { wch: col.width };
    // Calcular ancho máximo basado en cabecera y datos
    let maxLen = col.header.length;
    data.slice(0, 100).forEach((row) => {
      const val = (row as any)[col.key];
      const strVal = String(val ?? '');
      if (strVal.length > maxLen) maxLen = strVal.length;
    });
    return { wch: Math.min(Math.max(maxLen + 3, 12), 45) };
  });
  worksheet['!cols'] = colWidths;

  // 4. Creación del libro de trabajo
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);

  // 5. Generación de Timestamp Jolifoods
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  const timestamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(
    now.getHours()
  )}${pad(now.getMinutes())}${pad(now.getSeconds())}`;

  const fullFilename = `${filenamePrefix}_${timestamp}.xlsx`;

  // 6. Descarga del archivo
  XLSX.writeFile(workbook, fullFilename);
}
```

---

### 3. Componente de Botón `ExportExcelButton.tsx`

```tsx
// src/components/ui/ExportExcelButton.tsx
import React, { useState } from 'react';
import { FileSpreadsheet, Loader2 } from 'lucide-react';
import { exportToExcel, ExportColumn } from '../../utils/excelExport';
import { showToast } from './ToastNotification';

interface ExportExcelButtonProps<T> {
  filenamePrefix: string;
  columns: ExportColumn<T>[];
  getData: () => T[] | Promise<T[]>;
  totalCount?: number;
  className?: string;
}

export function ExportExcelButton<T>({
  filenamePrefix,
  columns,
  getData,
  totalCount,
  className = ''
}: ExportExcelButtonProps<T>) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    try {
      setIsExporting(true);
      const data = await Promise.resolve(getData());

      if (!data || data.length === 0) {
        showToast.warning('Sin datos para exportar', {
          description: 'No hay registros visibles o que cumplan con los filtros aplicados.'
        });
        return;
      }

      exportToExcel({
        filenamePrefix,
        columns,
        data
      });

      showToast.success('Archivo descargado con éxito', {
        description: `Se exportaron ${data.length.toLocaleString('es-CO')} registros a Excel.`
      });
    } catch (err: any) {
      console.error('Error al exportar Excel:', err);
      showToast.error('Fallo al exportar archivo', {
        description: 'Ocurrió un error inesperado al generar el archivo Excel.'
      });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      className={`btn-export-excel ${className}`}
      onClick={handleExport}
      disabled={isExporting}
      title="Exportar registros filtrados a formato Excel"
    >
      {isExporting ? (
        <Loader2 size={16} className="btn-spinner" />
      ) : (
        <FileSpreadsheet size={16} className="excel-icon" />
      )}
      <span>Exportar Excel {totalCount !== undefined ? `(${totalCount})` : ''}</span>
    </button>
  );
}
```

---

### 4. Estilos CSS (`export_button.css`)

```css
.btn-export-excel {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: var(--radius-sm, 6px);
  border: 1px solid #107C41;
  background: #107C41;
  color: #FFFFFF;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-export-excel:hover:not(:disabled) {
  background: #0E6835;
  border-color: #0E6835;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 124, 65, 0.2);
}

.btn-export-excel:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
}

.btn-export-excel .excel-icon {
  flex-shrink: 0;
}

.btn-export-excel .btn-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
```
