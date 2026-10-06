# Protocolo de Migraciones de Base de Datos Zero-Downtime y Disaster Recovery
## Ecosistema Corporativo Jolifoods / Greenyard — Metodología SDD

Este protocolo rige las modificaciones estructurales en bases de datos PostgreSQL en producción, garantizando disponibilidad 24/7 sin bloqueos de tabla (*zero table lock*) y la política de recuperación ante desastres (**RPO/RTO**).

---

## 1. Patrón "Expand and Contract" (Regla Inflexible de Despliegue)

Queda estrictamente prohibido aplicar migraciones DDL destructivas (renombrar columnas, eliminar campos o añadir restricciones `NOT NULL` sin valor por defecto) en un solo paso.

```
       PASO 1 (Expand)                PASO 2 (Migrate Data)             PASO 3 (Contract)
┌───────────────────────────┐     ┌───────────────────────────┐     ┌───────────────────────────┐
│ Añadir nueva columna como │ ──> │ Tarea Celery en segundo   │ ──> │ Desplegar código v2.      │
│ NULLABLE. El código nuevo │     │ plano copia datos de la   │     │ Eliminar columna antigua  │
│ escribe en ambas columnas.│     │ columna vieja a la nueva. │     │ en migración posterior.   │
└───────────────────────────┘     └───────────────────────────┘     └───────────────────────────┘
```

### Reglas Técnicas para PostgreSQL:
1. **Creación de Índices sin Bloqueo**:
   - Todo índice nuevo en tablas con más de 10,000 filas debe crearse con la cláusula `CONCURRENTLY`:
     ```sql
     CREATE INDEX CONCURRENTLY idx_usuarios_documento ON core_usuario(numero_documento);
     ```
2. **Adición de Columnas con Valor por Defecto**:
   - En PostgreSQL >= 11, `ALTER TABLE ... ADD COLUMN campo TYPE DEFAULT valor;` no reescribe la tabla si el default es constante. En versiones previas o con funciones dinámicas, la columna debe nacer `NULLABLE` y poblarse asíncronamente.
3. **Timeout de Bloqueo de Cerradura (`lock_timeout`)**:
   - En scripts de migración Django, fijar `SET lock_timeout = '3s';`. Si la migración no puede adquirir la cerradura en 3 segundos para no congelar las transacciones del usuario, la migración aborta y reintenta más tarde.

---

## 2. Lotes Controlados para Migración de Datos Masivos

Para actualizar millones de registros históricos, se prohíbe terminantemente ejecutar un `UPDATE` masivo en una sola transacción SQL. Debe utilizarse un script Celery que itere por lotes de claves primarias:

```python
def migrar_datos_en_lotes(batch_size=1000):
    """Evita bloqueos de tabla y sobrecarga del WAL en PostgreSQL."""
    ultimo_id = 0
    while True:
        registros = list(
            Modelo.objects.filter(id__gt=ultimo_id)
            .order_by('id')[:batch_size]
            .values_list('id', flat=True)
        )
        if not registros:
            break
        
        # Procesar lote
        Modelo.objects.filter(id__in=registros).update(nueva_columna=...)
        ultimo_id = registros[-1]
```

---

## 3. Política de Recuperación ante Desastres (Disaster Recovery)

Toda base de datos del ecosistema Jolifoods debe cumplir los siguientes parámetros de resiliencia:

| Parámetro | Definición | Meta Corporativa | Mecanismo de Garantía |
| :--- | :--- | :--- | :--- |
| **RPO (Recovery Point Objective)** | Máxima pérdida de datos admisible en tiempo | **< 15 minutos** | WAL Archiving continuo (Write-Ahead Logging) hacia almacenamiento S3/Object Storage secundario. |
| **RTO (Recovery Time Objective)** | Tiempo máximo para restaurar el servicio tras un desastre | **< 30 minutos** | Snapshot diario automatizado + script de restauración en un solo comando (`restore_db.sh`). |

### Simulacro de Restauración (Drill):
- Cada trimestre debe ejecutarse una restauración completa en un ambiente de staging estéril, verificando integridad referencial y suma de comprobación (*checksum*).
