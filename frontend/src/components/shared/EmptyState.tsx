import type { ReactNode } from 'react';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 24px',
      backgroundColor: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: '8px',
      textAlign: 'center',
    }}>
      {icon && <div style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>{icon}</div>}
      <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text)', margin: '0 0 8px' }}>{title}</h3>
      {description && <p style={{ fontSize: '14px', color: 'var(--text-muted)', margin: '0 0 16px', maxWidth: '400px' }}>{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
}
