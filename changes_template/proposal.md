# Propuesta de cambio: [Nombre breve de la funcionalidad o refactor]

## Metadatos
* **Identificador**: `AAAA-MM-DD-nombre-cambio`
* **Responsable (rol)**: `[Rol o equipo]`
* **Fecha de creación**: `AAAA-MM-DD`
* **Nivel**: 2 (cambio atómico)
* **Estado**: `[Borrador | Aprobado | En ejecución | Completado | Descartado]`
* **Aprobado por / fecha**: `[Rol] — AAAA-MM-DD`

---

## 1. Problema y motivación
> Qué ocurre hoy, a quién afecta y por qué conviene cambiarlo ahora. Distingue hechos (datos, incidentes) de supuestos.

* **Situación actual**: [cómo funciona hoy]
* **Impacto**: [qué cuesta no hacerlo: tiempo, errores, riesgo]
* **Evidencia**: [ticket, métrica, queja recurrente; o "supuesto, sin medir"]

---

## 2. Solución propuesta (alcance)
* [ ] Capacidad A: [descripción concreta]
* [ ] Capacidad B: [ajuste a componente existente]
* [ ] Capacidad C: [cambio en contrato o modelo de datos]

### Alternativas consideradas
| Alternativa | Por qué se descarta |
|---|---|
| [No hacer nada] | [...] |
| [Opción B] | [...] |

---

## 3. Fuera de alcance
> Lo listado aquí NO DEBE modificarse en este cambio. Si durante la ejecución aparece la necesidad, se registra como cambio nuevo.

* NO incluye: [ej. modificar la tabla de usuarios o el flujo de login]
* NO incluye: [ej. agregar dependencias nuevas a `package.json` o `requirements.txt`]
* NO incluye: [ej. rediseñar vistas existentes]

---

## 4. Impacto en otras áreas o sistemas
> Quién más se ve afectado (otras unidades de negocio, integraciones, reportes, usuarios de otros módulos) y cómo.

* [ej. El reporte de inventario consume este endpoint: requiere aviso de deprecación (protocolo 09)]

---

## 5. Criterios de aceptación
> Condiciones verificables. Cada una debe poder demostrarse en `evidence.md`.

1. [ej. `GET /api/v1/pedidos/?estado=...` responde con paginación en servidor y p95 < 500 ms en staging con N registros]
2. [ej. La interfaz usa `components/drawer/drawer.md` sin CSS nuevo]
3. [ej. `pruebas/validate_endpoints.py` termina con código de salida 0]
4. [ej. Pruebas nuevas en `pruebas/` cubren el caso feliz y los casos de borde de `design.md`]
