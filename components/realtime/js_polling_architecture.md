# Arquitectura Frontend: Polling en Tiempo Real con React (`useSmartPolling`)
## SDD Joli Foods — Spec-Driven Development

Este documento define cómo actualizar datos "en vivo" en las aplicaciones web mediante **short polling** (consultar al servidor cada cierto tiempo con peticiones HTTP normales).

> **Decisión de arquitectura:** el polling es el mecanismo por defecto para datos en vivo. Una auditoría NO DEBERÍA penalizarlo cuando cumple las reglas de este documento (intervalo acorde al caso, pausa con pestaña oculta, cancelación al desmontar y sin peticiones solapadas). Si un caso exige latencia de segundos con muchos usuarios simultáneos, se evalúa WebSockets o SSE (*Server-Sent Events*) con una decisión registrada (ADR).

---

### 1. Por qué polling en lugar de WebSockets

1. **Tolerancia a la red corporativa**: los WebSockets mantienen una conexión TCP abierta que proxies, firewalls de planta o balanceadores (Nginx/Apache) suelen cortar por inactividad; una petición HTTP corta no depende de eso.
2. **Sin estado en el servidor**: cada consulta es una petición HTTP normal que pasa por el cliente `api` (token de acceso en memoria y renovación con cookie `HttpOnly`), se puede cachear en Redis y escala horizontalmente.
3. **Control del cliente**: el frontend puede pausar, acelerar o espaciar las consultas según la visibilidad de la pestaña.

**Costo a tener en cuenta:** cada usuario genera carga periódica aunque no haya cambios. Por eso el intervalo DEBE ajustarse al caso de uso y la consulta del backend DEBERÍA ser liviana (índices, caché, respuesta corta).

---

### 2. Frecuencias recomendadas

| Caso de uso | Intervalo | Pestaña oculta |
| :--- | :--- | :--- |
| Seguimiento de una tarea Celery (`task_id`) | 2 – 3 s | Sigue hasta terminar (éxito o error). `pauseOnHidden: false`. |
| Campana de notificaciones | 30 – 60 s | Se espacia a 120 s (`hiddenIntervalMs: 120000`). |
| Tablas operativas en vivo | 5 – 10 s | Se pausa (`pauseOnHidden: true`). |
| Telemetría e infraestructura | 2 – 5 min | Se pausa. |

---

### 3. Hook reutilizable: `useSmartPolling`

Características:

- **Sin solapamiento**: la siguiente consulta se programa cuando termina la anterior (cadena de `setTimeout`), así una respuesta lenta nunca acumula peticiones.
- **Callback estable**: el callback se guarda en una `ref`; pasar una función nueva en cada render NO reinicia el sondeo.
- **Cancelación**: cada ciclo recibe un `AbortSignal`; al desmontar o deshabilitar se aborta la petición en vuelo y se limpia el temporizador.
- **Visibilidad**: pausa o espacia con la pestaña oculta y consulta de inmediato al volver.

```tsx
// src/hooks/useSmartPolling.ts
import { useEffect, useRef } from 'react';

export interface PollingOptions {
  intervalMs: number;
  enabled?: boolean;
  /** Pausar mientras la pestaña esté oculta (por defecto true). */
  pauseOnHidden?: boolean;
  /** Si se define y no se pausa, intervalo a usar con la pestaña oculta. */
  hiddenIntervalMs?: number;
  /** Ejecutar una consulta al activar el hook (por defecto true). */
  immediate?: boolean;
}

function isAbortError(err: unknown): boolean {
  return (
    (err instanceof DOMException && err.name === 'AbortError') ||
    (typeof err === 'object' && err !== null && 'code' in err && (err as { code?: string }).code === 'ERR_CANCELED') // Axios
  );
}

export function useSmartPolling(
  callback: (signal: AbortSignal) => Promise<void>,
  {
    intervalMs,
    enabled = true,
    pauseOnHidden = true,
    hiddenIntervalMs,
    immediate = true,
  }: PollingOptions
): void {
  const callbackRef = useRef(callback);

  // Siempre la última versión del callback, sin reiniciar el ciclo.
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) return;

    let timerId: ReturnType<typeof setTimeout> | null = null;
    let controller: AbortController | null = null;
    let running = false;
    let stopped = false;

    const isHidden = () => document.visibilityState === 'hidden';

    const schedule = () => {
      if (stopped) return;
      if (timerId) clearTimeout(timerId);
      if (isHidden() && pauseOnHidden) return; // se reanuda en visibilitychange
      const delay = isHidden() && hiddenIntervalMs ? hiddenIntervalMs : intervalMs;
      timerId = setTimeout(tick, delay);
    };

    const tick = async () => {
      if (stopped || running) return;
      if (isHidden() && pauseOnHidden) return;
      running = true;
      controller = new AbortController();
      try {
        await callbackRef.current(controller.signal);
      } catch (err: unknown) {
        if (!isAbortError(err)) {
          console.debug('[useSmartPolling] Error en la consulta; se reintentará en el siguiente ciclo.', err);
        }
      } finally {
        running = false;
        controller = null;
        schedule();
      }
    };

    const handleVisibility = () => {
      if (!isHidden() && !running) {
        if (timerId) clearTimeout(timerId);
        void tick(); // al volver a la pestaña, consultar de inmediato
      } else if (isHidden() && pauseOnHidden && timerId) {
        clearTimeout(timerId);
        timerId = null;
      }
    };

    document.addEventListener('visibilitychange', handleVisibility);
    if (immediate) void tick();
    else schedule();

    return () => {
      stopped = true;
      if (timerId) clearTimeout(timerId);
      controller?.abort();
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, [enabled, intervalMs, pauseOnHidden, hiddenIntervalMs, immediate]);
}
```

---

### 4. Ejemplo: seguimiento de una tarea pesada en Celery

Las rutas salen del catálogo `ENDPOINTS` (sin URLs quemadas) y todas las peticiones usan el cliente `api`, que agrega el token de acceso desde memoria.

```typescript
// src/services/endpoints.ts (fragmento de ejemplo; registrar también en endpoints_registry.json)
export const ENDPOINTS = {
  // ...
  REPORTES: {
    GENERAR_MASIVO: '/api/v1/reportes/generar-masivo/',
    DESCARGAR: (taskId: string) => `/api/v1/reportes/${taskId}/descargar/`,
  },
  TAREAS: {
    ESTADO: (taskId: string) => `/api/v1/tareas/${taskId}/estado/`,
  },
} as const;
```

```tsx
// src/components/ReportGenerator.tsx
import React, { useCallback, useState } from 'react';
import { useSmartPolling } from '@/hooks/useSmartPolling';
import { showToast } from '@/components/ui/ToastNotification';
import { api } from '@services/api';
import { ENDPOINTS } from '@services/endpoints';

type TaskStatus = 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'REVOKED';

interface TaskStatusResponse {
  status: TaskStatus;
  error_message?: string; // mensaje apto para el usuario; el backend NO DEBE enviar trazas internas
}

async function downloadReport(taskId: string): Promise<void> {
  // Descarga autenticada: un window.open() no enviaría la cabecera Authorization.
  const res = await api.get<Blob>(ENDPOINTS.REPORTES.DESCARGAR(taskId), { responseType: 'blob' });
  const url = URL.createObjectURL(res.data);
  const link = document.createElement('a');
  link.href = url;
  link.download = `Reporte_${taskId}.xlsx`;
  link.click();
  URL.revokeObjectURL(url);
}

export const ReportGenerator: React.FC = () => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);

  const handleStartTask = async () => {
    setIsStarting(true);
    try {
      const res = await api.post<{ task_id: string }>(ENDPOINTS.REPORTES.GENERAR_MASIVO);
      setActiveTaskId(res.data.task_id);
      showToast.info('Generación iniciada', {
        description: 'El reporte se está procesando en segundo plano.',
      });
    } catch {
      showToast.error('No fue posible solicitar el reporte');
    } finally {
      setIsStarting(false);
    }
  };

  const pollStatus = useCallback(
    async (signal: AbortSignal) => {
      if (!activeTaskId) return;
      const res = await api.get<TaskStatusResponse>(ENDPOINTS.TAREAS.ESTADO(activeTaskId), { signal });
      const { status, error_message } = res.data;

      if (status === 'SUCCESS') {
        const taskId = activeTaskId;
        setActiveTaskId(null);
        showToast.success('Reporte completado', {
          description: 'El archivo está listo para descargar.',
          actionLabel: 'Descargar',
          onAction: () => {
            downloadReport(taskId).catch(() => showToast.error('No fue posible descargar el archivo'));
          },
        });
      } else if (status === 'FAILURE' || status === 'REVOKED') {
        setActiveTaskId(null);
        showToast.error('Error en el reporte', {
          description: error_message ?? 'La tarea no pudo completarse. Intenta de nuevo.',
        });
      }
    },
    [activeTaskId]
  );

  // Sondeo cada 2,5 s mientras haya una tarea activa; sigue aunque la pestaña esté oculta.
  useSmartPolling(pollStatus, {
    intervalMs: 2500,
    enabled: activeTaskId !== null,
    pauseOnHidden: false,
  });

  const isProcessing = isStarting || activeTaskId !== null;

  return (
    <button type="button" className="btn btn-primary" onClick={handleStartTask} disabled={isProcessing} aria-busy={isProcessing}>
      {isProcessing ? 'Procesando reporte…' : 'Generar reporte masivo'}
    </button>
  );
};
```
