import type { KpiTone } from '../../../components/shared/KpiCard';

const colores: Record<KpiTone, string> = {
  primary: 'var(--primary)',
  success: 'var(--success-fg)',
  warning: 'var(--warning-fg)',
  danger: 'var(--danger-fg)',
  info: 'var(--info-fg)',
  neutral: 'var(--neutral-fg)',
};

export interface BarraItem {
  label: string;
  value: number;
  tone?: KpiTone;
}

interface BarrasHorizontalesProps {
  items: BarraItem[];
  vacio?: string;
}

export function BarrasHorizontales({ items, vacio = 'Sin datos para mostrar.' }: BarrasHorizontalesProps) {
  if (items.length === 0) {
    return <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>{vacio}</p>;
  }
  const maximo = Math.max(...items.map((item) => item.value), 1);

  return (
    <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', listStyle: 'none', margin: 0, padding: 0 }}>
      {items.map((item) => {
        const ancho = item.value > 0 ? Math.max((item.value / maximo) * 100, 4) : 0;
        return (
          <li key={item.label} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: '8px' }}>
              <span style={{ fontSize: '13px', color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {item.label}
              </span>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text)' }}>{item.value}</span>
            </div>
            <div
              style={{
                height: '6px',
                borderRadius: '9999px',
                backgroundColor: 'var(--surface-high)',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${ancho}%`,
                  height: '100%',
                  borderRadius: '9999px',
                  backgroundColor: colores[item.tone ?? 'primary'],
                  transition: 'width var(--transition-fast)',
                }}
              />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
