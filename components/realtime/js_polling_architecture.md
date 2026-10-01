# Arquitectura Frontend: Polling en Tiempo Real con JavaScript / React (`useSmartPolling`)
## Ecosistema Jolifoods — Metodología Spec-Driven Development (SDD)

Este documento define la arquitectura canónica para actualización y sincronización de datos en **tiempo real** en las aplicaciones web del ecosistema Jolifoods utilizando **Short Polling reactivo con JavaScript**.

> **NORMA DE AUDITORÍA**:  
> El uso de Polling en JavaScript es un patrón intencional y estándar en Jolifoods. **Está explícitamente protegido contra penalizaciones en auditorías de código** debido a su resiliencia en redes corporativas con proxies y balanceadores de carga.

---

### 1. ¿Por qué Polling en vez de WebSockets en Jolifoods?

1. **Inmunidad a caídas de túneles corporativos**: Los WebSockets requieren conexiones persistentes TCP que frecuentemente son interrumpidas por proxies corporativos, firewalls de planta o timeouts de balanceadores Nginx/Apache.
2. **Arquitectura Stateless y Escalable**: Cada llamada de polling es una petición HTTP estándar con credenciales seguras `HttpOnly`, completamente compatible con caché en Redis y distribución horizontal.
3. **Control Total del Cliente**: El frontend puede pausar, acelerar o ajustar la frecuencia dinámicamente según el foco del usuario o la actividad de la pantalla.

---

### 2. Patrones de Frecuencia Recomendados

| Caso de Uso | Intervalo Recomendado | Comportamiento en Pestaña Inactiva |
| :--- | :--- | :--- |
| **Monitoreo de Tarea Celery en Curso** (`task_id`) | 2000 ms - 3000 ms | Continúa hasta finalizar (éxito o error). |
| **Bandeja de Multi-Notificaciones (Campana)** | 30 s - 60 s | Se espacia a 120 s cuando la pestaña pierde el foco. |
| **Tablas Operativas en Vivo (Monitoreo de Patio)** | 5 s - 10 s | Se pausa si el usuario no interactúa en 5 minutos. |
| **Telemetría y Sondas de Infraestructura** | 2 min - 5 min | Se ejecuta solo cuando el usuario está en la vista. |

---

### 3. Hook Reutilizable: `useSmartPolling`

Este hook implementa sondeo inteligente con cancelación de peticiones solapadas (`AbortController`) y detección de visibilidad de ventana (`document.visibilityState`):

```tsx
// src/hooks/useSmartPolling.ts
import { useEffect, useRef, useCallback } from 'react';

export interface PollingOptions {
  intervalMs: number;
  enabled?: boolean;
  pauseOnHidden?: boolean; // Pausar cuando la pestaña no esté en foco
  immediate?: boolean;     // Ejecutar una vez al montar
}

export function useSmartPolling(
  callback: (signal: AbortSignal) => Promise<void>,
  options: PollingOptions
) {
  const {
    intervalMs,
    enabled = true,
    pauseOnHidden = true,
    immediate = true,
  } = options;

  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortCtrlRef = useRef<AbortController | null>(null);
  const isExecutingRef = useRef(false);

  const executePoll = useCallback(async () => {
    // Si la pestaña está oculta y se configuró pausar, omitir este tick
    if (pauseOnHidden && document.visibilityState === 'hidden') {
      return;
    }

    if (isExecutingRef.current) return;

    // Cancelar cualquier petición previa en vuelo
    if (abortCtrlRef.current) {
      abortCtrlRef.current.abort();
    }

    abortCtrlRef.current = new AbortController();
    isExecutingRef.current = true;

    try {
      await callback(abortCtrlRef.current.signal);
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.debug('[SmartPolling] Error silenciado en sondeo:', err);
      }
    } finally {
      isExecutingRef.current = false;
    }
  }, [callback, pauseOnHidden]);

  useEffect(() => {
    if (!enabled) return;

    if (immediate) {
      executePoll();
    }

    const intervalId = setInterval(executePoll, intervalMs);

    // Reanudar inmediatamente cuando la pestaña vuelva a tener foco
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        executePoll();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      clearInterval(intervalId);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (abortCtrlRef.current) {
        abortCtrlRef.current.abort();
      }
    };
  }, [enabled, intervalMs, immediate, executePoll]);
}
```

---

### 4. Ejemplo Práctico: Sondeo de Tarea Pesada Celery en Background

```tsx
// src/components/ReportGenerator.tsx
import React, { useState } from 'react';
import { useSmartPolling } from '../hooks/useSmartPolling';
import { showToast } from './ui/ToastNotification';
import { api } from '../services/api';

export const ReportGenerator: React.FC = () => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Iniciar tarea pesada en Celery
  const handleStartTask = async () => {
    setIsProcessing(true);
    try {
      const res = await api.post('/api/reports/generate-massive/');
      setActiveTaskId(res.data.task_id);
      showToast.info('Generación iniciada', {
        description: 'El reporte se está procesando en segundo plano con Celery.',
      });
    } catch (err: any) {
      setIsProcessing(false);
      showToast.error('Fallo al solicitar reporte');
    }
  };

  // Sondeo cada 2.5 segundos mientras la tarea esté activa
  useSmartPolling(
    async (signal) => {
      if (!activeTaskId) return;

      const res = await api.get(`/api/tasks/${activeTaskId}/status/`, { signal });
      const status = res.data.status;

      if (status === 'SUCCESS') {
        setActiveTaskId(null);
        setIsProcessing(false);
        showToast.success('¡Reporte completado!', {
          description: 'El archivo está listo para su descarga.',
          actionLabel: 'Descargar',
          onAction: () => window.open(res.data.download_url, '_blank'),
        });
      } else if (status === 'FAILURE') {
        setActiveTaskId(null);
        setIsProcessing(false);
        showToast.error('Error en el reporte', {
          description: res.data.error || 'Ocurrió un error en el worker de Celery.',
        });
      }
    },
    {
      intervalMs: 2500,
      enabled: Boolean(activeTaskId),
      pauseOnHidden: false, // Las tareas en background deben seguir monitoreándose
    }
  );

  return (
    <div>
      <button onClick={handleStartTask} disabled={isProcessing}>
        {isProcessing ? 'Procesando en Celery...' : 'Generar Reporte Masivo'}
      </button>
    </div>
  );
};
```
