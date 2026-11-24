import type { ReactNode } from 'react';

export type KpiTone = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';

const toneStyles: Record<KpiTone, { fg: string; bg: string }> = {
  primary: { fg: 'var(--primary)', bg: 'var(--primary-light)' },
  success: { fg: 'var(--success-fg)', bg: 'var(--success-bg)' },
  warning: { fg: 'var(--warning-fg)', bg: 'var(--warning-bg)' },
  danger: { fg: 'var(--danger-fg)', bg: 'var(--danger-bg)' },
  info: { fg: 'var(--info-fg)', bg: 'var(--info-bg)' },
  neutral: { fg: 'var(--neutral-fg)', bg: 'var(--neutral-bg)' },
};

interface KpiCardProps {
  label: string;
  value: string;
  hint?: string;
  icon?: ReactNode;
  tone?: KpiTone;
}

export function KpiCard({ label, value, hint, icon, tone = 'primary' }: KpiCardProps) {
  const colors = toneStyles[tone];
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        padding: '16px',
        minHeight: '112px',
        backgroundColor: 'var(--surface-lowest)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-card)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
        <span
          style={{
            fontSize: '11px',
            fontWeight: 600,
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          {label}
        </span>
        {icon && (
          <span
            aria-hidden
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '28px',
              height: '28px',
              borderRadius: 'var(--radius-control)',
              color: colors.fg,
              backgroundColor: colors.bg,
              flexShrink: 0,
            }}
          >
            {icon}
          </span>
        )}
      </div>
      <span
        style={{
          fontSize: value.length > 11 ? '19px' : '26px',
          fontWeight: 700,
          color: 'var(--text)',
          lineHeight: 1.15,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        {value}
      </span>
      {hint && <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{hint}</span>}
    </div>
  );
}
