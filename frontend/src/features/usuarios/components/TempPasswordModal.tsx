import { useState } from 'react';
import { Copy, Check, AlertTriangle } from 'lucide-react';

interface TempPasswordModalProps {
  open: boolean;
  password: string | null;
  title?: string;
  onClose: () => void;
}

export function TempPasswordModal({
  open,
  password,
  title = 'Contraseña temporal generada',
  onClose,
}: TempPasswordModalProps) {
  const [copied, setCopied] = useState(false);

  if (!open || !password) return null;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={title}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
      }}
    >
      <div style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(15, 23, 42, 0.45)' }} />
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: '480px',
          backgroundColor: 'var(--surface-lowest)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <h3 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text)', margin: '0 0 8px' }}>
          {title}
        </h3>
        <div
          style={{
            display: 'flex',
            gap: '10px',
            alignItems: 'flex-start',
            backgroundColor: 'var(--warning-bg)',
            border: '1px solid #FDE68A',
            borderRadius: '6px',
            padding: '10px 12px',
            marginBottom: '16px',
          }}
        >
          <AlertTriangle size={18} style={{ color: 'var(--warning-fg)', flexShrink: 0, marginTop: '1px' }} />
          <p style={{ fontSize: '13px', color: 'var(--warning-fg)', margin: 0 }}>
            Esta contraseña se muestra una sola vez. Cópiela y entréguela al usuario por un canal seguro.
          </p>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
            padding: '12px',
            backgroundColor: 'var(--surface-low)',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            marginBottom: '16px',
          }}
        >
          <code style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text)', wordBreak: 'break-all' }}>
            {password}
          </code>
          <button
            type="button"
            onClick={handleCopy}
            aria-label="Copiar contraseña temporal"
            style={{
              background: 'none',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              padding: '6px 10px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              color: copied ? 'var(--success-fg)' : 'var(--text)',
              cursor: 'pointer',
              flexShrink: 0,
              fontSize: '13px',
            }}
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copiada' : 'Copiar'}
          </button>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: 'var(--primary)',
              color: '#FFFFFF',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Ya la guardé, continuar
          </button>
        </div>
      </div>
    </div>
  );
}
