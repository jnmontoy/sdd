# Especificación de Componente: Modal de Firma Digitalizada (`SignatureModal`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

El componente `SignatureModal` proporciona un diálogo accesible para la captura de firmas manuscritas mediante pantalla táctil (smartphone, tablet) o cursor de ratón. Implementa un algoritmo inteligente de recorte de trazo (`cropToSignature`) para eliminar automáticamente los márgenes en blanco sobrantes antes de guardar la firma en formato Base64 (PNG transparente).

> **Origen y validación en producción**: Extraído y unificado a partir de las implementaciones operativas en `tiendita` y `app_tic` para entrega de EPPs, remisiones, actas de entrega TIC y autorizaciones.

---

### 1. Requisitos Técnicos y de Negocio

1. **Multi-dispositivo**: Soporte simultáneo para eventos `PointerEvent`, `TouchEvent` y `MouseEvent`.
2. **Auto-recorte (`Bounding Box`)**: Identifica el primer y último píxel dibujado en cada eje y genera un Canvas recortado para no almacenar lienzo en blanco innecesario en la base de datos.
3. **Validación de trazo mínimo**: Previene el envío accidental de lienzos en blanco o toques accidentales de un solo píxel.
4. **Desacople vía Portal**: Se renderiza en `document.body` mediante `createPortal` para evitar conflictos de z-index o stacking context.
5. **Herramientas integradas**: Botón de "Borrar / Limpiar" (`Eraser`) y botón de confirmación "Guardar Firma" (`Check`).

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/SignatureModal.tsx
import React, { useRef, useEffect, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { Eraser, Check, X } from 'lucide-react';
import './SignatureModal.css';

const ALPHA_THRESHOLD = 10;

/**
 * Recorta el canvas al bounding box real del trazo para exportar
 * la firma sin el espacio en blanco sobrante alrededor.
 */
export function cropToSignature(sourceCanvas: HTMLCanvasElement): string {
  const ctx = sourceCanvas.getContext('2d');
  if (!ctx) return sourceCanvas.toDataURL('image/png');

  const { width, height } = sourceCanvas;
  const { data } = ctx.getImageData(0, 0, width, height);

  let minX = width;
  let minY = height;
  let maxX = -1;
  let maxY = -1;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const alpha = data[(y * width + x) * 4 + 3];
      if (alpha > ALPHA_THRESHOLD) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }

  // Si no hay trazo válido, retorna cadena vacía o dataUrl
  if (maxX < minX || maxY < minY) {
    return sourceCanvas.toDataURL('image/png');
  }

  const croppedWidth = maxX - minX + 1;
  const croppedHeight = maxY - minY + 1;
  const croppedCanvas = document.createElement('canvas');
  croppedCanvas.width = croppedWidth;
  croppedCanvas.height = croppedHeight;

  const croppedCtx = croppedCanvas.getContext('2d');
  if (!croppedCtx) return sourceCanvas.toDataURL('image/png');

  croppedCtx.drawImage(
    sourceCanvas,
    minX,
    minY,
    croppedWidth,
    croppedHeight,
    0,
    0,
    croppedWidth,
    croppedHeight
  );
  return croppedCanvas.toDataURL('image/png');
}

export interface SignatureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (signatureBase64: string) => void;
  title?: string;
  initialSignature?: string | null;
}

export const SignatureModal: React.FC<SignatureModalProps> = ({
  isOpen,
  onClose,
  onSave,
  title = 'Registrar Firma del Colaborador',
  initialSignature,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasStroke, setHasStroke] = useState(false);

  const initCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Escalar para pantallas Retina / High-DPI
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    ctx.strokeStyle = '#1E293B';
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    if (initialSignature) {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, rect.width, rect.height);
        setHasStroke(true);
      };
      img.src = initialSignature;
    }
  }, [initialSignature]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(initCanvas, 50);
    } else {
      setHasStroke(false);
    }
  }, [isOpen, initCanvas]);

  const getPos = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    e.currentTarget.setPointerCapture(e.pointerId);
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    const { x, y } = getPos(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
    setHasStroke(true);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    const { x, y } = getPos(e);
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    setIsDrawing(false);
    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch {}
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setHasStroke(false);
  };

  const handleSave = () => {
    if (!canvasRef.current || !hasStroke) return;
    const cropped = cropToSignature(canvasRef.current);
    onSave(cropped);
    onClose();
  };

  if (!isOpen) return null;

  return createPortal(
    <div className="sig-modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div className="sig-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="sig-modal-header">
          <h3 className="sig-modal-title">{title}</h3>
          <button type="button" className="sig-modal-close" onClick={onClose} aria-label="Cerrar">
            <X size={20} />
          </button>
        </div>

        <div className="sig-canvas-wrapper">
          <canvas
            ref={canvasRef}
            className="sig-canvas"
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
          />
          <div className="sig-baseline-guide" aria-hidden="true" />
          <p className="sig-instruction">Firme sobre la línea utilizando el dedo o ratón</p>
        </div>

        <div className="sig-modal-footer">
          <button type="button" className="sig-btn sig-btn-clear" onClick={handleClear} disabled={!hasStroke}>
            <Eraser size={16} />
            <span>Limpiar</span>
          </button>

          <div className="sig-modal-actions">
            <button type="button" className="sig-btn sig-btn-cancel" onClick={onClose}>
              Cancelar
            </button>
            <button type="button" className="sig-btn sig-btn-confirm" onClick={handleSave} disabled={!hasStroke}>
              <Check size={16} />
              <span>Guardar Firma</span>
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};
```

---

### 3. Estilos CSS (`SignatureModal.css`)

```css
.sig-modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: var(--z-modal, 1050);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.sig-modal-content {
  background: var(--bg-card, #FFFFFF);
  border: 1px solid var(--border-subtle, #E2E8F0);
  border-radius: var(--radius-xl, 14px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 540px;
  overflow: hidden;
  animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.95) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.sig-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle, #E2E8F0);
}

.sig-modal-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  margin: 0;
}

.sig-modal-close {
  background: transparent;
  border: none;
  color: var(--text-muted, #94A3B8);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
}

.sig-modal-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-primary, #0F172A);
}

.sig-canvas-wrapper {
  position: relative;
  padding: 1.5rem;
  background: #F8FAFC;
}

.sig-canvas {
  width: 100%;
  height: 220px;
  background: #FFFFFF;
  border: 1.5px dashed #CBD5E1;
  border-radius: 8px;
  touch-action: none;
  cursor: crosshair;
}

.sig-baseline-guide {
  position: absolute;
  bottom: 3.5rem;
  left: 3rem;
  right: 3rem;
  height: 1px;
  background: #E2E8F0;
  pointer-events: none;
}

.sig-instruction {
  margin: 0.5rem 0 0 0;
  font-size: 0.75rem;
  color: var(--text-muted, #64748B);
  text-align: center;
}

.sig-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-subtle, #E2E8F0);
  background: var(--bg-surface, #FAFAFA);
}

.sig-modal-actions {
  display: flex;
  gap: 0.625rem;
}

.sig-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.sig-btn-clear {
  background: transparent;
  border: 1px solid var(--border-subtle, #E2E8F0);
  color: var(--text-secondary, #475569);
}

.sig-btn-clear:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.sig-btn-cancel {
  background: transparent;
  border: 1px solid var(--border-subtle, #E2E8F0);
  color: var(--text-secondary, #475569);
}

.sig-btn-confirm {
  background: var(--color-primary, #10B981);
  color: #FFFFFF;
  border: none;
}

.sig-btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sig-btn-confirm:hover:not(:disabled) {
  background: #059669;
}
```
