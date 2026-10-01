# Especificación de Componente: Banner de Instalación PWA (`PWAInstallBanner`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

El componente `PWAInstallBanner` detecta la compatibilidad del navegador con Progressive Web Apps (`beforeinstallprompt`) y presenta un banner inferior no intrusivo invitando a los operarios o guardas de portería a instalar la aplicación en su pantalla de inicio para acceso offline y pantalla completa.

> **Origen y validación en producción**: Extraído directamente de la aplicación de control de accesos vehiculares y peatonales en `porterias`.

---

### 1. Requisitos Técnicos y de Negocio

1. **Detección de Modo Standalone**: Si la aplicación ya se ejecuta instalada (modo PWA standalone), el banner se oculta automáticamente.
2. **Persistencia de Descarte**: Si el usuario presiona "✕" (cerrar), la decisión se guarda en `sessionStorage` para no molestarlo durante la misma sesión de trabajo.
3. **Disparador Nativo**: Al hacer clic en "Instalar", invoca `prompt()` nativo del navegador y captura el resultado (`accepted` o `dismissed`).

---

### 2. Implementación TypeScript / React

```tsx
// src/components/ui/PWAInstallBanner.tsx
import React, { useEffect, useState } from 'react';
import { Download, X } from 'lucide-react';
import './PWAInstallBanner.css';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
  prompt(): Promise<void>;
}

export interface PWAInstallBannerProps {
  appName?: string;
  subtitle?: string;
}

export const PWAInstallBanner: React.FC<PWAInstallBannerProps> = ({
  appName = 'Aplicación Corporativa Jolifoods',
  subtitle = 'Acceso rápido y sin conexión desde tu pantalla de inicio',
}) => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Si ya está en modo standalone, no mostrar
    const isStandalone =
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone === true;

    if (isStandalone) return;

    // Si ya fue descartado en esta sesión
    if (sessionStorage.getItem('joli-pwa-dismissed')) return;

    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShowBanner(true);
    };

    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      console.log('[PWA] Aplicación instalada exitosamente por el usuario.');
    }
    setDeferredPrompt(null);
    setShowBanner(false);
  };

  const handleDismiss = () => {
    sessionStorage.setItem('joli-pwa-dismissed', '1');
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <aside className="pwa-install-banner" role="banner" aria-label="Instalación de la aplicación">
      <div className="pwa-banner-icon-box" aria-hidden="true">
        <Download size={20} className="text-emerald-500" />
      </div>

      <div className="pwa-banner-text">
        <strong className="pwa-banner-title">{appName}</strong>
        <p className="pwa-banner-subtitle">{subtitle}</p>
      </div>

      <div className="pwa-banner-actions">
        <button
          type="button"
          className="pwa-btn-install"
          onClick={handleInstall}
          aria-label="Instalar aplicación"
        >
          Instalar
        </button>
        <button
          type="button"
          className="pwa-btn-close"
          onClick={handleDismiss}
          aria-label="Cerrar notificación"
        >
          <X size={16} />
        </button>
      </div>
    </aside>
  );
};
```

---

### 3. Estilos CSS (`PWAInstallBanner.css`)

```css
.pwa-install-banner {
  position: fixed;
  bottom: 1.25rem;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 2.5rem);
  max-width: 520px;
  background: rgba(15, 23, 42, 0.94);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-xl, 14px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
  padding: 0.875rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
  z-index: 1000;
  animation: bannerSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes bannerSlideUp {
  from { opacity: 0; transform: translate(-50%, 20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

.pwa-banner-icon-box {
  width: 38px;
  height: 38px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pwa-banner-text {
  flex: 1;
  min-width: 0;
}

.pwa-banner-title {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #F8FAFC;
  line-height: 1.2;
}

.pwa-banner-subtitle {
  margin: 2px 0 0 0;
  font-size: 0.75rem;
  color: #94A3B8;
  line-height: 1.3;
}

.pwa-banner-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.pwa-btn-install {
  background: var(--color-primary, #10B981);
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.pwa-btn-install:hover {
  background: #059669;
}

.pwa-btn-close {
  background: transparent;
  border: none;
  color: #64748B;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pwa-btn-close:hover {
  color: #F8FAFC;
}
```
