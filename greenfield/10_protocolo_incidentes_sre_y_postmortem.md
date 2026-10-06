# Protocolo de Gestión de Incidentes Críticos, SRE y Post-Mortem Sin Culpa
## Ecosistema Corporativo Jolifoods / Greenyard — Metodología SDD

Este protocolo estandariza la respuesta operativa del equipo de ingeniería ante incidentes en producción, la comunicación interna y la cultura de mejora continua basada en **Blameless Post-Mortems**.

---

## 1. Clasificación de Severidad de Incidentes

| Severidad | Impacto en el Negocio | Tiempo de Respuesta (MTTA) | Tiempo de Mitigación (MTTR) | Canal de Activación |
| :--- | :--- | :--- | :--- | :--- |
| **SEV-1 (Crítico)** | Sistema totalmente inaccesible, transacciones detenidas, pérdida o corrupción de datos. | **< 5 minutos** | **< 30 minutos** | Sirena automática PagerDuty / Llamada telefónica inmediata a Tech Lead y DevOps. |
| **SEV-2 (Mayor)** | Módulo principal con fallas severas (ej. facturación caída, pero el resto opera). | **< 15 minutos** | **< 2 horas** | Alerta en canal prioritario `#ops-emergencias` con mención `@here`. |
| **SEV-3 (Menor)** | Degradación de rendimiento o fallas cosméticas sin impacto en la continuidad operativa. | **< 2 horas** | **< 24 horas** | Ticket en backlog con prioridad Alta. |

---

## 2. Protocolo de Sala de Guerra (War Room) para SEV-1

1. **Roles Asignados**:
   - **Comandante del Incidente (IC)**: Dirige la estrategia de resolución y toma decisiones ejecutivas.
   - **Líder Operativo (Tech Lead / SRE)**: Investiga logs, métricas y ejecuta rollbacks o parches.
   - **Líder de Comunicaciones**: Mantiene informada a la gerencia de operaciones y usuarios clave cada 15 minutos.
2. **Regla de Oro en Producción**:
   - **Primero mitigar, luego investigar la causa raíz**. Si un despliegue reciente causó la falla, la acción inmediata e incuestionable es el **ROLLBACK** a la versión estable previa.

---

## 3. Plantilla Oficial de Post-Mortem Sin Culpa (*Blameless Post-Mortem*)

Todo incidente SEV-1 o SEV-2 exige la redacción y publicación de este reporte en menos de 48 horas hábiles:

```markdown
# Reporte Post-Mortem de Incidente — [SEV-X] [Título Breve]
**Fecha del Incidente**: AAAA-MM-DD  
**Duración Total**: XX minutos  
**Líder del Incidente**: Nombre y Cargo  

## 1. Resumen Ejecutivo
Breve descripción orientada a directores sobre qué ocurrió, a quiénes afectó y cómo se solucionó.

## 2. Impacto Cuantificado
- Usuarios afectados: XXX
- Transacciones no procesadas: XXX
- Tiempo total de indisponibilidad: XX min

## 3. Cronología Minuto a Minuto (Horas UTC-5)
- 10:02 - Se despliega versión v2.4.1 en producción.
- 10:07 - Alerta en canal #ops por disparo de latencia p95 > 1200ms.
- 10:11 - Se activa War Room con Comandante de Incidente.
- 10:15 - Se identifica bloqueo en tabla core_transaccion.
- 10:18 - Se ejecuta rollback a v2.4.0.
- 10:22 - Métricas regresan a parámetros normales (SLO restaurado).

## 4. Análisis de Causa Raíz (Los 5 Porqués)
1. ¿Por qué se congeló el sistema? -> Porque la base de datos se bloqueó.
2. ¿Por qué se bloqueó? -> Porque se ejecutó un ALTER TABLE sin timeout de lock.
3. ¿Por qué se ejecutó ese comando? -> Porque la migración no siguió el protocolo Expand & Contract.
4. ¿Por qué no se detectó en CI? -> Porque no se ejecutó oasdiff ni prueba de migración en staging.
5. ¿Por qué no había prueba en staging? -> Falta de regla estricta en el pipeline.

## 5. Acciones Preventivas Inmediatas (Action Items con Responsable y Fecha)
- [ ] Incorporar script de validación de lock_timeout en el CI (DevOps - 3 días).
- [ ] Actualizar documentación del módulo con checklist obligatorio (Tech Lead - 2 días).
```
