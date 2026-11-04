# Cargador Masivo de Archivos con Arrastrar y Soltar (`FileUploaderPro`)
## SDD Joli Foods — Spec-Driven Development

Este componente estandariza la carga de documentos de identidad, comprobantes de pago, evidencias fotográficas y anexos de auditoría, con validaciones previas a la subida.

> **Importante (seguridad):** las validaciones del navegador (tipo, tamaño, firma de bytes, hash) mejoran la experiencia y evitan subidas inútiles, pero se pueden saltar. El backend DEBE repetir todas las validaciones (tamaño, tipo real por firma de bytes, extensión permitida, antivirus si aplica) y DEBE calcular su propio hash; nunca debe confiar en el hash ni en el tipo enviados por el cliente.

---

## 1. Características técnicas

1. **Zona de arrastre (drag & drop)**: indicador visual al arrastrar y rechazo inmediato de tipos no permitidos. La zona DEBE ser operable con teclado (es un `<label>` del `<input type="file">`).
2. **Hash SHA-256 en el navegador (Web Crypto API)**: permite detectar duplicados antes de subir y mostrar una huella abreviada. El cálculo carga el archivo en memoria: para archivos de más de ~100 MB se DEBERÍA omitir o hacer en el servidor.
3. **Progreso y cancelación por archivo**: porcentaje individual (`onUploadProgress` de Axios) y cancelación con un `AbortController` por ítem.
4. **Validación por firma de bytes (*magic bytes*)**: se leen los primeros bytes del archivo para comprobar que su contenido corresponde al tipo declarado (un `.exe` renombrado a `.pdf` no tiene la firma `%PDF-`).
5. **Tamaño máximo por archivo** (ej. 25 MB) y número máximo de archivos.
6. **Subida autenticada**: usa el cliente HTTP `api` (token en memoria) y una ruta del catálogo `ENDPOINTS`. NO DEBE leer tokens de `localStorage` ni usar `fetch` directo.

---

## 2. Contrato de props (TypeScript)

```typescript
import type { AllowedMime } from '@/utils/fileUpload';

export type UploadStatus = 'idle' | 'validating' | 'hashing' | 'uploading' | 'completed' | 'error' | 'canceled';

export interface UploadedFileItem {
  id: string;
  file: File;
  name: string;
  sizeBytes: number;
  mimeType: string;
  sha256Hash?: string;
  progressPercent: number; // 0 a 100
  status: UploadStatus;
  errorMessage?: string;
  remoteId?: string;       // identificador devuelto por el backend
}

export interface FileUploaderProProps {
  /** Tipos MIME permitidos, ej. ['image/jpeg', 'image/png', 'application/pdf'] */
  acceptedTypes: AllowedMime[];
  maxFileSizeMb: number;
  maxFilesCount?: number;
  /** Ruta tomada de ENDPOINTS, ej. ENDPOINTS.ADJUNTOS.SUBIR */
  uploadEndpoint: string;
  onUploadSuccess: (completedFiles: UploadedFileItem[]) => void;
  allowMultiple?: boolean;
}
```

---

## 3. Utilidades de validación y subida (`fileUpload.ts`)

```typescript
// src/utils/fileUpload.ts
import type { AxiosProgressEvent } from 'axios';
import { api } from '@services/api';

/** Firmas de bytes conocidas. Los Office modernos (.xlsx/.docx) son ZIP: firma "PK\x03\x04". */
const MAGIC_SIGNATURES = {
  'application/pdf': [[0x25, 0x50, 0x44, 0x46, 0x2d]],                    // %PDF-
  'image/png': [[0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]],
  'image/jpeg': [[0xff, 0xd8, 0xff]],
  'image/webp': [[0x52, 0x49, 0x46, 0x46]],                               // RIFF (se verifica "WEBP" abajo)
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [[0x50, 0x4b, 0x03, 0x04]],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [[0x50, 0x4b, 0x03, 0x04]],
} as const satisfies Record<string, ReadonlyArray<ReadonlyArray<number>>>;

export type AllowedMime = keyof typeof MAGIC_SIGNATURES;

/** Devuelve true si los primeros bytes del archivo coinciden con la firma del tipo esperado. */
export async function matchesMagicBytes(file: File, expectedMime: AllowedMime): Promise<boolean> {
  const header = new Uint8Array(await file.slice(0, 16).arrayBuffer());
  const signatures = MAGIC_SIGNATURES[expectedMime];
  const startsWith = (sig: ReadonlyArray<number>) => sig.every((byte, i) => header[i] === byte);
  if (!signatures.some(startsWith)) return false;

  if (expectedMime === 'image/webp') {
    // Bytes 8..11 deben ser "WEBP"
    return header[8] === 0x57 && header[9] === 0x45 && header[10] === 0x42 && header[11] === 0x50;
  }
  return true;
}

/** Hash SHA-256 en hexadecimal (64 caracteres). Requiere contexto seguro (HTTPS o localhost). */
export async function sha256Hex(file: Blob): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', await file.arrayBuffer());
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, '0')).join('');
}

export interface ValidationResult {
  ok: boolean;
  error?: string;
}

/** Validación previa a la subida: tipo declarado, tamaño y firma real del contenido. */
export async function validateFile(
  file: File,
  acceptedTypes: AllowedMime[],
  maxFileSizeMb: number
): Promise<ValidationResult> {
  if (!acceptedTypes.includes(file.type as AllowedMime)) {
    return { ok: false, error: 'Tipo de archivo no permitido.' };
  }
  if (file.size === 0) {
    return { ok: false, error: 'El archivo está vacío.' };
  }
  if (file.size > maxFileSizeMb * 1024 * 1024) {
    return { ok: false, error: `El archivo supera el máximo de ${maxFileSizeMb} MB.` };
  }
  if (!(await matchesMagicBytes(file, file.type as AllowedMime))) {
    return { ok: false, error: 'El contenido del archivo no corresponde a su tipo.' };
  }
  return { ok: true };
}

/** Sube un archivo con progreso y cancelación. */
export async function uploadFile(
  endpoint: string,
  file: File,
  sha256: string,
  signal: AbortSignal,
  onProgress: (percent: number) => void
): Promise<{ id: string }> {
  const form = new FormData();
  form.append('archivo', file);
  form.append('sha256_cliente', sha256); // referencia; el servidor recalcula su propio hash

  const res = await api.post<{ id: string }>(endpoint, form, {
    signal,
    onUploadProgress: (e: AxiosProgressEvent) => {
      if (e.total) onProgress(Math.round((e.loaded / e.total) * 100));
    },
  });
  return res.data;
}
```

**Uso por ítem:** `validating` → `validateFile` → `hashing` → `sha256Hex` (y verificación de duplicados en la lista) → `uploading` → `uploadFile` con un `AbortController` guardado por `id` → `completed` o `error`. Al desmontar el componente se DEBEN abortar las subidas en curso (`controllers.forEach((c) => c.abort())` en la limpieza del `useEffect`).

---

## 4. Estructura HTML y clases CSS

```html
<div class="uploader-container">
  <!-- Zona de arrastre: el <label> hace que la zona sea operable con teclado y lector de pantalla -->
  <label class="uploader-dropzone uploader-dropzone--active" for="uploader-input">
    <span class="uploader-dropzone__icon" aria-hidden="true"><!-- icono lucide UploadCloud --></span>
    <span class="uploader-dropzone__title">Arrastra y suelta tus archivos aquí</span>
    <span class="uploader-dropzone__subtitle">O haz clic para buscarlos (PDF, PNG, JPG hasta 25 MB)</span>
    <input id="uploader-input" type="file" class="uploader-dropzone__input visually-hidden"
           accept="application/pdf,image/png,image/jpeg" multiple />
  </label>

  <!-- Lista de archivos en proceso -->
  <ul class="uploader-file-list" aria-live="polite">
    <li class="uploader-file-item uploader-file-item--completed">
      <span class="uploader-file-icon" aria-hidden="true"><!-- icono lucide FileText --></span>
      <div class="uploader-file-info">
        <div class="uploader-file-name">acta_entrega_firmada.pdf</div>
        <div class="uploader-file-meta">2.4 MB • Hash: 4a8b…9f12 • 100%</div>
        <div class="uploader-progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="100"
             aria-label="Progreso de acta_entrega_firmada.pdf">
          <div class="uploader-progress-fill" style="width: 100%"></div>
        </div>
      </div>
      <button type="button" class="btn-icon-remove" aria-label="Quitar acta_entrega_firmada.pdf" title="Quitar">
        <!-- icono lucide X -->
      </button>
    </li>
  </ul>
</div>
```

Los estilos de estas clases DEBEN usar tokens de `variables.css` (`--bg-card`, `--border-subtle`, `--brand-primary`, `--status-error`, etc.).
