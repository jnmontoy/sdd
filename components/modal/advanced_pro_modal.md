# Suite de Modales Profesionales Avanzados (`ProModal`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este componente eleva la interacción de ventanas modales más allá de simples alertas o popups genéricos. Ofrece tres modalidades de alto rigor empresarial:
1. **Modal de Confirmación con Doble Factor / Contraseña** (Acciones destructivas o autorizaciones de alto impacto).
2. **Modal Multi-Paso (Wizard / Stepper Integrado)** (Procesos guiados complejos sin recargar la página).
3. **Modal de Vista Dividida (Split-Screen / Master-Detail)** (Inspección lateral con previsualización o edición simultánea).

---

## 1. Modal con Doble Verificación de Seguridad (`SecurityConfirmModal`)

Para borrados permanentes, anulaciones de facturas o cambios de privilegios de superusuario, se exige confirmación explícita mediante contraseña o escritura de frase clave.

```text
┌────────────────────────────────────────────────────────┐
│ ⚠️ Confirmación de Seguridad Crítica               [✕] │
├────────────────────────────────────────────────────────┤
│ ¿Está seguro de anular el lote de producción #9482?     │
│ Esta acción es irreversible y notificará a auditoría.  │
│                                                        │
│ Para confirmar, ingrese su contraseña actual:          │
│ [🔒 •••••••••••••••••••••••••••••••••••••••••••••••]   │
├────────────────────────────────────────────────────────┤
│ [Cancelar]                 [🔴 Confirmar y Ejecutar]    │
└────────────────────────────────────────────────────────┘
```

### Contrato de Props TypeScript:
```typescript
export interface SecurityConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (passwordOrToken: string) => Promise<void>;
  title: string;
  description: string;
  confirmType?: 'password' | 'phrase' | 'otp';
  expectedPhrase?: string; // Ej: "CONFIRMAR-BORRADO"
  severity?: 'danger' | 'warning';
  isLoading?: boolean;
}
```

---

## 2. Modal Multi-Paso / Wizard (`WizardModal`)

Permite dividir formularios extensos en pasos secuenciales con validación por etapa.

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [Pasos:  ① Empresa  ───  ② Permisos  ───  ③ Resumen]              [✕] │
├────────────────────────────────────────────────────────────────────────┤
│ [Paso 2: Asignación de Roles y Sedes]                                  │
│ Seleccione las sucursales donde el colaborador tendrá permisos:        │
│ [☑ Sede Principal]  [☐ Planta Norte]  [☑ Bodega Central]              │
├────────────────────────────────────────────────────────────────────────┤
│ [← Anterior]                                 [Cancelar]   [Siguiente →] │
└────────────────────────────────────────────────────────────────────────┘
```

### Estructura de Control de Pasos:
```typescript
export interface WizardStep {
  id: string;
  title: string;
  component: React.ReactNode;
  validate?: () => Promise<boolean> | boolean;
}

export interface WizardModalProps {
  isOpen: boolean;
  onClose: () => void;
  steps: WizardStep[];
  onComplete: (data: any) => Promise<void>;
  title: string;
}
```

---

## 3. Modal de Vista Dividida / Master-Detail (`SplitScreenModal`)

Diseñado para auditorías o comparativas: el panel izquierdo muestra la lista o datos origen, y el derecho muestra el documento, formulario de cotejo o previsualización.

```css
.split-modal-container {
  display: grid;
  grid-template-columns: 380px 1fr;
  min-height: 520px;
  max-height: 80vh;
  overflow: hidden;
}

.split-modal-sidebar {
  border-right: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.08));
  padding: 20px;
  background-color: var(--color-bg-surface-elevated, #1a2234);
  overflow-y: auto;
}

.split-modal-content {
  padding: 24px;
  background-color: var(--color-bg-surface, #0f172a);
  overflow-y: auto;
}
```

---

## 4. Estándar de Comportamiento y Accesibilidad (A11y)

1. **Backdrop Blur y Esc**: Desenfoque de fondo (`backdrop-filter: blur(6px)`) con cierre opcional mediante la tecla `Escape`.
2. **Focus Trap**: El foco del teclado se mantiene confinado dentro de la ventana activa mediante `tabindex` y listeners de navegación.
3. **Bloqueo de Scroll en `body`**: Al abrir el modal, se fija `overflow: hidden` en el documento raíz para evitar desplazamientos involuntarios.
4. **Cero `window.alert()` / `window.confirm()`**: Quedan terminantemente prohibidas las alertas nativas del navegador.
