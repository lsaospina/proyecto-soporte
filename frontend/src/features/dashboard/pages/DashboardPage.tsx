import { LayoutDashboard, Monitor, Wrench, ShieldCheck, AlertTriangle } from 'lucide-react';
import { PageHeader } from '../../../components/shared/PageHeader';

function KpiPlaceholder({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  return (
    <div style={{
      backgroundColor: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: '8px',
      padding: '20px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      flex: '1 1 200px',
    }}>
      <div style={{
        width: '48px',
        height: '48px',
        borderRadius: '8px',
        backgroundColor: color,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        {icon}
      </div>
      <div>
        <div style={{ fontSize: '24px', fontWeight: 600, color: 'var(--text)' }}>{value}</div>
        <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{label}</div>
      </div>
    </div>
  );
}

export function DashboardPage() {
  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Resumen general del sistema"
      />
      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '24px' }}>
        <KpiPlaceholder
          icon={<Monitor size={24} color="#FFFFFF" />}
          label="Activos registrados"
          value="—"
          color="var(--primary)"
        />
        <KpiPlaceholder
          icon={<ShieldCheck size={24} color="#FFFFFF" />}
          label="Operativos"
          value="—"
          color="#15803D"
        />
        <KpiPlaceholder
          icon={<Wrench size={24} color="#FFFFFF" />}
          label="En mantenimiento"
          value="—"
          color="#B45309"
        />
        <KpiPlaceholder
          icon={<AlertTriangle size={24} color="#FFFFFF" />}
          label="Alertas activas"
          value="—"
          color="#B91C1C"
        />
      </div>
      <div style={{
        backgroundColor: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        padding: '40px',
        textAlign: 'center',
        color: 'var(--text-muted)',
      }}>
        <LayoutDashboard size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
        <p style={{ fontSize: '16px', fontWeight: 500, margin: '0 0 8px' }}>Dashboard en construcción</p>
        <p style={{ fontSize: '14px', margin: 0 }}>Los gráficos y métricas estarán disponibles cuando se registren activos en el sistema.</p>
      </div>
    </div>
  );
}
