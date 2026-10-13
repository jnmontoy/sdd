# Convenciones y Reglas del Ecosistema Greenfield / Jolifoods

> **PROPÓSITO**:
> Este documento contiene las convenciones operativas de negocio, datos y diseño que los agentes de IA deben recordar en cualquier sesión.

---

## 📅 1. Manejo de Fechas y Zonas Horarias
* **Zona Horaria Oficial**: `America/Bogota` (UTC-5).
* **Almacenamiento en DB**: UTC ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).
* **Visualización en UI**: Formato `DD/MM/YYYY HH:MM:SS` (12h o 24h según el módulo).
* **Nombres de Meses**: Español (Enero, Febrero, ...).

---

## 💰 2. Moneda y Formato Numérico
* **Moneda Base**: Peso Colombiano (`COP`), salvo especificación en dólares (`USD`).
* **Formato Visual**: `$ 1.250.000` (Separador de miles punto `.`, decimal coma `,`).
* **Cálculos Backend**: Tipo `Decimal` de Python (`from decimal import Decimal`). Prohibido usar `float` para montos de dinero para evitar errores de redondeo de punto flotante.

---

## 🏢 3. Identidad de Marca y Colores Oficiales
* **Verde Primario Jolifoods**: `#00a859` / `#059669` (Esmeralda corporativo).
* **Modo Oscuro Oficial**: Fondo `#0f172a`, Tarjetas `#1e293b`, Borde `#334155`.
* **Modo Claro Oficial**: Fondo `#f8fafc`, Tarjetas `#ffffff`, Borde `#e2e8f0`.
* **Logos Oficiales**: `Jolifoods.svg`, `Joli.svg`, `logoJoli.png`. Copiados siempre en `./assets/` locales de cada módulo.

---

## 🗄️ 4. Convenciones de Nomenclatura en Base de Datos
* **Nombres de Tablas**: Minúsculas en singular o plural consistente con prefijo de app (ej. `logistica_despacho`, `calidad_inspeccion`).
* **Claves Primarias**: `id` auto-incremental tipo BigAutoField o UUID según el módulo.
* **Auditoría Obligatoria**: Todo modelo debe incluir `creado_en` (`auto_now_add=True`) y `actualizado_en` (`auto_now=True`).
* **Borrado Lógico**: Preferir bandera `activo = models.BooleanField(default=True)` antes que borrado físico `DELETE`, con registro de justificación en auditoría.
