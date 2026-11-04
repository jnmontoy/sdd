# Especificación de Componente: Banner de Instalación PWA (`PWAInstallBanner`)
## SDD Joli Foods — Spec-Driven Development

> **Origen:** patrón tomado de porterias (control de accesos vehiculares y peatonales). Aquí se describe de forma genérica.

El componente `PWAInstallBanner` detecta si el navegador ofrece instalar la aplicación como PWA (*Progressive Web App*: app web instalable en la pantalla de inicio) mediante el evento `beforeinstallprompt`, y muestra un banner inferior no intrusivo para que operarios o personal de kiosco la instalen y la abran a pantalla completa.

---

### 1. Requisitos técnicos y de negocio

1. **Modo standalone**: si la app ya corre instalada (`display-mode: standalone`), el banner NO DEBE mostrarse.
2. **Descarte por sesión**: al cerrar con "✕", la decisión se guarda en `sessionStorage` con la clave `STORAGE_KEYS.pwaDismissed` (`<slug-app>:pwa_dismissed`). La clave DEBE llevar el identificador de la app porque varias apps pueden compartir dominio; el acceso a storage DEBE ir en `try/catch` (modo privado o storage bloqueado).
3. **Disparador nativo**: "Instalar" invoca `prompt()` del navegador y lee el resultado (`accepted` / `dismissed`). El evento solo se puede usar una vez.
4. **Instalación desde otro lugar**: si el usuario instala desde el menú del navegador, el evento `appinstalled` oculta el banner.
5. **Compatibilidad**: `beforeinstallprompt` existe en navegadores basados en Chromium. Safari (iOS/macOS) no lo emite; allí la instalación es manual ("Compartir → Agregar a inicio") y el banner simplemente no aparece.

---

### 2. Implementación React + TypeScript

```typescript
// src/config/storageKeys.ts (fragmento; ver la decisión canónica de claves de almacenamiento)
const APP = import.meta.env.VITE_APP_SLUG ?? 'app';
export const STORAGE_KEYS = {
  pwaDismissed: `${APP}:pwa_dismissed`,
  // ...resto de claves
} as const;
```

```tsx
// src/components/ui/PWAInstallBanner.tsx
import React, { useEffect, useState } from 'react';
import { Download, X } from 'lucide-react';
import { STORAGE_KEYS } from '@/config/storageKeys';
import './PWAInstallBanner.css';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
  prompt(): Promise<void>;
}

// Safari expone `navigator.standalone`; no está en los tipos estándar del DOM.
interface NavigatorStandalone extends Navigator {
  standalone?: boolean;
}

export interface PWAInstallBannerProps {
  appName?: string;
  subtitle?: string;
}

function readDismissed(): boolean {
  try {
    return sessionStorage.getItem(STORAGE_KEYS.pwaDismissed) === '1';
  } catch {
    return false;
  }
}

function saveDismissed(): void {
  try {
    sessionStorage.setItem(STORAGE_KEYS.pwaDismissed, '1');
  } catch {
    // Storage no disponible: el banner se ocultará solo hasta recargar.
  }
}

export const PWAInstallBanner: React.FC<PWAInstallBannerProps> = ({
  appName = 'Instala la aplicación',
  subtitle = 'Acceso rápido a pantalla completa desde tu pantalla de inicio',
}) => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);

  useEffect(() => {
    const isStandalone =
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as NavigatorStandalone).standalone === true;

    if (isStandalone || readDismissed()) return;

    const handleBeforeInstall = (e: Event) => {
      e.preventDefault(); // evita el mini-aviso nativo; mostramos el nuestro
      setDeferredPrompt(e as BeforeInstallPromptEvent);
    };
    const handleInstalled = () => setDeferredPrompt(null);

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    window.addEventListener('appinstalled', handleInstalled);
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
      window.removeEventListener('appinstalled', handleInstalled);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    const promptEvent = deferredPrompt;
    setDeferredPrompt(null); // el evento solo se puede usar una vez
    await promptEvent.prompt();
    await promptEvent.userChoice; // 'accepted' | 'dismissed' (se puede enviar a telemetría)
  };

  const handleDismiss = () => {
    saveDismissed();
    setDeferredPrompt(null);
  };

  if (!deferredPrompt) return null;

  return (
    <aside className="pwa-install-banner" role="region" aria-label="Instalación de la aplicación">
      <div className="pwa-banner-icon-box" aria-hidden="true">
        <Download size={20} />
      </div>

      <div className="pwa-banner-text">
        <strong className="pwa-banner-title">{appName}</strong>
        <p className="pwa-banner-subtitle">{subtitle}</p>
      </div>

      <div className="pwa-banner-actions">
        <button type="button" className="pwa-btn-install" onClick={handleInstall}>
          Instalar
        </button>
        <button type="button" className="pwa-btn-close" onClick={handleDismiss} aria-label="Cerrar aviso de instalación" title="Cerrar">
          <X size={16} aria-hidden="true" />
        </button>
      </div>
    </aside>
  );
};
```

---

### 3. Estilos CSS (`PWAInstallBanner.css`)

El banner es un aviso flotante (no una vista), por eso puede ir centrado en la parte inferior.

```css
.pwa-install-banner {
  position: fixed;
  bottom: 1.25rem;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 2.5rem);
  max-width: 520px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-popover);
  padding: 0.875rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
  z-index: var(--z-drawer);
  animation: bannerSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes bannerSlideUp {
  from { opacity: 0; transform: translate(-50%, 20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

@media (prefers-reduced-motion: reduce) {
  .pwa-install-banner { animation: none; }
}

.pwa-banner-icon-box {
  width: 38px;
  height: 38px;
  color: var(--brand-primary);
  background: var(--status-success-bg);
  border: 1px solid var(--border-card-accent);
  border-radius: var(--radius-lg);
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
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  line-height: var(--line-height-tight);
}

.pwa-banner-subtitle {
  margin: 2px 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  line-height: 1.3;
}

.pwa-banner-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.pwa-btn-install {
  background: var(--brand-primary);
  color: var(--text-on-brand);
  border: none;
  border-radius: var(--radius-sm);
  padding: 0.4rem 0.85rem;
  font-size: 0.8rem;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.pwa-btn-install:hover {
  background: var(--brand-primary-hover);
}

.pwa-btn-install:focus-visible,
.pwa-btn-close:focus-visible {
  outline: none;
  box-shadow: var(--shadow-input-focus);
}

.pwa-btn-close {
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pwa-btn-close:hover {
  color: var(--text-primary);
}
```
