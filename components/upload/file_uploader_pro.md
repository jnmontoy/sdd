# Cargador Masivo de Archivos con Drag & Drop (`FileUploaderPro`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este componente estandariza la carga de documentos de identidad, comprobantes de pago, evidencias fotográficas de contenedores y anexos de auditoría con validación de seguridad previa a la subida.

---

## 1. Características Técnicas Obligatorias

1. **Zona de Arrastre Inteligente (Drag & Drop Zone)**: Indicador visual reactivo al arrastrar sobre el área, con rechazo inmediato de extensiones no autorizadas.
2. **Cálculo de Hash en el Navegador (Web Crypto API)**:
   - Genera el hash SHA-256 del archivo localmente antes de iniciar el streaming al backend, permitiendo deduplicación instantánea y verificación de integridad.
3. **Progreso Individual y Agrupado**:
   - Barra de porcentaje individual por archivo + tiempo restante estimado.
   - Cancelación independiente con `AbortController` por ítem.
4. **Validación Estricta de Seguridad**:
   - Inspección de cabeceras mágicas (*Magic Bytes*) para impedir ejecutables camuflados como imágenes o PDF.
   - Restricción de peso máximo por archivo (ej. máx 25 MB).

---

## 2. Contrato de Props en TypeScript

```typescript
export interface UploadedFileItem {
  id: string;
  file: File;
  name: string;
  sizeBytes: number;
  mimeType: string;
  sha256Hash?: string;
  progressPercent: number; // 0 a 100
  status: 'idle' | 'hashing' | 'uploading' | 'completed' | 'error';
  errorMessage?: string;
  remoteUrl?: string;
}

export interface FileUploaderProProps {
  acceptedTypes: string[]; // Ej: ['image/jpeg', 'image/png', 'application/pdf', '.xlsx']
  maxFileSizeMb: number;
  maxFilesCount?: number;
  uploadEndpointUrl: string;
  onUploadSuccess: (completedFiles: UploadedFileItem[]) => void;
  allowMultiple?: boolean;
}
```

---

## 3. Estructura HTML y Clases CSS

```html
<div class="uploader-container">
  <!-- Zona Drag & Drop -->
  <div class="uploader-dropzone uploader-dropzone--active">
    <div class="uploader-dropzone__icon">📁</div>
    <h4 class="uploader-dropzone__title">Arrastra y suelta tus archivos aquí</h4>
    <p class="uploader-dropzone__subtitle">O haz clic para explorar tus carpetas (PDF, PNG, JPG hasta 25 MB)</p>
    <input type="file" class="uploader-dropzone__input" multiple />
  </div>

  <!-- Lista de Archivos en Proceso -->
  <div class="uploader-file-list">
    <div class="uploader-file-item uploader-file-item--completed">
      <div class="uploader-file-icon">📄</div>
      <div class="uploader-file-info">
        <div class="uploader-file-name">acta_entrega_firmada.pdf</div>
        <div class="uploader-file-meta">2.4 MB • Hash: 4a8b...9f12 • 100%</div>
        <div class="uploader-progress-bar"><div class="uploader-progress-fill" style="width: 100%"></div></div>
      </div>
      <button class="btn-icon-remove">✕</button>
    </div>
  </div>
</div>
```
