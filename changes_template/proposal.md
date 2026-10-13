# Propuesta de Cambio: [Nombre Breve de la Funcionalidad o Refactor]

## 📌 Metadatos del Cambio
* **Identificador**: `[YYYY-MM-DD]-[nombre-cambio]`
* **Autor / Responsable**: `[Nombre del Ingeniero o Rol]`
* **Fecha de Creación**: `[YYYY-MM-DD]`
* **Nivel ODD**: Nivel 2 (Feature Incremental)
* **Estado**: `[Borrador | Aprobado | En Ejecución | Completado | Descartado]`

---

## 1. Problema de Negocio y Motivación
> Describe qué problema actual existe, qué limitación técnica se presenta o qué nueva necesidad operativa de la organización se busca resolver con este cambio.

* **Situación Actual**:
  * [Explicar cómo funciona hoy el sistema]
* **Impacto Negativo o Cuello de Botella**:
  * [Explicar por qué es necesario modificarlo ahora]

---

## 2. Solución Propuesta (Alcance)
> Define con precisión qué se va a construir o modificar.

* [ ] Capacidad A: [Descripción precisa de la nueva capacidad]
* [ ] Capacidad B: [Descripción de ajustes a componentes existentes]
* [ ] Capacidad C: [Ajustes en contratos o modelos de datos]

---

## 3. Límites Estrictos de Alcance (Out-of-Scope)
> **REGLA DE ORO CONTRA LA ALUCINACIÓN Y OVER-ENGINEERING**:
> La IA tiene prohibido tocar o agregar código fuera de esta lista. Lo que esté listado aquí NO DEBE TOCARSE en este cambio.

* ❌ **NO incluye**: [Ejemplo: No se modifica la tabla de usuarios ni el flujo de login]
* ❌ **NO incluye**: [Ejemplo: No se agregan nuevas dependencias al package.json]
* ❌ **NO incluye**: [Ejemplo: No se rediseñan las vistas existentes, solo se añade el modal]

---

## 4. Criterios de Éxito y Aceptación
> Condiciones innegociables para considerar el cambio exitoso.

1. [Criterio 1: El endpoint responde en < 200ms con paginación server-side]
2. [Criterio 2: La interfaz reutiliza `.sdd/components/drawer/drawer.md` sin inventar CSS]
3. [Criterio 3: El validador `validate_endpoints.py` pasa con Score 100%]
4. [Criterio 4: Cero errores en TypeScript y Pytest]
