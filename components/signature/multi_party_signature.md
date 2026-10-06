# Suite Avanzada de Firmas y Consentimiento Multi-Firmante (`MultiPartySignature`)
## Componente UI Canónico — Spec-Driven Development (SDD)

Este componente extiende la captura básica de trazos sobre Canvas a un **protocolo completo de firma digital corporativa**, diseñado para actas de entrega, acuerdos de confidencialidad, inspecciones de contenedores y aprobaciones jerárquicas multi-rol.

---

## 1. Características Técnicas Obligatorias

1. **Multi-Firmante Secuencial o Paralelo**: Soporta flujo para múltiples involucrados (ej. Operador de Entrega, Transportista, Supervisor de Calidad).
2. **Metadatos Criptográficos y de Auditoría Inmutables**:
   - Marca temporal ISO-8601 de precisión (`timestamp`).
   - Hash SHA-256 del contenido del documento antes y después de firmar.
   - Registro de IP pública, User-Agent del dispositivo y coordenadas de geolocalización (GPS con consentimiento del usuario).
3. **Sello de Agua y Certificación Visual**: Renderizado sobre Canvas del trazo limpio (`cropToSignature`) incrustando sello con fecha, documento de identidad del firmante y hash abreviado.

---

## 2. Contrato de Datos de Firma (`SignatureRecord`)

```typescript
export interface SignerMetadata {
  signerName: string;
  documentId: string; // Cédula o ID Corporativo
  signerRole: 'solicitante' | 'aprobador' | 'auditor' | 'receptor';
  email?: string;
  geoLocation?: {
    latitude: number;
    longitude: number;
    accuracyMeters: number;
  };
}

export interface SignatureProof {
  signatureBase64Png: string; // Trazo recortado en fondo transparente
  signedAtIso: string;
  signer: SignerMetadata;
  documentSha256: string;
  signatureTokenHash: string; // SHA-256(trazo + timestamp + documentSha256)
  ipAddress?: string;
}

export interface MultiPartySignatureProps {
  documentId: string;
  documentHash: string; // Hash SHA-256 del documento a firmar
  requiredSigners: SignerMetadata[];
  onAllSigned: (proofs: SignatureProof[]) => Promise<void>;
  enableGeoLocation?: boolean;
}
```

---

## 3. Algoritmo de Generación de Sello Digital Integrado (Canvas)

```javascript
/**
 * Incrusta el sello criptográfico en el pie del trazo firmado.
 */
export function embedSecurityWatermark(canvas, signer, documentHash) {
  const ctx = canvas.getContext('2d');
  const now = new Date().toISOString();
  const shortHash = documentHash.substring(0, 16);

  ctx.save();
  ctx.font = '10px monospace';
  ctx.fillStyle = '#64748b';
  ctx.textAlign = 'right';

  const footerText = `Firmado por: ${signer.signerName} (${signer.documentId}) | DOC: ${shortHash} | ${now}`;
  ctx.fillText(footerText, canvas.width - 12, canvas.height - 8);
  ctx.restore();

  return canvas.toDataURL('image/png');
}
```

---

## 4. Estilos y Layout Responsivo

```css
.signature-card-box {
  background: var(--color-bg-surface, #1e293b);
  border: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.08));
  border-radius: 12px;
  padding: 20px;
}

.signature-canvas-wrapper {
  position: relative;
  border: 2px dashed var(--color-border-hover, rgba(16, 185, 129, 0.4));
  border-radius: 8px;
  background: #0f172a;
  touch-action: none; /* Crucial para evitar scroll al firmar con dedo o stylus */
}

.signature-signers-progress {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.signer-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  background: var(--color-bg-surface-elevated, #334155);
}

.signer-chip--completed {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-primary, #10b981);
  border: 1px solid var(--color-primary, #10b981);
}
```
