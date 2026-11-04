# Suite de Modales Profesionales Avanzados (`ProModal`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este documento describe tres variantes de modal para casos que `ConfirmModal` no cubre. Todas reutilizan `useModalA11y` de [`modal_dialog.md`](./modal_dialog.md) §2 para foco, Escape y bloqueo de scroll:
1. **Modal de Confirmación con Doble Factor / Contraseña** (Acciones destructivas o autorizaciones de alto impacto).
2. **Modal Multi-Paso (Wizard)** (procesos guiados que no son creación/edición CRUD; para CRUD extenso se usa el drawer con [`stepper_wizard.md`](../stepper/stepper_wizard.md)).
3. **Modal de Vista Dividida (Master-Detail)** (inspección o cotejo de solo lectura con previsualización).

---

## 1. Modal con Doble Verificación de Seguridad (`SecurityConfirmModal`)

Para borrados permanentes, anulaciones de documentos o cambios de privilegios de superusuario, se pide confirmación explícita con contraseña, frase clave u OTP.

- **Regla:** la verificación (contraseña/OTP) DEBE validarla el backend en el mismo endpoint de la acción (o con un token de reautenticación de vida corta); el frontend NO DEBE comparar contraseñas ni guardarlas en estado más allá del envío.
- **Por qué:** una verificación solo en cliente se omite llamando directamente a la API.
- La frase clave (`expectedPhrase`) sí PUEDE validarse en el cliente: es una barrera contra clics accidentales, no un control de seguridad.

```text
┌────────────────────────────────────────────────────────┐
│ ⚠️ Confirmación de Seguridad Crítica               [✕] │
├────────────────────────────────────────────────────────┤
│ ¿Está seguro de anular el lote de producción #0001?     │
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
  onComplete: (data: Record<string, unknown>) => Promise<void>;
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
  border-right: 1px solid var(--border-subtle);
  padding: 20px;
  background-color: var(--bg-elevated);
  overflow-y: auto;
}

.split-modal-content {
  padding: 24px;
  background-color: var(--bg-card);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .split-modal-container { grid-template-columns: 1fr; }
  .split-modal-sidebar { border-right: none; border-bottom: 1px solid var(--border-subtle); }
}
```

---

## 4. Estándar de Comportamiento y Accesibilidad (A11y)

1. **Rol y nombre:** `role="dialog"` (o `alertdialog` en `SecurityConfirmModal`), `aria-modal="true"` y `aria-labelledby` apuntando al título.
2. **Escape:** cierra el modal salvo mientras `isLoading` sea verdadero; en el wizard, si hay datos capturados, DEBERÍA pedir confirmación antes de descartarlos.
3. **Foco:** atrapado dentro del modal y devuelto al disparador al cerrar (`useModalA11y`). En el wizard, al cambiar de paso el foco va al título del paso.
4. **Bloqueo de scroll** del `body` mientras está abierto.
5. **Sin diálogos nativos:** NO DEBEN usarse `window.alert()` / `window.confirm()` (ver [`confirm_modal.md`](./confirm_modal.md)).
