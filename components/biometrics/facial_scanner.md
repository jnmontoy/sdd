# Especificación de Componente: Escáner Facial (`FacialScanner`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de contenedores (acceso de operarios de patio). Aquí se describe de forma genérica.

`FacialScanner` es un visor de cámara (web o móvil) con **guía ovalada**, cambio de cámara y zoom digital, para capturar la fotografía del rostro en quioscos, puntos de acceso o registro fotográfico de colaboradores.

> **Alcance:** este componente **captura** la imagen. No detecta rostros ni verifica identidad: esa comparación (si existe) DEBE hacerse en el backend con un servicio biométrico. El texto de estado no debe afirmar "rostro detectado" si no hay detección real.

> **Datos sensibles (DEBE):** en Colombia los datos biométricos son datos sensibles (Ley 1581 de 2012). Antes de capturar se DEBE contar con autorización previa, expresa e informada del titular, indicando finalidad y tiempo de conservación. La imagen viaja solo por HTTPS al backend, no se guarda en `localStorage` y el acceso a ella queda restringido y auditado.

---

### 1. Requisitos técnicos y de experiencia de usuario

1. **Guía ovalada (`facial-oval-guide`)**: marco elíptico que ayuda a centrar el rostro.
2. **Cortina de enfoque**: máscara oscura semitransparente (`--overlay-scrim`) que deja transparente solo el óvalo. Usa un `id` único por instancia (`useId`) para que dos escáneres en la misma página no compartan la máscara.
3. **Captura manual**: botón obturador; la imagen capturada respeta el zoom visible y el efecto espejo de la cámara frontal.
4. **Cámaras y zoom**: alterna frontal/trasera (`facingMode`) y zoom digital de 1.0x a 2.0x.
5. **Liberación de la cámara (DEBE)**: se detienen todas las pistas de `MediaStream` al desmontar, al cambiar de cámara y si el componente se desmonta mientras el navegador aún está pidiendo permiso (evita que el LED de la cámara quede encendido).
6. **Errores claros**: distingue permiso denegado (`NotAllowedError`), cámara inexistente (`NotFoundError`) y contexto inseguro (la cámara solo funciona en HTTPS o `localhost`).

---

### 2. Implementación React + TypeScript

```tsx
// src/components/biometrics/FacialScanner.tsx
import React, { useCallback, useEffect, useId, useRef, useState } from 'react';
import { Camera, RefreshCw, ZoomIn, ZoomOut, CheckCircle2, AlertCircle } from 'lucide-react';
import './FacialScanner.css';

export interface FacialScannerProps {
  /** Recibe la imagen JPEG como data URL. El contenedor la envía al backend y no la persiste en el navegador. */
  onCapture: (jpegDataUrl: string) => void;
  onError?: (errorMessage: string) => void;
  title?: string;
  autoStart?: boolean;
}

const MIN_ZOOM = 1.0;
const MAX_ZOOM = 2.0;
const ZOOM_STEP = 0.2;

function cameraErrorMessage(err: unknown): string {
  if (!window.isSecureContext) return 'La cámara solo está disponible en conexiones seguras (HTTPS).';
  if (err instanceof DOMException) {
    if (err.name === 'NotAllowedError') return 'Permiso de cámara denegado. Habilítalo en la configuración del navegador.';
    if (err.name === 'NotFoundError') return 'No se encontró ninguna cámara en este dispositivo.';
    if (err.name === 'NotReadableError') return 'La cámara está siendo usada por otra aplicación.';
  }
  return 'No se pudo acceder a la cámara.';
}

export const FacialScanner: React.FC<FacialScannerProps> = ({
  onCapture,
  onError,
  title = 'Alinea tu rostro dentro del óvalo',
  autoStart = true,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const requestIdRef = useRef(0); // invalida solicitudes de cámara viejas
  const maskId = useId();
  const [isReady, setIsReady] = useState(false);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [zoom, setZoom] = useState(MIN_ZOOM);
  const [statusText, setStatusText] = useState('Iniciando cámara…');

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setIsReady(false);
  }, []);

  const startCamera = useCallback(async () => {
    stopCamera();
    const requestId = ++requestIdRef.current;
    try {
      setStatusText('Solicitando acceso a la cámara…');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });

      // Si el componente se desmontó o se pidió otra cámara mientras esperábamos, liberar y salir.
      if (requestId !== requestIdRef.current) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }

      streamRef.current = stream;
      const video = videoRef.current;
      if (!video) return;
      video.srcObject = stream;
      await video.play();
      setIsReady(true);
      setStatusText('Cámara lista. Mantén el rostro dentro del óvalo');
    } catch (err: unknown) {
      if (requestId !== requestIdRef.current) return;
      const msg = cameraErrorMessage(err);
      setStatusText(msg);
      onError?.(msg);
    }
  }, [facingMode, stopCamera, onError]);

  useEffect(() => {
    if (autoStart) void startCamera();
    return () => {
      requestIdRef.current++; // cancela cualquier getUserMedia pendiente
      stopCamera();
    };
  }, [autoStart, startCamera, stopCamera]);

  const handleCapture = () => {
    const video = videoRef.current;
    if (!video || !isReady) return;

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Recorte central equivalente al zoom que ve el usuario.
    const srcW = width / zoom;
    const srcH = height / zoom;
    const srcX = (width - srcW) / 2;
    const srcY = (height - srcH) / 2;

    if (facingMode === 'user') {
      // Igual a lo que el usuario ve (vista espejo).
      ctx.translate(width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(video, srcX, srcY, srcW, srcH, 0, 0, width, height);
    onCapture(canvas.toDataURL('image/jpeg', 0.9));
  };

  const videoTransform = `scale(${zoom})${facingMode === 'user' ? ' scaleX(-1)' : ''}`;

  return (
    <div className="facial-scanner-wrapper">
      <div className="facial-scanner-viewport">
        <video
          ref={videoRef}
          playsInline
          muted
          className="facial-video-feed"
          style={{ transform: videoTransform }}
          aria-label="Vista previa de la cámara"
        />

        {/* Cortina oscura con recorte ovalado */}
        <svg className="facial-curtain-mask" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <mask id={maskId}>
              <rect x="0" y="0" width="100" height="100" fill="white" />
              <ellipse cx="50" cy="50" rx="30" ry="38" fill="black" />
            </mask>
          </defs>
          <rect x="0" y="0" width="100" height="100" className="facial-curtain-fill" mask={`url(#${maskId})`} />
        </svg>

        <div className={`facial-oval-guide ${isReady ? 'guide-active' : ''}`} aria-hidden="true">
          <div className="oval-pulse-ring" />
        </div>

        <div className="facial-status-pill" role="status" aria-live="polite">
          {isReady ? <CheckCircle2 size={15} className="facial-status-ok" aria-hidden="true" /> : <AlertCircle size={15} aria-hidden="true" />}
          <span>{statusText}</span>
        </div>

        <div className="btn-group btn-group-sm facial-cam-controls" role="group" aria-label="Controles de cámara">
          <button type="button" onClick={() => setFacingMode((p) => (p === 'user' ? 'environment' : 'user'))} title="Cambiar cámara" aria-label="Cambiar cámara">
            <RefreshCw size={17} aria-hidden="true" />
          </button>
          <button type="button" onClick={() => setZoom((z) => Math.min(+(z + ZOOM_STEP).toFixed(1), MAX_ZOOM))} disabled={zoom >= MAX_ZOOM} title="Acercar" aria-label="Acercar">
            <ZoomIn size={17} aria-hidden="true" />
          </button>
          <button type="button" onClick={() => setZoom((z) => Math.max(+(z - ZOOM_STEP).toFixed(1), MIN_ZOOM))} disabled={zoom <= MIN_ZOOM} title="Alejar" aria-label="Alejar">
            <ZoomOut size={17} aria-hidden="true" />
          </button>
        </div>
      </div>

      <p className="facial-scanner-instruction">{title}</p>

      <div className="facial-shutter-bar">
        <button type="button" className="facial-shutter-btn" onClick={handleCapture} disabled={!isReady}>
          <Camera size={20} aria-hidden="true" />
          <span>Capturar fotografía</span>
        </button>
      </div>
    </div>
  );
};
```

---

### 3. Estilos CSS (`FacialScanner.css`)

El visor va sobre video, por eso usa los tokens fijos de capa (`--overlay-*`, `--text-on-overlay`), que no cambian con el tema. El escáner suele vivir dentro de un modal (`ScannerModal`/`FacialScanner` son excepciones permitidas de centrado).

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
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--overlay-surface);
  box-shadow: var(--shadow-modal);
}

.facial-video-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-base);
}

.facial-curtain-mask {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.facial-curtain-fill {
  fill: var(--overlay-scrim);
}

.facial-oval-guide {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  height: 76%;
  border-radius: 50%;
  border: 2px dashed var(--overlay-border);
  pointer-events: none;
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}

.facial-oval-guide.guide-active {
  border: 2.5px solid var(--brand-primary);
  box-shadow: 0 0 24px var(--brand-glow);
}

.oval-pulse-ring {
  position: absolute;
  inset: -6px;
  border-radius: inherit;
  border: 1px solid var(--brand-primary);
  opacity: 0.5;
  animation: ovalPulse 2s infinite ease-in-out;
}

@keyframes ovalPulse {
  0%, 100% { transform: scale(0.98); opacity: 0.8; }
  50% { transform: scale(1.02); opacity: 0.3; }
}

@media (prefers-reduced-motion: reduce) {
  .oval-pulse-ring { animation: none; }
}

.facial-status-pill {
  position: absolute;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--overlay-surface);
  backdrop-filter: blur(8px);
  border: 1px solid var(--overlay-border);
  color: var(--text-on-overlay);
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.facial-status-ok {
  color: var(--brand-primary-light);
}

.facial-cam-controls {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background: var(--overlay-surface);
  backdrop-filter: blur(8px);
  padding: 0.3rem;
  border-radius: var(--radius-full);
}

.facial-cam-controls button {
  background: transparent;
  border: none;
  color: var(--text-on-overlay);
  padding: 4px 8px;
  border-radius: var(--radius-full);
  cursor: pointer;
}

.facial-cam-controls button:hover:not(:disabled) {
  background: var(--overlay-control-hover);
}

.facial-cam-controls button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.facial-cam-controls button:focus-visible,
.facial-shutter-btn:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.facial-scanner-instruction {
  margin: 0.85rem 0 0 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-align: center;
}

.facial-shutter-bar {
  margin-top: 1rem;
  width: 100%;
}

.facial-shutter-btn {
  width: 100%;
  background: var(--brand-primary);
  color: var(--text-on-brand);
  border: none;
  border-radius: var(--radius-md);
  padding: 0.75rem;
  font-size: 0.9rem;
  font-weight: var(--font-weight-semibold);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.facial-shutter-btn:hover:not(:disabled) {
  background: var(--brand-primary-hover);
}

.facial-shutter-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```
