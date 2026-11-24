import type { ReactNode } from 'react';

interface SeccionPanelProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
}

export function SeccionPanel({ title, subtitle, action, children }: SeccionPanelProps) {
  return (
    <section
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        padding: '20px',
        backgroundColor: 'var(--surface-lowest)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-card)',
        boxShadow: 'var(--shadow-sm)',
        minWidth: 0,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text)', margin: 0 }}>{title}</h2>
          {subtitle && (
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: '4px 0 0' }}>{subtitle}</p>
          )}
        </div>
        {action && <div style={{ flexShrink: 0 }}>{action}</div>}
      </div>
      <div style={{ minWidth: 0 }}>{children}</div>
    </section>
  );
}
