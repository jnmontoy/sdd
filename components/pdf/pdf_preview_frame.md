# Especificación de Componente: Previsualizador PDF en Canvas (`PdfPreviewFrame`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

El componente `PdfPreviewFrame` renderiza documentos PDF recibidos en formato `Blob` directamente sobre elementos `<canvas>` de HTML5 (utilizando `pdfjs-dist`), simulando hojas físicas apiladas con sombras realistas, paginación continua por scroll y controles de zoom gradual interactivo.

> **Origen y validación en producción**: Extraído del módulo de entrega y retiro de dotación en `tiendita` para comprobantes de nómina, certificados y facturas.

---

### 1. Requisitos Técnicos y Dependencias

- **Librería base**: `pdfjs-dist` (`npm install pdfjs-dist`).
- **Renderizado por Hojas**: Cada página del PDF se renderiza en un Canvas independiente montado dentro de una tarjeta con sombra y numeración flotante.
- **Controles de Zoom**: Botones de Acercar (`+`), Alejar (`-`) y Reset al 100%, con ajuste fluido por `ResizeObserver`.
- **Estados de Carga y Error**: Spinner giratorio corporativo durante la rasterización y mensaje constructivo con botón de reintento ante fallos de descarga.

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/PdfPreviewFrame.tsx
import React, { useEffect, useRef, useState } from 'react';
import { FileText, Loader2, AlertTriangle, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';
import './PdfPreviewFrame.css';

// Configuración del worker de PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

export interface PdfPreviewFrameProps {
  previewBlob: Blob | null;
  isLoading: boolean;
  error?: string | null;
  emptyMessage?: string;
}

export const PdfPreviewFrame: React.FC<PdfPreviewFrameProps> = ({
  previewBlob,
  isLoading,
  error,
  emptyMessage = 'No hay ningún documento disponible para previsualizar.',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [pages, setPages] = useState<string[]>([]);
  const [isRendering, setIsRendering] = useState(false);
  const [scale, setScale] = useState(1.0);
  const [renderError, setRenderError] = useState<string | null>(null);

  useEffect(() => {
    if (!previewBlob) {
      setPages([]);
      return;
    }

    let isMounted = true;
    setIsRendering(true);
    setRenderError(null);

    const loadPdf = async () => {
      try {
        const arrayBuffer = await previewBlob.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        const renderedPages: string[] = [];

        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const viewport = page.getViewport({ scale: 1.5 });
          const canvas = document.createElement('canvas');
          const context = canvas.getContext('2d');

          if (!context) continue;

          canvas.height = viewport.height;
          canvas.width = viewport.width;

          await page.render({ canvasContext: context, viewport }).promise;
          renderedPages.push(canvas.toDataURL('image/png'));
        }

        if (isMounted) {
          setPages(renderedPages);
          setIsRendering(false);
        }
      } catch (err: any) {
        if (isMounted) {
          console.error('[PdfPreviewFrame] Error al renderizar PDF:', err);
          setRenderError(err.message || 'Error al procesar el archivo PDF');
          setIsRendering(false);
        }
      }
    };

    loadPdf();

    return () => {
      isMounted = false;
    };
  }, [previewBlob]);

  const zoomIn = () => setScale((s) => Math.min(s + 0.15, 2.0));
  const zoomOut = () => setScale((s) => Math.max(s - 0.15, 0.6));
  const zoomReset = () => setScale(1.0);

  if (isLoading || isRendering) {
    return (
      <div className="pdf-frame-state">
        <Loader2 className="animate-spin text-emerald-600" size={36} />
        <p className="pdf-frame-text">Generando vista previa del documento...</p>
      </div>
    );
  }

  if (error || renderError) {
    return (
      <div className="pdf-frame-state pdf-frame-error">
        <AlertTriangle size={36} className="text-amber-500" />
        <p className="pdf-frame-text">{error || renderError}</p>
      </div>
    );
  }

  if (!previewBlob || pages.length === 0) {
    return (
      <div className="pdf-frame-state">
        <FileText size={40} className="text-slate-400" />
        <p className="pdf-frame-text">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="pdf-preview-wrapper" ref={containerRef}>
      {/* Barra de Controles de Zoom Flotante */}
      <div className="pdf-zoom-bar">
        <button type="button" onClick={zoomOut} title="Alejar" aria-label="Alejar">
          <ZoomOut size={16} />
        </button>
        <span className="pdf-zoom-label">{Math.round(scale * 100)}%</span>
        <button type="button" onClick={zoomIn} title="Acercar" aria-label="Acercar">
          <ZoomIn size={16} />
        </button>
        <button type="button" onClick={zoomReset} title="Restablecer" aria-label="Restablecer">
          <RotateCcw size={15} />
        </button>
      </div>

      {/* Visor con Hojas Apiladas */}
      <div className="pdf-pages-scroll">
        {pages.map((dataUrl, idx) => (
          <div
            key={idx}
            className="pdf-page-sheet"
            style={{ transform: `scale(${scale})`, transformOrigin: 'top center' }}
          >
            <img src={dataUrl} alt={`Página ${idx + 1}`} className="pdf-page-image" />
            <span className="pdf-page-number">Página {idx + 1} de {pages.length}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

### 3. Estilos CSS (`PdfPreviewFrame.css`)

```css
.pdf-preview-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 520px;
  background: #E2E8F0;
  border-radius: var(--radius-lg, 10px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.pdf-zoom-bar {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  padding: 0.35rem 0.6rem;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.pdf-zoom-bar button {
  background: transparent;
  border: none;
  color: #FFFFFF;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.pdf-zoom-bar button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.pdf-zoom-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #F8FAFC;
  padding: 0 0.25rem;
}

.pdf-pages-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 2.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.pdf-page-sheet {
  position: relative;
  background: #FFFFFF;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  transition: transform 0.15s ease-out;
}

.pdf-page-image {
  display: block;
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.pdf-page-number {
  position: absolute;
  bottom: -1.5rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  color: #64748B;
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
  background: #F8FAFC;
  border: 1px dashed #CBD5E1;
  border-radius: var(--radius-lg, 10px);
}

.pdf-frame-text {
  font-size: 0.875rem;
  color: #64748B;
  margin: 0;
}
```
