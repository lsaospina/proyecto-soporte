import { useState } from 'react';
import { Copy, Check, AlertTriangle } from 'lucide-react';

interface RecoveryCodesDisplayProps {
  codes: string[];
  onContinue: () => void;
}

export function RecoveryCodesDisplay({ codes, onContinue }: RecoveryCodesDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyAll = async () => {
    await navigator.clipboard.writeText(codes.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text)', margin: '0 0 8px' }}>
          Códigos de recuperación
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
          Guarde estos códigos en un lugar seguro. Cada código solo puede usarse una vez.
        </p>
      </div>

      {/* Warning */}
      <div
        style={{
          backgroundColor: 'var(--warning-bg)',
          border: '1px solid #FDE68A',
          borderRadius: 'var(--radius-control)',
          padding: '12px 16px',
          marginBottom: '16px',
          display: 'flex',
          gap: '10px',
          alignItems: 'flex-start',
        }}
      >
        <AlertTriangle size={18} style={{ color: 'var(--warning-fg)', flexShrink: 0, marginTop: '1px' }} />
        <p style={{ fontSize: '13px', color: 'var(--warning-fg)', margin: 0 }}>
          Estos códigos solo se muestran una vez. Si pierde acceso a su aplicación de autenticación,
          necesitará uno de estos códigos para ingresar al sistema.
        </p>
      </div>

      {/* Codes grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '8px',
          padding: '16px',
          backgroundColor: 'var(--neutral-bg)',
          borderRadius: 'var(--radius-card)',
          marginBottom: '16px',
        }}
      >
        {codes.map((code, index) => (
          <div
            key={index}
            style={{
              fontFamily: 'monospace',
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--text)',
              padding: '6px 10px',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius-control)',
              textAlign: 'center',
              border: '1px solid var(--border)',
            }}
          >
            {code}
          </div>
        ))}
      </div>

      {/* Copy button */}
      <button
        onClick={handleCopyAll}
        style={{
          width: '100%',
          padding: '10px',
          backgroundColor: 'var(--surface)',
          color: 'var(--text)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-control)',
          fontSize: '13px',
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          marginBottom: '12px',
        }}
      >
        {copied ? <Check size={16} color="var(--success-fg)" /> : <Copy size={16} />}
        {copied ? 'Copiados' : 'Copiar todos los códigos'}
      </button>

      {/* Continue */}
      <button
        onClick={onContinue}
        style={{
          width: '100%',
          padding: '12px',
          backgroundColor: 'var(--primary)',
          color: '#FFFFFF',
          border: 'none',
          borderRadius: 'var(--radius-control)',
          fontSize: '14px',
          fontWeight: 600,
        }}
      >
        Ya guardé mis códigos, continuar
      </button>
    </div>
  );
}
