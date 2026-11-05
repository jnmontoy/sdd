# Especificación de Componente: Modal de Escáner de Códigos de Barras / QR (`ScannerModal`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de tiendita (despacho de EPP por código de barras) y contenedores (lectura de sellos y QR). Aquí se describe de forma genérica.

`ScannerModal` usa la cámara del equipo o del celular para leer en tiempo real códigos de barras (Code 128, EAN-13, ITF) y códigos QR. Muestra un marco de enfoque y se cierra solo al leer un código válido. Es una de las excepciones permitidas de modal centrado (escáneres).

---

### 1. Requisitos técnicos y dependencias

- **Librería**: `html5-qrcode` (`npm install html5-qrcode`).
- **Cámara**: la librería pide el permiso y permite elegir la cámara (trasera por defecto en celulares). Solo funciona en HTTPS o `localhost`.
- **Una sola lectura (DEBE)**: tras la primera lectura válida se ignoran las siguientes (la librería puede reportar el mismo código varias veces seguidas) y se detiene la cámara.
- **Callbacks estables**: `onScan` y `onClose` se guardan en `ref`; si el padre pasa funciones nuevas en cada render, la cámara NO se reinicia.
- **Liberación de la cámara (DEBE)**: al cerrar o desmontar se llama `clear()` una sola vez.
- **Id único**: el contenedor del lector usa `useId`, para que no choque con otro escáner en la página.
- **Accesibilidad**: `role="dialog"`, `aria-modal`, `aria-labelledby`, cierre con `Escape` y foco inicial en "Cerrar". El clic en el fondo NO cierra el modal (evita cierres accidentales mientras se apunta la cámara).
- **Alternativa manual**: el contenedor DEBERÍA ofrecer un campo para digitar el código si la cámara no está disponible.

---

### 2. Implementación React + TypeScript

```tsx
// src/components/ui/ScannerModal.tsx
import React, { useEffect, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, ScanLine, Loader2 } from 'lucide-react';
import { Html5QrcodeScanner, Html5QrcodeScanType } from 'html5-qrcode';
import './ScannerModal.css';

export interface ScannerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onScan: (decodedText: string) => void;
  title?: string;
}

export const ScannerModal: React.FC<ScannerModalProps> = ({
  isOpen,
  onClose,
  onScan,
  title = 'Escanear código de barras o QR',
}) => {
  const [isStarting, setIsStarting] = useState(true);
  const [startError, setStartError] = useState<string | null>(null);
  const readerId = `reader-${useId().replace(/:/g, '')}`;
  const titleId = useId();
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const onScanRef = useRef(onScan);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    onScanRef.current = onScan;
    onCloseRef.current = onClose;
  }, [onScan, onClose]);

  useEffect(() => {
    if (!isOpen) return;

    let scanner: Html5QrcodeScanner | null = null;
    let cleared = false;
    let handled = false;

    const clearScanner = () => {
      if (cleared || !scanner) return;
      cleared = true;
      scanner.clear().catch(() => {
        /* la cámara ya estaba detenida */
      });
    };

    setIsStarting(true);
    setStartError(null);
    closeBtnRef.current?.focus();

    // Se espera un frame para que el contenedor exista en el DOM (portal recién montado).
    const frame = requestAnimationFrame(() => {
      try {
        scanner = new Html5QrcodeScanner(
          readerId,
          {
            fps: 12,
            qrbox: { width: 260, height: 200 },
            supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
            rememberLastUsedCamera: true,
          },
          false
        );
        scanner.render(
          (decodedText) => {
            if (handled) return; // ignora lecturas repetidas del mismo código
            handled = true;
            clearScanner();
            onScanRef.current(decodedText);
            onCloseRef.current();
          },
          () => {
            /* frames sin código: es normal, no se registra */
          }
        );
      } catch {
        setStartError('No fue posible iniciar la cámara.');
      } finally {
        setIsStarting(false);
      }
    });

    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCloseRef.current();
    };
    document.addEventListener('keydown', onKey);

    return () => {
      cancelAnimationFrame(frame);
      document.removeEventListener('keydown', onKey);
      clearScanner();
    };
  }, [isOpen, readerId]);

  if (!isOpen) return null;

  return createPortal(
    <div className="scanner-modal-backdrop">
      <div className="scanner-modal-box" role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <div className="scanner-modal-header">
          <div className="scanner-modal-title-group">
            <ScanLine className="scanner-header-icon" size={20} aria-hidden="true" />
            <h3 id={titleId} className="scanner-modal-title">{title}</h3>
          </div>
          <button ref={closeBtnRef} type="button" className="scanner-modal-close" onClick={onClose} aria-label="Cerrar escáner" title="Cerrar">
            <X size={20} aria-hidden="true" />
          </button>
        </div>

        <div className="scanner-modal-body">
          {isStarting && (
            <div className="scanner-loading-overlay" role="status">
              <Loader2 className="scanner-spinner" size={32} aria-hidden="true" />
              <p>Iniciando cámara…</p>
            </div>
          )}
          {startError && <p className="scanner-error" role="alert">{startError}</p>}
          <div id={readerId} className="scanner-viewport-box" />
          <p className="scanner-guide-text">Apunta la cámara al código; la lectura es automática.</p>
        </div>
      </div>
    </div>,
    document.body
  );
};
```

---

### 3. Estilos CSS (`ScannerModal.css`)

```css
.scanner-modal-backdrop {
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

.scanner-modal-box {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-width: 480px;
  overflow: hidden;
  animation: scannerPop 0.25s ease-out;
}

@keyframes scannerPop {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

@media (prefers-reduced-motion: reduce) {
  .scanner-modal-box { animation: none; }
}

.scanner-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle);
}

.scanner-modal-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scanner-header-icon {
  color: var(--brand-primary);
}

.scanner-modal-title {
  font-size: 0.95rem;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.scanner-modal-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
}

.scanner-modal-close:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.scanner-modal-close:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.scanner-modal-body {
  position: relative;
  padding: 1.25rem;
  background: var(--bg-elevated);
}

.scanner-loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: var(--glass-bg);
  z-index: var(--z-card);
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.scanner-spinner {
  color: var(--brand-primary);
  animation: joliSpin 1s linear infinite;
}

@keyframes joliSpin {
  to { transform: rotate(360deg); }
}

.scanner-error {
  color: var(--status-error);
  font-size: var(--font-size-sm);
  margin: 0 0 0.75rem;
}

.scanner-viewport-box {
  width: 100%;
  min-height: 280px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--overlay-surface);
}

.scanner-guide-text {
  margin: 0.75rem 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  text-align: center;
}
```
