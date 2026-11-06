# Tablero de Estado del Servidor (`ServerStatusDashboard`)
## SDD Joli Foods — Spec-Driven Development

Vista de **operación y soporte** para administradores: muestra de un vistazo si la plataforma está sana (servicios, recursos, tiempos de respuesta, errores) y permite leer los logs del backend sin entrar al servidor. Implementación de referencia: Pandora (`frontend-admin/src/components/estado/`, `backend/api/estado_servidor.py`).

> **Privacidad (DEBE, Ley 1581 de 2012):** los logs traen documento, correo e IP. Todo lo que el backend devuelve al panel DEBE ir **enmascarado** (documento `103••••282`, correo `jo•••@dominio`, IP sin el último bloque); para soporte basta el nombre del usuario. Las métricas de uso son **agregadas** (por plataforma y endpoint), no por persona. Solo administradores (`is_staff`).

---

## 1. Anatomía

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ [Dashboard | Tabla]  [Última hora | 24 h | 7 días]     ● Operativo · Actualizado 10:42 [↻] │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ KPIs: Usuarios en línea · Peticiones · Tiempo de respuesta p95 · Errores del servidor  │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ▸ Servicios   ●●●●●○  5 de 6 operativos            [Servicios 6/6 ▾]  (acordeón)     │
│   ◠ API   ◠ Base de datos   ◠ OSRM   ◠ Geoapify   ◠ Disco   ◠ Chat                    │
├───────────────────────────────────────────────┬──────────────────────────────────────┤
│ Peticiones por plataforma (barras apiladas)   │ Recursos: CPU, memoria, disco        │
├───────────────────────────────┬───────────────┴──────────┬───────────────────────────┤
│ Más consultados / más lentos  │ Uso de la plataforma     │ Logs y último error       │
├───────────────────────────────┴──────────────────────────┴───────────────────────────┤
│ Sincronización de la app móvil (si trabaja sin conexión): cifras + lista de celulares │
└───────────────────────────────┴──────────────────────────┴───────────────────────────┘
```

- **Estado general = punto + texto** en la barra superior (no una tarjeta KPI): 🟢 Operativo, 🟡 Con alertas, 🔴 Caído, con los servicios afectados al lado. El punto late (respeta `prefers-reduced-motion`).
- **Servicios en acordeón con tacómetros.** La cabecera conserva **siempre un punto por servicio**, aunque el acordeón esté cerrado o el tacómetro del servicio esté oculto con el selector: así una falla se ve de inmediato.
- **Selector Dashboard / Tabla**: la Tabla son las líneas de los logs (sección 5).
- Se actualiza cada 30 s con la pestaña visible; el botón Actualizar fuerza la revisión de servicios en el momento.

---

## 2. Servicios y tacómetros

Cada servicio entrega `estado` (`ok | advertencia | caido | sin_configurar`), un `detalle`, y para el tacómetro `valor`, `maximo`, `unidad` y los umbrales `advertencia` / `critico`:

| Servicio | Qué mide la aguja | Escala sugerida (máx · amarillo · rojo) |
|---|---|---|
| API | p95 de las peticiones del periodo | 1000 · 300 · 800 ms |
| Base de datos | `SELECT 1` | 1000 · 200 · 500 ms |
| Ruteo (OSRM) | cálculo de una ruta corta sobre **conexión reutilizada** ([BUG-011](../../memory/learnings/bug_lessons.md#bug-011)) | 5000 · 1500 · 3000 ms |
| Geocodificación (cupo diario) | % del cupo usado, **sin consultar la API** | 100 · 80 · 100 % |
| Disco | % usado | 100 · 85 · 95 % |
| Chat en tiempo real | conectados / usuarios activos | sin zonas |

**Solo servicios de uso recurrente (DEBE).** Lo que se usa de vez en cuando (una BD externa que solo se consulta con un botón de sincronizar, el correo de recuperación de contraseña) NO se vigila cada 30 s: deja conexiones abiertas contra sistemas ajenos y genera alertas sin impacto real. Si hace falta, se prueba a demanda.

Reglas:
- Las revisiones corren **a la vez y con tiempo límite**, fuera del hilo de FastAPI (`asyncio.gather`, `asyncio.to_thread`), y se guardan 30 s en caché para no saturar los servicios.
- Un servicio caído o sin configurar muestra su estado en el centro del tacómetro, sin aguja.
- El estado va siempre con **ícono + texto** (nunca solo color); los colores de zona son los de estado (`--status-success/warning/error`).
- No exponer mensajes del controlador de base de datos: pueden traer el servidor o el usuario. Basta el tipo de error.

---

## 3. Peticiones por plataforma

- El middleware de auditoría DEBE anotar la plataforma en cada línea del log: `[Plataforma: apk|admin|otro]`. La app móvil envía su cabecera (`X-Pandora-Plataforma: apk`); el resto de `/api` es el panel.
- Barras apiladas por intervalo (5 min, 1 h o 6 h según el periodo), **un solo eje**, leyenda y ayuda flotante por barra. Colores categóricos validados para daltonismo (skill de visualización): azul = app móvil, naranja = panel.
- Las consultas del propio tablero (`/api/v1/admin/estado`) NO cuentan en las métricas.
- Endpoints agrupados con la ruta normalizada (`/visitas/:codigo`, `/:id`, `/:fecha`).

---

## 4. Lectura de logs (backend)

- Formato de línea fijo: `[AAAA-MM-DD HH:MM:SS] [NIVEL] [origen] mensaje`; las líneas siguientes sin ese formato son la traza del error anterior.
- Leer `backend.log` y sus rotados (`.1` … `.5`) hasta cubrir el periodo; caché por archivo que **solo lee lo nuevo** cuando el archivo crece y se reinicia si rota.
- Enmascarar en el servidor, nunca en el navegador: correos, secuencias de 6 a 15 dígitos (documentos) e IPv4.

---

## 5. Vista Tabla (logs)

Sigue [`data_table/data_table.md`](../data_table/data_table.md) completo: buscador con una sola X, grupo de filtros (log `backend.log`/`errors.log`, nivel, plataforma), **filtros por columna tipo Excel** ([`checklist_popover.md`](../data_table/checklist_popover.md)), orden por encabezado, ancho ajustable ([`column_resizer.md`](../data_table/column_resizer.md)), visibilidad de columnas, paginación y fila desplegable con el mensaje completo y la traza. La fecha se filtra agrupada por hora; duración y mensaje no se filtran (solo se ordenan).

---

## 6. Contrato de datos (resumen)

```typescript
interface ServicioEstado {
  clave: string; nombre: string;
  estado: 'ok' | 'advertencia' | 'caido' | 'sin_configurar';
  detalle: string; descripcion?: string; latencia_ms?: number | null;
  valor?: number | null; maximo?: number | null; unidad?: 'ms' | '%' | 'usuarios' | '';
  advertencia?: number | null; critico?: number | null;
}

interface EstadoServidorResponse {
  generado_en: string; horas: number;
  estado_general: 'ok' | 'advertencia' | 'caido';
  servicios: ServicioEstado[];
  recursos: { cpu_pct: number; memoria_pct: number; disco_pct: number; /* … */ };
  uso: { apk_en_linea: number; admin_en_linea: number; /* hoy, 30 días, chat … */ };
  peticiones: { total: number; p50_ms: number | null; p95_ms: number | null; barras: BarraPeticiones[]; /* … */ };
  errores: { errores: number; advertencias: number; ultimo_error: { fecha_hora: string; mensaje: string } | null };
  logs: { archivo: string; tamano_mb: number; rotados: number }[];
}
```

Endpoints: `GET /api/v1/admin/estado?horas=24&forzar=false` y `GET /api/v1/admin/estado/logs?archivo=general|errores&horas=24&limite=5000`. Dependencia del backend: `psutil` (CPU, memoria, disco).

---

## Sincronización de la app móvil (si la app trabaja sin conexión)

Si la app móvil guarda primero en el celular y sube después (local-first), el tablero DEBE mostrar lo que aún no llega al servidor; si no, un «yo sí lo marqué» no se puede verificar.

- **Reporte:** la app manda su resumen en la consulta periódica de sesión (cabeceras: pendientes, desde cuándo el más antiguo, rechazados, red débil, versión). El backend guarda **solo lo último** por usuario, y escribe si cambió o cada 5 min (no en cada consulta).
- **Cifras:** celulares reportando (15 min), con cambios sin subir, total sin subir, rechazados, con red débil, alertas.
- **Lista:** solo celulares con algo pendiente, rechazado o red débil; nombre (sin documento), qué tiene, «reportó hace…» y versión. Primero las alertas.
- **Alerta:** un cambio con más de N horas sin subir (Pandora: 4 h). Un celular sin señal **no puede reportar**: por eso se muestra la hora del último reporte, no se asume que está al día.

