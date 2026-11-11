import type { ReactNode } from 'react';

interface FormFieldProps {
  label: string;
  htmlFor: string;
  required?: boolean;
  error?: string;
  helpText?: string;
  children: ReactNode;
}

export function FormField({ label, htmlFor, required, error, helpText, children }: FormFieldProps) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <label
        htmlFor={htmlFor}
        style={{
          display: 'block',
          fontSize: '13px',
          fontWeight: 500,
          color: 'var(--text)',
          marginBottom: '6px',
        }}
      >
        {label}{required && <span style={{ color: '#B91C1C', marginLeft: '2px' }}>*</span>}
      </label>
      {children}
      {helpText && !error && (
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: '4px 0 0' }}>{helpText}</p>
      )}
      {error && (
        <p role="alert" style={{ fontSize: '12px', color: '#B91C1C', margin: '4px 0 0' }}>{error}</p>
      )}
    </div>
  );
}
