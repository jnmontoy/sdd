# 07. Plan de Pruebas y Matriz de Aseguramiento de Calidad (QA)
## Módulo de Login / Autenticación — SDD Greenyard (`GY-SPEC-AUTH-001`)

Este documento define la estrategia exhaustiva de aseguramiento de calidad (QA) y la batería de pruebas automatizadas requerida para certificar cualquier implementación del módulo de Login.

---

## 1. Pirámide de Pruebas del Módulo

```
           /\
          /  \         E2E (Playwright / Cypress) - 10%
         /----\        Flujo completo de login, SSO y persistencia
        /      \       
       / Integr \      Integración API (Django Test Client / Supertest) - 30%
      /----------\     Endpoints, Códigos HTTP, Cookies HttpOnly, DB
     /            \    
    /   Unitarias  \   Pruebas Unitarias (Vitest / Pytest) - 60%
   /----------------\  Validación Zod, Hashers, Máquina de estados
```

---

## 2. Matriz de Casos de Prueba de Integración Backend

| ID Caso | Nombre de la Prueba | Entrada (Payload) | Condición Previa | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| **TC-BE-01** | Login Exitoso con Credenciales | `{"documento": "1037645123", "password": "PassCorrecta!2026"}` | Usuario activo en DB con hash correspondiente | HTTP 200 OK, Set-Cookie con directivas `HttpOnly; Secure; SameSite=Lax`, body con datos del usuario sin contraseñas. |
| **TC-BE-02** | Contraseña Incorrecta | `{"documento": "1037645123", "password": "PasswordErrada"}` | Usuario existe en DB | HTTP 401 Unauthorized, mensaje `"Credenciales inválidas"`, incremento en contador de intentos fallidos. |
| **TC-BE-03** | Documento Inexistente | `{"documento": "9999999999", "password": "CualquierPass"}` | Documento no existe en DB | HTTP 401 Unauthorized, mensaje idéntico al anterior (para evitar enumeración de usuarios). |
| **TC-BE-04** | Usuario Inactivo | `{"documento": "1010101010", "password": "PassCorrecta!2026"}` | Usuario con `is_active = False` | HTTP 403 Forbidden, código `"USER_INACTIVE"`. |
| **TC-BE-05** | Activación de Rate Limit | 5 peticiones erróneas consecutivas en menos de 60 segundos | Misma IP de origen | La 6ta petición retorna HTTP 429 Too Many Requests con cabecera `Retry-After: 900`. |
| **TC-BE-06** | Sanitización contra Inyección SQL | `{"documento": "1037645' OR '1'='1", "password": "test"}` | Cualquiera | HTTP 400 Bad Request por fallo en validación de regex `^[0-9]+$`. |
| **TC-BE-07** | Verificación de Atributos de Cookie | Petición POST exitosa | Servidor en modo producción | Header `Set-Cookie` verificado: `HttpOnly=True`, `Secure=True`, `SameSite=Lax`. |
| **TC-BE-08** | Cierre de Sesión (Logout) | Petición POST a `/api/auth/logout/` con cookie válida | Sesión activa | HTTP 200 OK, `Set-Cookie` con `Max-Age=0` y token invalidado en lista negra. |

---

## 3. Matriz de Casos de Prueba de Frontend (Unitarias & E2E)

| ID Caso | Componente | Descripción de la Prueba | Criterio de Aprobación |
| :--- | :--- | :--- | :--- |
| **TC-FE-01** | `loginSchema` (Zod) | Validación de documento numérico de 5 a 15 dígitos. | Rechaza letras, símbolos y longitudes fuera del rango. |
| **TC-FE-02** | `LoginForm` | Prevención de doble envío concurrente. | Al hacer submit, el botón queda deshabilitado (`disabled=true`) y no dispara peticiones duplicadas. |
| **TC-FE-03** | `PasswordToggle` | Alternancia de visibilidad de contraseña. | El input conmuta entre `type="password"` y `type="text"` al hacer clic en el botón de ojo. |
| **TC-FE-04** | `RememberMe` | Persistencia del número de cédula en almacenamiento local. | Si está marcado, guarda el valor al autenticar; si está desmarcado, purga la clave almacenada. |
| **TC-FE-05** | Flujo E2E Completo | Carga de formulario, llenado, envío y redirección a vista protegida. | Verificado en Chromium, Firefox y WebKit con Playwright. |
| **TC-FE-06** | Navegación Accesible | Operación completa del formulario mediante teclado (`Tab`, `Enter`, `Space`). | Foco visual presente en todo momento y submit disparado al pulsar Enter. |

---

## 4. Batería de Pruebas de Seguridad y Pentesting (DAST)

- **Test de Enumeración de Cuentas**: Comprobar que el tiempo de respuesta y el mensaje de error sean estadísticamente indistinguibles cuando el usuario existe vs. cuando no existe.
- **Fuzzing de Caracteres Unicode y Null Bytes**: Inyección de caracteres nulos `%00` y secuencias UTF-8 atípicas en el campo de contraseña y documento para verificar que no causen fallos no controlados (500 Internal Server Error).
- **Inspección de Tráfico y Almacenamiento Local**: Confirmar que en ningún caso el valor de la contraseña ni el token de sesión sensible queden expuestos en `window.localStorage`, `window.sessionStorage` o historial de consola.
