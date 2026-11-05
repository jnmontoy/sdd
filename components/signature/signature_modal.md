# Especificación de Componente: Modal de Firma Manuscrita (`SignatureModal`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de tiendita y app_tic (entrega de EPP, remisiones, actas de entrega de equipos y autorizaciones). Aquí se describe de forma genérica.

`SignatureModal` es un diálogo para capturar una firma manuscrita con el dedo, lápiz o mouse. Recorta automáticamente los márgenes vacíos (`cropToSignature`) y entrega la firma como PNG con fondo transparente en Base64. Es una de las excepciones permitidas de modal centrado (firmas).

> **Valor legal:** una firma dibujada es una **firma electrónica** (Ley 527 de 1999 y Decreto 2364 de 2012), no una "firma digital" con certificado. Su valor probatorio depende de poder demostrar quién firmó, cuándo y qué documento; ver [`multi_party_signature.md`](./multi_party_signature.md).

---

### 1. Requisitos técnicos y de negocio

1. **Multi-dispositivo**: usa `PointerEvent`, que unifica mouse, toque y lápiz. `touch-action: none` en el lienzo evita que la página se desplace mientras se firma.
2. **Alta densidad de píxeles**: el lienzo se escala con `devicePixelRatio` para que el trazo se vea nítido.
3. **Recorte automático**: se calcula el rectángulo que contiene el trazo y se exporta solo esa zona (más un pequeño margen).
4. **Trazo mínimo (DEBE)**: no se permite guardar un lienzo vacío ni un toque accidental; el recorte debe medir al menos 20 × 10 px.
5. **Portal**: se renderiza en `document.body` con `createPortal` para evitar problemas de `z-index`.
6. **Accesibilidad**: `role="dialog"`, `aria-modal`, `aria-labelledby`, cierre con `Escape`, foco inicial en el lienzo y devuelto al botón que abrió el modal. El clic en el fondo NO cierra el modal (se perdería la firma). Como dibujar no es posible para todas las personas, el flujo DEBERÍA ofrecer una alternativa (p. ej. confirmación con nombre y documento registrada en auditoría).
7. **Color del trazo**: tinta oscura fija (`--ink-signature`) porque la firma se imprime sobre papel blanco; el lienzo usa fondo `--surface-paper` en ambos temas.

---

### 2. Implementación React + TypeScript

```tsx
// src/components/ui/SignatureModal.tsx
import React, { useCallback, useEffect, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Eraser, Check, X } from 'lucide-react';
import './SignatureModal.css';

const ALPHA_THRESHOLD = 10;
const MIN_SIGNATURE_W = 20;
const MIN_SIGNATURE_H = 10;
const CROP_PADDING = 4;

/**
 * Recorta el canvas al rectángulo real del trazo.
 * Devuelve null si no hay trazo suficiente (lienzo vacío o toque accidental).
 */
export function cropToSignature(source: HTMLCanvasElement): string | null {
  const ctx = source.getContext('2d');
  if (!ctx) return null;

  const { width, height } = source;
  const { data } = ctx.getImageData(0, 0, width, height);
  let minX = width, minY = height, maxX = -1, maxY = -1;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (data[(y * width + x) * 4 + 3] > ALPHA_THRESHOLD) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }

  if (maxX < 0) return null;
  minX = Math.max(minX - CROP_PADDING, 0);
  minY = Math.max(minY - CROP_PADDING, 0);
  maxX = Math.min(maxX + CROP_PADDING, width - 1);
  maxY = Math.min(maxY + CROP_PADDING, height - 1);

  const w = maxX - minX + 1;
  const h = maxY - minY + 1;
  if (w < MIN_SIGNATURE_W || h < MIN_SIGNATURE_H) return null;

  const cropped = document.createElement('canvas');
  cropped.width = w;
  cropped.height = h;
  const croppedCtx = cropped.getContext('2d');
  if (!croppedCtx) return null;
  croppedCtx.drawImage(source, minX, minY, w, h, 0, 0, w, h);
  return cropped.toDataURL('image/png');
}

/** Lee un color de un token CSS (el canvas necesita un valor concreto). */
function readToken(name: string, fallback: string): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

export interface SignatureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (signaturePngDataUrl: string) => void;
  title?: string;
  /** Firma previa (data URL) para mostrar y permitir reemplazar. */
  initialSignature?: string | null;
}

export const SignatureModal: React.FC<SignatureModalProps> = ({
  isOpen,
  onClose,
  onSave,
  title = 'Registrar firma',
  initialSignature,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isDrawingRef = useRef(false);
  const returnFocusRef = useRef<HTMLElement | null>(null);
  const onCloseRef = useRef(onClose); // evita reiniciar el lienzo si el padre pasa una función nueva
  const titleId = useId();
  const [hasStroke, setHasStroke] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(rect.width * dpr); // reasignar el tamaño reinicia la transformación
    canvas.height = Math.round(rect.height * dpr);
    ctx.scale(dpr, dpr);
    ctx.strokeStyle = readToken('--ink-signature', '#0f172a');
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    if (initialSignature) {
      const img = new Image();
      img.onload = () => {
        // Dibuja la firma previa centrada y sin deformar.
        const ratio = Math.min(rect.width / img.width, rect.height / img.height, 1);
        const w = img.width * ratio;
        const h = img.height * ratio;
        ctx.drawImage(img, (rect.width - w) / 2, (rect.height - h) / 2, w, h);
        setHasStroke(true);
      };
      img.src = initialSignature;
    }
  }, [initialSignature]);

  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  useEffect(() => {
    if (!isOpen) return;
    returnFocusRef.current = document.activeElement as HTMLElement | null;
    setHasStroke(false);
    setError(null);
    const frame = requestAnimationFrame(() => {
      initCanvas();
      canvasRef.current?.focus();
    });
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCloseRef.current();
    };
    document.addEventListener('keydown', onKey);
    return () => {
      cancelAnimationFrame(frame);
      document.removeEventListener('keydown', onKey);
      returnFocusRef.current?.focus();
    };
  }, [isOpen, initCanvas]);

  const getPos = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    const { x, y } = getPos(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
    isDrawingRef.current = true;
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawingRef.current) return;
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    const { x, y } = getPos(e);
    ctx.lineTo(x, y);
    ctx.stroke();
    if (!hasStroke) setHasStroke(true);
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawingRef.current) return;
    isDrawingRef.current = false;
    if (e.currentTarget.hasPointerCapture(e.pointerId)) e.currentTarget.releasePointerCapture(e.pointerId);
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();
    setHasStroke(false);
    setError(null);
  };

  const handleSave = () => {
    if (!canvasRef.current) return;
    const cropped = cropToSignature(canvasRef.current);
    if (!cropped) {
      setError('La firma es demasiado pequeña o está vacía. Firma de nuevo.');
      return;
    }
    onSave(cropped);
    onClose();
  };

  if (!isOpen) return null;

  return createPortal(
    <div className="sig-modal-backdrop">
      <div className="sig-modal-content" role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <div className="sig-modal-header">
          <h3 id={titleId} className="sig-modal-title">{title}</h3>
          <button type="button" className="sig-modal-close" onClick={onClose} aria-label="Cerrar" title="Cerrar">
            <X size={20} aria-hidden="true" />
          </button>
        </div>

        <div className="sig-canvas-wrapper">
          <canvas
            ref={canvasRef}
            className="sig-canvas"
            tabIndex={0}
            role="img"
            aria-label="Área de firma. Firme con el dedo, lápiz o mouse."
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
          />
          <div className="sig-baseline-guide" aria-hidden="true" />
          <p className="sig-instruction">Firme sobre la línea con el dedo, lápiz o mouse</p>
          {error && <p className="sig-error" role="alert">{error}</p>}
        </div>

        <div className="sig-modal-footer">
          <button type="button" className="sig-btn sig-btn-clear" onClick={handleClear} disabled={!hasStroke}>
            <Eraser size={16} aria-hidden="true" />
            <span>Limpiar</span>
          </button>

          <div className="sig-modal-actions">
            <button type="button" className="sig-btn sig-btn-cancel" onClick={onClose}>
              Cancelar
            </button>
            <button type="button" className="sig-btn sig-btn-confirm" onClick={handleSave} disabled={!hasStroke}>
              <Check size={16} aria-hidden="true" />
              <span>Guardar firma</span>
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
  background-color: var(--overlay-scrim);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.sig-modal-content {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-width: 540px;
  overflow: hidden;
  animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.95) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
  .sig-modal-content { animation: none; }
}

.sig-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
}

.sig-modal-title {
  font-size: 1.05rem;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.sig-modal-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
}

.sig-modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sig-canvas-wrapper {
  position: relative;
  padding: 1.5rem;
  background: var(--bg-elevated);
}

.sig-canvas {
  display: block;
  width: 100%;
  height: 220px;
  background: var(--surface-paper);
  border: 1.5px dashed var(--border-strong);
  border-radius: var(--radius-md);
  touch-action: none;
  cursor: crosshair;
}

.sig-canvas:focus-visible,
.sig-btn:focus-visible,
.sig-modal-close:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.sig-baseline-guide {
  position: absolute;
  bottom: 4.25rem;
  left: 3rem;
  right: 3rem;
  height: 1px;
  background: var(--border-strong);
  pointer-events: none;
}

.sig-instruction {
  margin: 0.5rem 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  text-align: center;
}

.sig-error {
  margin: 0.5rem 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--status-error);
  text-align: center;
}

.sig-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-card);
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
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.sig-btn-clear,
.sig-btn-cancel {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.sig-btn-clear:hover:not(:disabled),
.sig-btn-cancel:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sig-btn-confirm {
  background: var(--brand-primary);
  color: var(--text-on-brand);
  border: none;
}

.sig-btn-confirm:hover:not(:disabled) {
  background: var(--brand-primary-hover);
}

.sig-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
```
