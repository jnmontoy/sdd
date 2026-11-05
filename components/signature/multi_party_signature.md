# Firma Electrónica con Varios Firmantes (`MultiPartySignature`)
## SDD Joli Foods — Spec-Driven Development

Extiende la captura de trazo de [`SignatureModal`](./signature_modal.md) a un **flujo de firma con varios firmantes** para actas de entrega, acuerdos de confidencialidad, inspecciones y aprobaciones por roles, con evidencia que permita demostrar quién firmó, qué documento y cuándo.

> **Marco legal (Colombia):** una firma dibujada más su evidencia es una **firma electrónica** (Ley 527 de 1999, Decreto 2364 de 2012). Una **firma digital** exige un certificado emitido por una entidad de certificación acreditada (ONAC); este componente NO la produce. Si un documento exige firma digital certificada, se integra un proveedor certificado. El área jurídica DEBERÍA validar qué documentos pueden firmarse con este mecanismo.

---

## 1. Características

1. **Varios firmantes, en orden o en paralelo**: ej. quien entrega, transportista y supervisor de calidad. Cada firmante se identifica en la sesión (usuario autenticado) o con un mecanismo verificable (código enviado al correo o celular registrado).
2. **Evidencia generada en el servidor (DEBE)**: todo lo que da valor probatorio lo calcula y guarda el **backend**, no el navegador (el cliente puede ser manipulado):
   - hash SHA-256 del documento antes de firmar y del documento final;
   - marca de tiempo del servidor (ISO-8601, UTC);
   - dirección IP y User-Agent (el navegador no conoce su IP pública: la registra el servidor);
   - identidad del firmante según la sesión;
   - registro de auditoría inmutable (solo inserción).
3. **Geolocalización opcional**: solo con consentimiento explícito del firmante y si la finalidad lo justifica (es dato personal).
4. **Sello visual**: el PDF final DEBERÍA mostrar junto a cada firma el nombre, la fecha y el hash abreviado del documento. El número de documento de identidad DEBERÍA mostrarse enmascarado (ej. `****0001`).

---

## 2. Contrato de datos

```typescript
export type SignerRole = 'solicitante' | 'aprobador' | 'auditor' | 'receptor';

export interface SignerMetadata {
  signerName: string;
  documentId: string; // cédula o ID corporativo; usar valores ficticios en ejemplos (ej. 1000000001)
  signerRole: SignerRole;
  email?: string;
}

/** Lo que el navegador envía: solo el trazo y a qué documento/firmante corresponde. */
export interface SignatureSubmission {
  documentId: string;
  signerRole: SignerRole;
  signatureBase64Png: string;     // salida de cropToSignature
  clientDocumentSha256: string;   // hash que vio el cliente; el servidor lo compara con el suyo
  geoLocation?: { latitude: number; longitude: number; accuracyMeters: number }; // solo con consentimiento
}

/** Lo que el servidor devuelve como evidencia (calculado y almacenado en backend). */
export interface SignatureProof {
  signer: SignerMetadata;
  signedAtIso: string;            // hora del servidor
  documentSha256: string;         // calculado por el servidor
  signatureSha256: string;        // SHA-256(trazo + signedAtIso + documentSha256), calculado por el servidor
  ipAddress: string;              // registrada por el servidor
  userAgent: string;
}

export interface MultiPartySignatureProps {
  documentId: string;
  documentSha256: string;         // hash publicado por el backend para el documento a firmar
  requiredSigners: SignerMetadata[];
  onAllSigned: (proofs: SignatureProof[]) => void;
  enableGeoLocation?: boolean;
}
```

El hash en el cliente sirve solo para comprobar que la persona vio el mismo documento que el servidor; se calcula con `sha256Hex` (ver [`upload/file_uploader_pro.md`](../upload/file_uploader_pro.md)).

---

## 3. Sello visual en un lienzo

Cuando se necesite una vista previa del sello en el navegador (el sello definitivo lo estampa el backend en el PDF):

```typescript
/** Agrega una franja con el sello bajo la firma y devuelve un PNG nuevo. */
export function addSignatureStamp(
  signaturePng: HTMLCanvasElement,
  signer: Pick<SignerMetadata, 'signerName' | 'documentId'>,
  documentSha256: string,
  signedAtIso: string
): string {
  const STAMP_HEIGHT = 18;
  const masked = `****${signer.documentId.slice(-4)}`;
  const text = `Firmado por: ${signer.signerName} (${masked}) | DOC: ${documentSha256.slice(0, 16)} | ${signedAtIso}`;

  const out = document.createElement('canvas');
  const ctx = out.getContext('2d');
  if (!ctx) return signaturePng.toDataURL('image/png');

  ctx.font = '10px monospace';
  out.width = Math.max(signaturePng.width, Math.ceil(ctx.measureText(text).width) + 16);
  out.height = signaturePng.height + STAMP_HEIGHT;

  // Al cambiar el tamaño se reinicia el contexto: se vuelve a fijar la fuente.
  ctx.drawImage(signaturePng, 0, 0);
  ctx.font = '10px monospace';
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--ink-signature').trim() || '#0f172a';
  ctx.textAlign = 'left';
  ctx.fillText(text, 8, out.height - 5);
  return out.toDataURL('image/png');
}
```

---

## 4. Estilos

```css
.signature-card-box {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.signature-canvas-wrapper {
  position: relative;
  border: 2px dashed var(--border-strong);
  border-radius: var(--radius-md);
  background: var(--surface-paper);
  touch-action: none; /* evita que la página se desplace al firmar con el dedo o lápiz */
}

.signature-signers-progress {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
}

.signer-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  color: var(--text-secondary);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
}

.signer-chip--completed {
  background: var(--status-success-bg);
  color: var(--text-primary);
  border-color: var(--status-success);
}
```
