import {
  Monitor,
  Wrench,
  ShieldCheck,
  AlertTriangle,
  Timer,
  Badge,
  Download,
  Plus,
} from 'lucide-react';
import { PageHeader } from '../../../components/shared/PageHeader';

function KpiCard({
  label,
  value,
  icon,
  iconColor,
  trendLabel,
  trendValue,
  trendColor,
  sparklinePoints,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
  iconColor: string;
  trendLabel: string;
  trendValue: string;
  trendColor: string;
  sparklinePoints: string;
}) {
  return (
    <div
      style={{
        backgroundColor: 'var(--surface-lowest)',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        padding: '16px',
        minHeight: '120px',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</span>
        <span style={{ color: iconColor }}>{icon}</span>
      </div>
      <span style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text)', lineHeight: 1 }}>{value}</span>
      <svg
        className="w-full h-full stroke-current fill-none stroke-2"
        preserveAspectRatio="none"
        viewBox="0 0 100 24"
        style={{ width: '100%', height: '20px', marginTop: '8px', color: iconColor }}
      >
        <polyline points={sparklinePoints} />
      </svg>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px' }}>
        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: trendColor, display: 'inline-block' }} />
        <span style={{ fontSize: '11px', fontWeight: 600, color: trendColor }}>{trendValue}</span>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{trendLabel}</span>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const sparklineDefault = '0,18 15,16 30,19 45,13 60,11 75,9 90,6 100,4';
  const sparklineUp = '0,12 18,10 35,11 50,8 70,7 85,5 100,4';
  const sparklineFluctuate = '0,6 20,8 40,14 60,12 80,18 100,16';
  const sparklineDown = '0,20 18,17 38,15 54,8 72,11 88,6 100,5';
  const sparklineMid = '0,15 20,13 40,16 60,11 80,7 100,5';
  const sparklineFlat = '0,12 25,12 50,15 75,8 100,7';

  return (
    <div style={{ backgroundColor: 'var(--background)', minHeight: '100vh' }}>
      <PageHeader
        title="Centro de Comando de TI — Visión General"
        subtitle="Monitoreo holístico de inventario tecnológico, ciclo de vida de garantías, licenciamiento de software y continuidad operativa de servicios."
        actions={
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              type="button"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                backgroundColor: 'var(--surface-lowest)',
                border: '1px solid var(--border)',
                borderRadius: '6px',
                color: 'var(--text)',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              <Download size={14} color="currentColor" />
              <span>Exportar Resumen KPI</span>
            </button>
            <button
              type="button"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                backgroundColor: 'var(--primary)',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <Plus size={14} color="#FFFFFF" />
              <span>+ Registrar Activo</span>
            </button>
          </div>
        }
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <KpiCard label="Total de Activos" value="2,845" icon={<Monitor size={18} />} iconColor="var(--primary)" trendLabel="este mes" trendValue="+4.2%" trendColor="var(--success-fg)" sparklinePoints={sparklineDefault} />
        <KpiCard label="Equipos Operativos" value="2,510" icon={<ShieldCheck size={18} />} iconColor="var(--success-fg)" trendLabel="disponibilidad" trendValue="88.2%" trendColor="var(--success-fg)" sparklinePoints={sparklineUp} />
        <KpiCard label="En Mantenimiento" value="142" icon={<Wrench size={18} />} iconColor="var(--warning-fg)" trendLabel="9 taller · 133 interno" trendValue="" trendColor="var(--warning-fg)" sparklinePoints={sparklineFluctuate} />
        <KpiCard label="Incidentes Abiertos" value="28" icon={<AlertTriangle size={18} />} iconColor="var(--danger-fg)" trendLabel="9 Altos · 15 Medios" trendValue="SLA Activo" trendColor="var(--danger-fg)" sparklinePoints={sparklineDown} />
        <KpiCard label="Garantías por Vencer" value="34" icon={<Timer size={18} />} iconColor="var(--info-fg)" trendLabel="Próximos 60 días" trendValue="12 OEM Pro" trendColor="var(--info-fg)" sparklinePoints={sparklineMid} />
        <KpiCard label="Licencias por Vencer" value="19" icon={<Badge size={18} />} iconColor="var(--primary)" trendLabel="Revisión presupuestal" trendValue="Q3/Q4" trendColor="var(--primary)" sparklinePoints={sparklineFlat} />
      </div>

      <div style={{ backgroundColor: 'var(--surface-lowest)', border: '1px solid var(--border)', borderRadius: '8px', padding: '20px', boxShadow: 'var(--shadow-sm)' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text)', marginBottom: '16px' }}>Estado del Sistema</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
          Los datos de métricas y gráficos se poblarán cuando se implementen los módulos de activos y mantenimientos (T-003 a T-007).
        </p>
      </div>
    </div>
  );
}
