# Especificación de Componente: Modal de Escáner Barcode / QR (`ScannerModal`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

El componente `ScannerModal` integra la cámara web o del dispositivo móvil para decodificar en tiempo real códigos de barras (Code 128, EAN-13, ITF) y códigos QR. Proporciona una interfaz asistida con marco de enfoque, estado de encendido de cámara y retroalimentación sonora/háptica opcional al detectar una lectura válida.

> **Origen y validación en producción**: Extraído de las implementaciones operativas de `tiendita` (despacho de EPP por código de barras) y `contenedores` (lectura de sellos y QR de contenedores).

---

### 1. Requisitos Técnicos y Dependencias

- **Librería del núcleo**: `html5-qrcode` (`npm install html5-qrcode`).
- **Permisos de Cámara**: Manejo automático de solicitud de permisos y selección de cámara trasera (`environment`) en dispositivos móviles.
- **Auto-cierre**: Cierre inmediato y detención del stream de video tras una lectura exitosa para liberar recursos de la GPU/cámara.
- **Tolerancia a fallos**: Supresión de logs rutinarios de escaneo vacío para mantener la consola limpia.

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/ScannerModal.tsx
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, ScanLine, Loader2, Camera } from 'lucide-react';
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
  title = 'Escanear Código de Barras o QR',
}) => {
  const [isStarting, setIsStarting] = useState(true);
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);

  useEffect(() => {
    if (isOpen) {
      setIsStarting(true);
      const timer = setTimeout(() => {
        try {
          scannerRef.current = new Html5QrcodeScanner(
            'joli-reader-container',
            {
              fps: 12,
              qrbox: { width: 260, height: 200 },
              supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
              rememberLastUsedCamera: true,
            },
            false
          );

          scannerRef.current.render(
            (decodedText) => {
              if (scannerRef.current) {
                scannerRef.current.clear().catch(console.error);
              }
              onScan(decodedText);
              onClose();
            },
            () => {
              // Silenciar errores rutinarios de frames sin código
            }
          );
          setIsStarting(false);
        } catch (err) {
          console.error('[ScannerModal] Error al inicializar cámara:', err);
          setIsStarting(false);
        }
      }, 250);

      return () => {
        clearTimeout(timer);
        if (scannerRef.current) {
          scannerRef.current.clear().catch(console.error);
        }
      };
    }
  }, [isOpen, onScan, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div className="scanner-modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div className="scanner-modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="scanner-modal-header">
          <div className="scanner-modal-title-group">
            <ScanLine className="scanner-header-icon" size={20} />
            <h3 className="scanner-modal-title">{title}</h3>
          </div>
          <button type="button" className="scanner-modal-close" onClick={onClose} aria-label="Cerrar">
            <X size={20} />
          </button>
        </div>

        <div className="scanner-modal-body">
          {isStarting && (
            <div className="scanner-loading-overlay">
              <Loader2 className="scanner-spinner animate-spin" size={32} />
              <p>Iniciando sensor de cámara...</p>
            </div>
          )}
          <div id="joli-reader-container" className="scanner-viewport-box" />
          <p className="scanner-guide-text">
            Apunta la cámara al código de barras o QR para escanear automáticamente
          </p>
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
  background-color: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: var(--z-modal, 1050);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.scanner-modal-box {
  background: var(--bg-card, #FFFFFF);
  border: 1px solid var(--border-subtle, #E2E8F0);
  border-radius: var(--radius-xl, 14px);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
  width: 100%;
  max-width: 480px;
  overflow: hidden;
  animation: scannerPop 0.25s ease-out;
}

@keyframes scannerPop {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.scanner-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-subtle, #E2E8F0);
}

.scanner-modal-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scanner-header-icon {
  color: var(--color-primary, #10B981);
}

.scanner-modal-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  margin: 0;
}

.scanner-modal-close {
  background: transparent;
  border: none;
  color: var(--text-muted, #94A3B8);
  cursor: pointer;
  padding: 4px;
}

.scanner-modal-body {
  position: relative;
  padding: 1.25rem;
  background: #F8FAFC;
}

.scanner-loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  z-index: 10;
  color: #475569;
  font-size: 0.85rem;
}

.scanner-viewport-box {
  width: 100%;
  min-height: 280px;
  border-radius: 8px;
  overflow: hidden;
  background: #000000;
}

.scanner-guide-text {
  margin: 0.75rem 0 0 0;
  font-size: 0.75rem;
  color: var(--text-muted, #64748B);
  text-align: center;
}
```
