# Protocolo 10: gestión de incidentes y análisis posterior sin culpa

Cómo responder a un incidente en producción, cómo comunicarlo y cómo aprender de él mediante un **post-mortem sin culpa** (análisis posterior que busca causas en el sistema y el proceso, no culpables).

Las palabras **DEBE / DEBERÍA / PUEDE** siguen la RFC 2119.

> **Estado de implementación**: este protocolo es normativo. La organización DEBE definir, por sistema, la herramienta de guardia y el canal de comunicación de incidentes; los nombres usados abajo son ejemplos.

---

## 1. Severidades

| Severidad | Impacto en el negocio | Reconocer (MTTA objetivo) | Mitigar (objetivo) | Activación |
|---|---|---|---|---|
| **SEV-1 (crítico)** | Sistema inaccesible, operación detenida, pérdida o corrupción de datos, o incidente de seguridad con datos expuestos. | < 15 min en horario laboral | < 4 h | Llamada directa al responsable técnico de guardia y al líder del área afectada. |
| **SEV-2 (mayor)** | Un módulo principal falla o se degrada gravemente, pero hay alternativa o el resto opera. | < 30 min | < 1 día hábil | Mensaje en el canal de incidentes del equipo (p. ej. `#ops-incidentes`). |
| **SEV-3 (menor)** | Degradación leve o defecto sin impacto en la continuidad. | < 1 día hábil | Según priorización del backlog | Ticket en el backlog. |

* **MTTA** (*Mean Time To Acknowledge*): tiempo hasta que alguien reconoce el incidente. Los tiempos son **objetivos de referencia**; cada sistema los ajusta según su criticidad y la disponibilidad real del equipo (p. ej. si no hay guardia fuera de horario, decirlo explícitamente).
* Ante duda entre dos severidades, se elige la más alta y se baja después.
* Un incidente que exponga datos personales se trata además según el procedimiento de protección de datos de la organización (Ley 1581 de 2012).

---

## 2. Respuesta a un SEV-1 (y SEV-2 cuando aplique)

1. **Roles** (en equipos pequeños una persona puede cubrir dos, pero se nombran explícitamente):
   * **Coordinador del incidente** (*Incident Commander*): decide y prioriza; no necesariamente es quien corrige.
   * **Responsable técnico**: investiga logs, métricas y trazas (protocolo 07) y ejecuta la mitigación.
   * **Responsable de comunicación**: informa a los usuarios afectados y a la gerencia con una cadencia acordada (p. ej. cada 30 min en SEV-1).
2. **Primero mitigar, después investigar.** Si un despliegue reciente coincide con el inicio del incidente, la primera opción DEBERÍA ser revertir a la versión anterior (*rollback*). **Por qué:** restaurar el servicio reduce el daño mientras se busca la causa con calma. Excepción: si el despliegue incluyó una migración de base de datos no reversible, se evalúa antes (protocolo 08).
3. Llevar una línea de tiempo con hora de cada hallazgo y acción mientras ocurre.

---

## 3. Post-mortem sin culpa

Todo SEV-1 DEBE y todo SEV-2 DEBERÍA tener un post-mortem publicado en máximo **5 días hábiles**. Se redacta sobre hechos, en términos de sistema y proceso ("la migración no tenía límite de espera de bloqueo"), nunca de personas ("X olvidó…").

**Por qué sin culpa:** si contar un error tiene castigo, la gente lo oculta y la organización pierde la información para evitar el siguiente.

Plantilla:

```markdown
# Post-mortem — [SEV-X] [Título breve]
**Fecha del incidente**: AAAA-MM-DD
**Duración (detección → mitigación)**: XX min
**Coordinador del incidente (rol)**: ...
**Estado de las acciones**: abiertas / cerradas

## 1. Resumen
Qué pasó, a quién afectó y cómo se resolvió, en lenguaje para no técnicos.

## 2. Impacto
- Usuarios o áreas afectadas: ...
- Transacciones no procesadas o datos afectados: ...
- Tiempo sin servicio: ...

## 3. Línea de tiempo (hora de Colombia, UTC−5)
- 10:02 Se despliega la versión 2.4.1.
- 10:07 Alerta: p95 de latencia > 1,2 s.
- 10:11 Se declara SEV-1 y se nombra coordinador.
- 10:15 Se identifica bloqueo en la tabla `core_transaccion`.
- 10:18 Se revierte a 2.4.0.
- 10:22 Latencia vuelve a valores normales.

## 4. Causas (técnica de los 5 porqués u otra)
1. ¿Por qué se detuvo el sistema? Porque una tabla quedó bloqueada.
2. ¿Por qué se bloqueó? Porque un `ALTER TABLE` esperó un bloqueo exclusivo sin `lock_timeout` y las demás consultas se encolaron detrás.
3. ¿Por qué no tenía `lock_timeout`? Porque la migración no siguió el protocolo 08.
4. ¿Por qué no se detectó antes? Porque la migración no se probó en staging con volumen de datos similar al de producción.
5. ¿Por qué no se probó? Porque el *pipeline* no exige ese paso para migraciones.

(Los 5 porqués suelen revelar varias causas; se registran todas las relevantes, no solo una cadena.)

## 5. Qué funcionó y qué no
- Funcionó: la alerta de latencia detectó el problema en 5 minutos.
- No funcionó: ...

## 6. Acciones (responsable por rol y fecha)
- [ ] Agregar al *pipeline* la verificación de migraciones en staging. (DevOps — AAAA-MM-DD)
- [ ] Incluir `SET LOCAL lock_timeout` en la plantilla de migraciones. (Líder técnico — AAAA-MM-DD)
- [ ] Registrar la lección en `memory/learnings/bug_lessons.md`. (Responsable técnico — AAAA-MM-DD)
```

Las acciones se siguen hasta cerrarse; un post-mortem con acciones abiertas indefinidamente no cumplió su propósito.
