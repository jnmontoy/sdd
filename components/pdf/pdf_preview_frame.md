# Especificación de Componente: Previsualizador PDF (`PdfPreviewFrame`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de tiendita (entrega y retiro de dotación: comprobantes, certificados y actas). Aquí se describe de forma genérica.

`PdfPreviewFrame` muestra un PDF recibido como `Blob` dibujando cada página en `<canvas>` con `pdfjs-dist` (PDF.js), como hojas apiladas con sombra, desplazamiento continuo y zoom.

---

### 1. Requisitos técnicos y dependencias

- **Librería**: `pdfjs-dist` (versión 4 o superior).
- **Worker local (DEBE)**: el *worker* de PDF.js se empaqueta con la app (Vite `?url`), no se descarga de un CDN externo.
  - **Por qué:** un CDN externo es una dependencia de terceros en tiempo de ejecución (disponibilidad, integridad y política CSP) y debe coincidir exactamente con la versión instalada.
- **Una hoja por página**: cada página se renderiza a una imagen y se muestra en una tarjeta con su número.
- **Zoom real**: acercar/alejar cambia el ancho de la hoja (el contenido se reacomoda y el scroll funciona), no un `transform: scale` que encima las páginas.
- **Liberación de memoria (DEBE)**: al cambiar de documento o desmontar se cancela la carga en curso y se destruye el documento PDF (`loadingTask.destroy()`); así no quedan workers ni memoria retenida.
- **Estados**: cargando, error con botón "Reintentar" y vacío.
- **Límite**: para documentos muy largos (más de ~50 páginas) DEBERÍA renderizarse por demanda (solo las páginas visibles, con `IntersectionObserver`).

---

### 2. Implementación React + TypeScript

```tsx
// src/components/ui/PdfPreviewFrame.tsx
import React, { useEffect, useState } from 'react';
import { FileText, Loader2, AlertTriangle, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
import './PdfPreviewFrame.css';

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

export interface PdfPreviewFrameProps {
  previewBlob: Blob | null;
  isLoading?: boolean;
  error?: string | null;
  emptyMessage?: string;
  /** Escala de rasterizado (calidad). 1.5 equilibra nitidez y memoria. */
  renderScale?: number;
}

const MIN_ZOOM = 0.6;
const MAX_ZOOM = 2.0;
const ZOOM_STEP = 0.15;

export const PdfPreviewFrame: React.FC<PdfPreviewFrameProps> = ({
  previewBlob,
  isLoading = false,
  error,
  emptyMessage = 'No hay ningún documento para previsualizar.',
  renderScale = 1.5,
}) => {
  const [pages, setPages] = useState<string[]>([]);
  const [isRendering, setIsRendering] = useState(false);
  const [zoom, setZoom] = useState(1.0);
  const [renderError, setRenderError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0); // "Reintentar" incrementa y vuelve a renderizar

  useEffect(() => {
    if (!previewBlob) {
      setPages([]);
      return;
    }

    let cancelled = false;
    let loadingTask: ReturnType<typeof pdfjsLib.getDocument> | null = null;
    setIsRendering(true);
    setRenderError(null);

    (async () => {
      try {
        const data = new Uint8Array(await previewBlob.arrayBuffer());
        loadingTask = pdfjsLib.getDocument({ data });
        const pdf = await loadingTask.promise;
        const rendered: string[] = [];

        for (let i = 1; i <= pdf.numPages; i++) {
          if (cancelled) return;
          const page = await pdf.getPage(i);
          const viewport = page.getViewport({ scale: renderScale });
          const canvas = document.createElement('canvas');
          const context = canvas.getContext('2d');
          if (!context) continue;
          canvas.width = Math.floor(viewport.width);
          canvas.height = Math.floor(viewport.height);
          await page.render({ canvasContext: context, viewport }).promise;
          rendered.push(canvas.toDataURL('image/png'));
          page.cleanup();
          canvas.width = 0; // libera la memoria del canvas temporal
        }

        if (!cancelled) setPages(rendered);
      } catch (err: unknown) {
        if (!cancelled) {
          console.error('[PdfPreviewFrame] Error al renderizar PDF:', err);
          setRenderError('No fue posible mostrar el documento PDF.');
        }
      } finally {
        if (!cancelled) setIsRendering(false);
      }
    })();

    return () => {
      cancelled = true;
      void loadingTask?.destroy(); // cancela la carga y libera el documento y el worker
    };
  }, [previewBlob, renderScale, attempt]);

  const zoomIn = () => setZoom((z) => Math.min(+(z + ZOOM_STEP).toFixed(2), MAX_ZOOM));
  const zoomOut = () => setZoom((z) => Math.max(+(z - ZOOM_STEP).toFixed(2), MIN_ZOOM));

  if (isLoading || isRendering) {
    return (
      <div className="pdf-frame-state" role="status">
        <Loader2 className="pdf-frame-spinner" size={36} aria-hidden="true" />
        <p className="pdf-frame-text">Generando vista previa del documento…</p>
      </div>
    );
  }

  if (error || renderError) {
    return (
      <div className="pdf-frame-state pdf-frame-error" role="alert">
        <AlertTriangle size={36} className="pdf-frame-error-icon" aria-hidden="true" />
        <p className="pdf-frame-text">{error || renderError}</p>
        {renderError && (
          <button type="button" className="btn btn-outline-secondary btn-sm" onClick={() => setAttempt((a) => a + 1)}>
            Reintentar
          </button>
        )}
      </div>
    );
  }

  if (!previewBlob || pages.length === 0) {
    return (
      <div className="pdf-frame-state">
        <FileText size={40} className="pdf-frame-empty-icon" aria-hidden="true" />
        <p className="pdf-frame-text">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="pdf-preview-wrapper">
      <div className="btn-group btn-group-sm pdf-zoom-bar" role="group" aria-label="Zoom del documento">
        <button type="button" onClick={zoomOut} disabled={zoom <= MIN_ZOOM} title="Alejar" aria-label="Alejar">
          <ZoomOut size={16} aria-hidden="true" />
        </button>
        <span className="pdf-zoom-label" aria-live="polite">{Math.round(zoom * 100)}%</span>
        <button type="button" onClick={zoomIn} disabled={zoom >= MAX_ZOOM} title="Acercar" aria-label="Acercar">
          <ZoomIn size={16} aria-hidden="true" />
        </button>
        <button type="button" onClick={() => setZoom(1.0)} title="Restablecer zoom" aria-label="Restablecer zoom">
          <RotateCcw size={15} aria-hidden="true" />
        </button>
      </div>

      <div className="pdf-pages-scroll">
        {pages.map((dataUrl, idx) => (
          <figure
            key={`page-${idx + 1}`}
            className="pdf-page-sheet"
            style={{ width: `min(${Math.round(zoom * 100)}%, ${Math.round(820 * zoom)}px)` }}
          >
            <img src={dataUrl} alt={`Página ${idx + 1} de ${pages.length}`} className="pdf-page-image" />
            <figcaption className="pdf-page-number">Página {idx + 1} de {pages.length}</figcaption>
          </figure>
        ))}
      </div>
    </div>
  );
};
```

---

### 3. Estilos CSS (`PdfPreviewFrame.css`)

La hoja es "papel" (`--surface-paper`, blanco en ambos temas) y la barra de zoom flota sobre el documento (`--overlay-*`).

```css
.pdf-preview-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 520px;
  background: var(--bg-viewport);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.pdf-zoom-bar {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  z-index: var(--z-card);
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--overlay-surface);
  backdrop-filter: blur(8px);
  padding: 0.35rem 0.6rem;
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-card);
}

.pdf-zoom-bar button {
  background: transparent;
  border: none;
  color: var(--text-on-overlay);
  padding: 4px 6px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
}

.pdf-zoom-bar button:hover:not(:disabled) {
  background: var(--overlay-control-hover);
}

.pdf-zoom-bar button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pdf-zoom-bar button:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.pdf-zoom-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--text-on-overlay);
  padding: 0 0.25rem;
  min-width: 3.2em;
  text-align: center;
}

.pdf-pages-scroll {
  flex: 1;
  overflow: auto;
  padding: 2.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2.5rem;
}

.pdf-page-sheet {
  position: relative;
  margin: 0;
  max-width: none;
  background: var(--surface-paper);
  box-shadow: var(--shadow-card);
  border-radius: var(--radius-sm);
  transition: width var(--transition-fast);
}

.pdf-page-image {
  display: block;
  width: 100%;
  height: auto;
  border-radius: var(--radius-sm);
}

.pdf-page-number {
  position: absolute;
  bottom: -1.6rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  white-space: nowrap;
}

.pdf-frame-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  gap: 0.75rem;
  background: var(--bg-elevated);
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius-lg);
}

.pdf-frame-spinner {
  color: var(--brand-primary);
  animation: joliSpin 1s linear infinite;
}

.pdf-frame-error-icon {
  color: var(--status-warning);
}

.pdf-frame-empty-icon {
  color: var(--text-muted);
}

.pdf-frame-text {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  margin: 0;
}

@keyframes joliSpin {
  to { transform: rotate(360deg); }
}
```
