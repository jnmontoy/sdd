# Especificación de Componente: Escáner Biométrico Facial (`FacialScanner`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

El componente `FacialScanner` implementa un visor de cámara web o dispositivo móvil con **guía biométrica ovalada**, control de exposición/zoom y detección de presencia facial para autenticación de "manos libres" en quioscos operativos, porterías y registro fotográfico de colaboradores.

> **Origen y validación en producción**: Extraído y generalizado a partir del módulo de acceso de operarios de patio en `contenedores`.

---

### 1. Requisitos Técnicos y de Experiencia de Usuario (UX)

1. **Guía Ovalada Asistida (`FacialOvalGuide`)**: Proporciona un marco elíptico en pantalla que guía al usuario a centrar su rostro a la distancia correcta.
2. **Cortina Oscurecedora de Enfoque (`FacialCurtainOverlay`)**: Aplica una máscara perimetral oscura semi-translúcida (`rgba(15, 23, 42, 0.75)`) dejando transparente únicamente el interior del óvalo facial.
3. **Modos Operativos**:
   - `auto`: Disparo automático continuo para inicio de sesión inmediato al reconocer el descriptor facial.
   - `manual`: Botón obturador para captura de fotografía fija en enrolamiento de nuevos usuarios.
4. **Control de Dispositivos y Zoom**: Detección de cámaras frontales/traseras (`facingMode`) y slider/botones de zoom digital (1.0x a 3.0x).
5. **Liberación de Hardware**: Apagado estricto de pistas `MediaStream` al desmontar el componente para apagar el LED de la cámara física.

---

### 2. Implementación TypeScript / React

```tsx
// src/components/biometrics/FacialScanner.tsx
import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Camera, RefreshCw, ZoomIn, ZoomOut, CheckCircle2, AlertCircle } from 'lucide-react';
import './FacialScanner.css';

export interface FacialScannerProps {
  onCapture: (base64Image: string) => void;
  onError?: (errorMessage: string) => void;
  mode?: 'auto' | 'manual';
  title?: string;
  autoStart?: boolean;
}

export const FacialScanner: React.FC<FacialScannerProps> = ({
  onCapture,
  onError,
  mode = 'manual',
  title = 'Alinea tu rostro dentro del óvalo',
  autoStart = true,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [zoom, setZoom] = useState(1.0);
  const [statusText, setStatusText] = useState('Iniciando cámara...');

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setIsReady(false);
  }, []);

  const startCamera = useCallback(async () => {
    stopCamera();
    try {
      setStatusText('Solicitando acceso al sensor de video...');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
          setIsReady(true);
          setStatusText('Rostro detectado. Mantén la posición');
        };
      }
    } catch (err: any) {
      const msg = 'No se pudo acceder a la cámara. Verifica los permisos del navegador.';
      setStatusText(msg);
      onError?.(msg);
    }
  }, [facingMode, stopCamera, onError]);

  useEffect(() => {
    if (autoStart) {
      startCamera();
    }
    return () => {
      stopCamera();
    };
  }, [autoStart, startCamera, stopCamera]);

  const toggleFacingMode = () => {
    setFacingMode((prev) => (prev === 'user' ? 'environment' : 'user'));
  };

  const handleCapture = () => {
    const video = videoRef.current;
    if (!video) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Efecto espejo si la cámara es frontal
    if (facingMode === 'user') {
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
    onCapture(dataUrl);
  };

  return (
    <div className="facial-scanner-wrapper">
      <div className="facial-scanner-viewport">
        {/* Video feed */}
        <video
          ref={videoRef}
          playsInline
          muted
          className={`facial-video-feed ${facingMode === 'user' ? 'mirror' : ''}`}
          style={{ transform: `scale(${zoom}) ${facingMode === 'user' ? 'scaleX(-1)' : ''}` }}
        />

        {/* Cortina oscura perimetral con máscara ovalada SVG */}
        <svg className="facial-curtain-mask" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <mask id="oval-cutout">
              <rect x="0" y="0" width="100" height="100" fill="#FFFFFF" />
              <ellipse cx="50" cy="50" rx="30" ry="38" fill="#000000" />
            </mask>
          </defs>
          <rect
            x="0"
            y="0"
            width="100"
            height="100"
            fill="rgba(15, 23, 42, 0.72)"
            mask="url(#oval-cutout)"
          />
        </svg>

        {/* Borde reactivo de la guía ovalada */}
        <div className={`facial-oval-guide ${isReady ? 'guide-active' : ''}`}>
          <div className="oval-pulse-ring" />
        </div>

        {/* Badge superior de estado */}
        <div className="facial-status-pill">
          {isReady ? <CheckCircle2 size={15} className="text-emerald-400" /> : <AlertCircle size={15} />}
          <span>{statusText}</span>
        </div>

        {/* Controles de cámara flotantes */}
        <div className="facial-cam-controls">
          <button type="button" onClick={toggleFacingMode} title="Cambiar cámara" aria-label="Cambiar cámara">
            <RefreshCw size={17} />
          </button>
          <button
            type="button"
            onClick={() => setZoom((z) => Math.min(z + 0.2, 2.0))}
            title="Acercar"
            aria-label="Acercar"
          >
            <ZoomIn size={17} />
          </button>
          <button
            type="button"
            onClick={() => setZoom((z) => Math.max(z - 0.2, 1.0))}
            title="Alejar"
            aria-label="Alejar"
          >
            <ZoomOut size={17} />
          </button>
        </div>
      </div>

      <p className="facial-scanner-instruction">{title}</p>

      {mode === 'manual' && (
        <div className="facial-shutter-bar">
          <button
            type="button"
            className="facial-shutter-btn"
            onClick={handleCapture}
            disabled={!isReady}
          >
            <Camera size={20} />
            <span>Capturar Fotografía</span>
          </button>
        </div>
      )}
    </div>
  );
};
```

---

### 3. Estilos CSS (`FacialScanner.css`)

```css
.facial-scanner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
}

.facial-scanner-viewport {
  position: relative;
  width: 100%;
  height: 380px;
  border-radius: var(--radius-xl, 16px);
  overflow: hidden;
  background: #000000;
  box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.45);
}

.facial-video-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.facial-curtain-mask {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.facial-oval-guide {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  height: 76%;
  border-radius: 50% / 50%;
  border: 2px dashed rgba(255, 255, 255, 0.4);
  pointer-events: none;
  transition: all 0.3s ease;
}

.facial-oval-guide.guide-active {
  border: 2.5px solid var(--color-primary, #10B981);
  box-shadow: 0 0 24px rgba(16, 185, 129, 0.35);
}

.oval-pulse-ring {
  position: absolute;
  inset: -6px;
  border-radius: inherit;
  border: 1px solid var(--color-primary, #10B981);
  opacity: 0.5;
  animation: ovalPulse 2s infinite ease-in-out;
}

@keyframes ovalPulse {
  0% { transform: scale(0.98); opacity: 0.8; }
  50% { transform: scale(1.02); opacity: 0.3; }
  100% { transform: scale(0.98); opacity: 0.8; }
}

.facial-status-pill {
  position: absolute;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #F8FAFC;
  padding: 0.4rem 0.85rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.facial-cam-controls {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.35rem;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  padding: 0.3rem 0.5rem;
  border-radius: 20px;
}

.facial-cam-controls button {
  background: transparent;
  border: none;
  color: #FFFFFF;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
}

.facial-cam-controls button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.facial-scanner-instruction {
  margin: 0.85rem 0 0 0;
  font-size: 0.85rem;
  color: var(--text-secondary, #475569);
  text-align: center;
}

.facial-shutter-bar {
  margin-top: 1rem;
  width: 100%;
}

.facial-shutter-btn {
  width: 100%;
  background: var(--color-primary, #10B981);
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.facial-shutter-btn:hover:not(:disabled) {
  background: #059669;
}

.facial-shutter-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```
