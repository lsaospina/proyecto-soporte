import type { ReactNode } from 'react';

type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

const variantStyles: Record<BadgeVariant, { color: string; backgroundColor: string; dotColor: string }> = {
  success: { color: '#15803D', backgroundColor: '#DCFCE7', dotColor: '#16A34A' },
  warning: { color: '#B45309', backgroundColor: '#FEF3C7', dotColor: '#D97706' },
  danger: { color: '#B91C1C', backgroundColor: '#FEE2E2', dotColor: '#DC2626' },
  info: { color: '#1D4ED8', backgroundColor: '#DBEAFE', dotColor: '#2563EB' },
  neutral: { color: '#334155', backgroundColor: '#F1F5F9', dotColor: '#64748B' },
};

interface StatusBadgeProps {
  label?: string;
  children?: ReactNode;
  variant: BadgeVariant;
  dot?: boolean;
}

export function StatusBadge({ label, children, variant, dot = true }: StatusBadgeProps) {
  const styles = variantStyles[variant];
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '2px 10px',
        fontSize: '12px',
        fontWeight: 500,
        borderRadius: '9999px',
        color: styles.color,
        backgroundColor: styles.backgroundColor,
        lineHeight: '20px',
      }}
    >
      {dot && (
        <span
          style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: styles.dotColor,
            flexShrink: 0,
          }}
        />
      )}
      {children ?? label}
    </span>
  );
}

export type { BadgeVariant };
