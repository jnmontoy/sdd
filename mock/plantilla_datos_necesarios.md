# Especificación Universal de Datos Requeridos del Backend (Contrato JSON)
## Módulo / Pantalla: [NOMBRE_DE_LA_PANTALLA_O_TEMA] (Ej: Control de Calidad, Inventario de Lotes, Despachos, Ventas, etc.)
**Dominio / Área Solicitante**: [Ej: Producción, Calidad, Logística, Comercial, etc.]  
**Solicitante**: [Cargo del usuario no técnico (no es necesario el nombre)]  
**Fecha de Entrega**: [YYYY-MM-DD]  
**Archivo Mockup Asociado**: `[NOMBRE_DEL_MOCKUP].html`  

> **PRINCIPIO DE AGNOSTICISMO DEL SDD**:
> El sistema SDD **NO asume temas fijos ni está atado a ventas**. Puede aplicarse a **cualquier necesidad de la organización** (control de calidad, bodega, transporte, mantenimiento, producción, etc.). 
> Lo que se mantiene **constante y reutilizable** es la estructura visual corporativa: Rejilla de Métricas (`KpiCard`), Tabla interactiva con filtros (`DataTable`), Buscador reactivo (`SearchInput`), Modales de confirmación (`ConfirmModal`) y Conmutador de tema, **sin inventar CSS nuevo ni componentes ad-hoc**.

---

## 1. Resumen de la Necesidad (Objetivo de Negocio)
Explica en tus propias palabras qué proceso deseas monitorear o gestionar en esta pantalla:
> *Ejemplo A (Calidad): "Controlar en tiempo real la temperatura y humedad de los cuartos de almacenamiento de materia prima y alertar al jefe de calidad cuando salgan de rango."*  
> *Ejemplo B (Logística): "Rastrear camiones en ruta, temperatura de la cadena de frío y hora estimada de llegada a planta."*  
> *Ejemplo C (Inventario): "Controlar lotes de materia prima, fechas de vencimiento y alertas de rotación."*

---

## 2. Indicadores Clave del Tablero (Métricas / KPIs)
Valores agregados que deben resumir el estado del módulo en tarjetas visuales superiores:

| Clave JSON | Nombre Visible | Tipo de Dato | Ejemplo de Valor | Descripción de Negocio |
| :--- | :--- | :--- | :--- | :--- |
| `[metrica_1]` | [Ej: Temperatura promedio / Stock total / Ventas] | Decimal / Entero | `21,4 °C` o `1.240 kg` | Indicador principal del proceso |
| `[metrica_2]` | [Ej: Humedad Relativa / Meta / Eficiencia] | Porcentaje | `78.5 %` | Nivel o porcentaje de avance |
| `[metrica_3]` | [Ej: Lotes en Riesgo / Pendientes / Alertas] | Entero | `3 sensores` o `12 alertas` | Alertas de advertencia (color amarillo) |
| `[metrica_4]` | [Ej: Críticos / Vencidos / Máquinas Paradas] | Entero | `1 zona crítica` | Casos que requieren atención urgente (rojo) |

---

## 3. Listado Principal (Array de Registros JSON)
Estructura de datos que contendrá cada fila de la tabla o cuadrícula. El backend entregará un arreglo (`List[Schema]`):

### Ejemplo de Estructura JSON (Un elemento del Array según tu dominio):

```json
{
  "id": 101,
  "codigo_referencia": "SEN-BODEGA-04",
  "fecha_registro": "2026-09-30T14:30:00",
  "entidad_principal": {
    "nombre": "Sensor Cuarto de Materia Prima 2",
    "ubicacion_o_categoria": "Bodega Principal - Zona B"
  },
  "valor_medicion_1": 22.8,
  "valor_medicion_2": 82.0,
  "estado": "NORMAL",
  "responsable": "Jefe de Calidad (rol de ejemplo)",
  "acciones_permitidas": ["ver_grafico_historico", "calibrar_sensor", "desactivar"]
}
```

### Diccionario de Campos de la Tabla:
| Campo JSON | Etiqueta en Pantalla | Tipo de Dato | ¿Obligatorio? | Formato Visual / Unidad | Estados / Badges |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `codigo_referencia` | Código / Identificador | String | Sí | Negrita | Código único |
| `fecha_registro` | Fecha y Hora | ISO 8601 | Sí | `30 Sep 2026, 02:30 PM` | Formato legible |
| `entidad_principal.nombre` | Nombre / Descripción | String | Sí | Texto normal | Nombre del elemento |
| `valor_medicion_1` | [Medición Principal] | Numérico | Sí | Ej: `22,8 °C` o `$ 1.500.000` | Unidad de medida clara |
| `estado` | Estado | String | Sí | Badge de Color SDD | `ACTIVO / NORMAL` (Verde), `ALERTA / PENDIENTE` (Amarillo), `CRÍTICO / FALLA` (Rojo) |

---

## 4. Filtros y Búsqueda Requeridos
Parámetros que el usuario podrá manipular en la interfaz para filtrar los datos:

- `q`: Búsqueda de texto libre (busca por código, nombre, ubicación o responsable).
- `estado`: Selector rápido de estados (`NORMAL`, `ALERTA`, `CRÍTICO`).
- `rango_fechas`: Filtro por fecha inicial y fecha final.
- `categoria_o_zona`: Filtro por sede, bodega o línea de producción.
- `page` y `page_size`: Paginación (por defecto 20 registros por página).

---

## 5. Matriz de Permisos por Rol (¿Quién puede ver y hacer qué?)
*Define la visibilidad de datos sensibles y las acciones según el usuario logueado:*

| Perfil de Usuario | ¿Puede ver esta pantalla? | Columnas o Datos Sensibles Visibles | ¿Puede Modificar / Anular? | ¿Puede Descargar Reporte? |
| :--- | :--- | :--- | :--- | :--- |
| **Administrador / Jefatura** | Sí (Acceso Total) | Todas las métricas y configuraciones | Sí (con justificación) | Sí (Todos los registros) |
| **Supervisor / Técnico** | Sí | Mediciones y alertas de su zona | Sí (solo calibración / ajustes) | Sí (Su área) |
| **Operario / Consultor** | Sí (Solo Lectura) | Datos generales de operación | **No** (Botones de acción ocultos) | No |

---

## 6. Acciones Críticas / Peligrosas y Modal de Confirmación (`ConfirmModal`)
*Cualquier acción destructiva o de impacto debe usar el modal corporativo con justificación:*

- **Acción Crítica**: [Ej: Desactivar Sensor / Apagar Máquina / Anular Registro / Rechazar Lote].
- **Título del Modal**: `"¿Está seguro de [acción] en [código_referencia]?"`
- **Mensaje de Advertencia**: `"Esta acción afectará los promedios históricos y enviará una notificación al equipo de guardia. Esta acción queda registrada en la bitácora de auditoría."`
- **¿Exige Motivo Obligatorio?**: **Sí**. Campo de texto libre (mínimo 10 o 15 caracteres).
- **Feedback**: `ToastNotification` corporativa en verde (éxito) o rojo (error).

---

## 7. Comportamiento ante Estado Vacío (Empty State)
*Cómo responde la pantalla cuando no hay datos disponibles:*

1. **Cuando no hay registros iniciales**:
   - Icono: `inbox` o `cloud-off`.
   - Mensaje: `"No hay [registros / mediciones] disponibles para el período seleccionado."`
   - Botón CTA: `[+ Registrar Nueva Entrada]` o `[Actualizar Conexión]`.
2. **Cuando la búsqueda da 0 coincidencias**:
   - Icono: `search-x`.
   - Mensaje: `"No se encontraron resultados que coincidan con la búsqueda."`
   - Botón CTA: `[Limpiar Filtros]`.

---

## 8. Dispositivos y Entorno de Uso (Responsive)
- **¿Dónde se utilizará?**:
  - `[ ]` Computador de escritorio en oficina (Pantalla grande, uso intensivo de mouse y teclado).
  - `[ ]` Tablet en campo / bodega / planta (Botones táctiles grandes, layout que no dependa de scroll horizontal forzado).
  - `[ ]` Celular corporativo (Tarjetas apiladas verticalmente en lugar de tabla ancha).

---

## 9. Datos de Ejemplo Copiados desde Hoja de Cálculo (Opcional)
*Pega aquí una tabla en texto plano para que la IA la convierta a datos JSON del mock.*

> **Antes de pegar**: usa datos ficticios o anonimizados con la misma forma que los reales. NO incluyas nombres, cédulas, correos o teléfonos de personas reales, ni costos, fórmulas, recetas o cifras financieras no públicas. Para el mock basta con que los valores sean verosímiles.

```text
| Código         | Fecha / Hora      | Nombre / Sensor            | Valor Medido | Estado   |
| SEN-001        | 30/09/2026 14:00  | Cuarto Frío Norte         | 22.4 °C      | NORMAL   |
| SEN-002        | 30/09/2026 14:15  | Bodega Sur                 | 28.1 °C      | ALERTA   |
| SEN-003        | 30/09/2026 14:30  | Bodega Refrigerada 2       | 4.2 °C       | NORMAL   |
```
