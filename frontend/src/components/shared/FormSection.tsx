import type { ReactNode } from 'react';

interface FormSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function FormSection({ title, description, children }: FormSectionProps) {
  return (
    <div style={{
      backgroundColor: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: '8px',
      padding: '24px',
      marginBottom: '16px',
    }}>
      <div style={{ marginBottom: '16px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text)', margin: 0 }}>{title}</h2>
        {description && <p style={{ fontSize: '14px', color: 'var(--text-muted)', margin: '4px 0 0' }}>{description}</p>}
      </div>
      {children}
    </div>
  );
}
