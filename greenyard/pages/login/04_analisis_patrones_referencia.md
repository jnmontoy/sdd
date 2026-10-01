# 04. Arquetipos Arquitectónicos y Patrones de Referencia
## Módulo de Login / Autenticación — SDD Greenyard (`GY-SPEC-AUTH-001`)

Este documento define la taxonomía formal de los arquetipos de autenticación contemplados en la arquitectura, sus fortalezas, vectores de riesgo y las decisiones técnicas canónicas adoptadas en esta especificación.

---

## 1. Matriz de Arquetipos Arquitectónicos

| Arquetipo | Enfoque de Autenticación | Almacenamiento de Sesión | Validación en Cliente | Fortalezas | Riesgos Mitigados por SDD |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Arquetipo A: Operativo / Quiosco** | Documento físico directo | Token de sesión acotado | Validación numérica simple | Máxima agilidad para turnos operativos de alta rotación. | Aislamiento en subredes locales y token con tiempo de vida reducido. |
| **Arquetipo B: Corporativo con Persistencia** | Documento + Clave / SSO | Cookie / Storage con "Recuérdame" | Validación de campos y visibilidad | Ergonomía para personal administrativo, toggle de contraseña. | Separación entre documento recordado (no sensible) y credencial. |
| **Arquetipo C: Fortalecido contra XSS** | Documento + Clave | **Cookies HttpOnly (`SameSite=Lax`)** | **`Zod` estricto en cliente** | **Máxima seguridad**: Inmunidad total a robo de sesión por script malicioso. | Mitiga fugas por dependencias de terceros o inyección de scripts. |
| **Arquetipo D: Híbrido con SSO Forzado** | Bifurcación según jerarquía de rol | Cookie HttpOnly | Pre-chequeo de rol en vuelo | Gobernanza: Obliga a perfiles de Administrador a usar MFA/SSO. | Previene que administradores usen contraseñas locales débiles. |
| **Arquetipo E: Biometría con Resiliencia** | Reconocimiento Facial + Fallback | Cookie de sesión segura | Validación biométrica + manual | Manos libres en plantas de producción con contingencia tras 3 intentos. | Resiliencia operativa ante fallos de cámara o iluminación. |

---

## 2. Decisiones Canónicas de Estandarización SDD

### Decisión 1: Adopción Mandatoria de Cookies HttpOnly
- **Motivación**: Guardar tokens JWT en el almacenamiento accesible por JavaScript (`localStorage`) expone la sesión ante cualquier vulnerabilidad de Cross-Site Scripting (XSS).
- **Estándar SDD**: Todo servicio de login debe emitir la sesión mediante la cabecera `Set-Cookie` con directivas `HttpOnly; Secure; SameSite=Lax; Path=/`.

### Decisión 2: Validación Temprana con Esquemas Declarativos (Zod)
- **Motivación**: Eliminar llamadas de red innecesarias ante errores tipográficos evidentes (cédulas con caracteres alfabéticos, contraseñas vacías).
- **Estándar SDD**: Esquemas `zod` vinculados al formulario para retroalimentación visual inmediata mientras el usuario escribe.

### Decisión 3: Verificación Previa y Gobernanza de Cuentas Administrativas
- **Motivación**: Las cuentas con privilegios elevados no deben ingresar mediante contraseñas estáticas simples, sino requerir el inicio de sesión federado corporativo (Microsoft 365 Entra ID) con autenticación multifactor (MFA).
- **Estándar SDD**: Endpoint `/api/auth/check-user/` para verificar el tipo de cuenta antes de solicitar credenciales locales.

### Decisión 4: Ergonomía Visual sin Suposición de Dependencias (CSS Puro)
- **Motivación**: La interfaz debe funcionar de forma autónoma en cualquier aplicación, sin requerir frameworks de estilos pesados o dependencias externas.
- **Estándar SDD**: Toda la presentación visual se apoya en el archivo maestro de `variables.css` con variables CSS nativas para soporte transparente de Modo Noche y Modo Día.
