import { AlertTriangle, CalendarClock, CheckCircle2, Info } from 'lucide-react';

import type { MantenimientosResumen } from '../types';

interface Alerta {
  tone: 'danger' | 'warning' | 'info' | 'success';
  titulo: string;
  detalle: string;
}

const ESTILOS = {
  danger: { color: 'var(--danger-fg)', bg: 'var(--danger-bg)' },
  warning: { color: 'var(--warning-fg)', bg: 'var(--warning-bg)' },
  info: { color: 'var(--info-fg)', bg: 'var(--info-bg)' },
  success: { color: 'var(--success-fg)', bg: 'var(--success-bg)' },
} as const;

function icono(tone: Alerta['tone']) {
  if (tone === 'danger') return <AlertTriangle size={16} aria-hidden />;
  if (tone === 'warning') return <CalendarClock size={16} aria-hidden />;
  if (tone === 'info') return <Info size={16} aria-hidden />;
  return <CheckCircle2 size={16} aria-hidden />;
}

function construirAlertas(mantenimientos: MantenimientosResumen, anio: number): Alerta[] {
  const { preventivos_anio: preventivos, activos_sin_preventivo: sinPreventivo, proximos } = mantenimientos;
  const alertas: Alerta[] = [];

  if (preventivos.vencidos > 0) {
    alertas.push({
      tone: 'danger',
      titulo: `${preventivos.vencidos} mantenimiento${preventivos.vencidos === 1 ? '' : 's'} preventivo${preventivos.vencidos === 1 ? '' : 's'} vencido${preventivos.vencidos === 1 ? '' : 's'}`,
      detalle: 'Reprograma o completa estos servicios para recuperar el cumplimiento del año.',
    });
  }
  if (preventivos.incumplidos > 0) {
    alertas.push({
      tone: 'warning',
      titulo: `${preventivos.incumplidos} servicio${preventivos.incumplidos === 1 ? '' : 's'} incumplido${preventivos.incumplidos === 1 ? '' : 's'}`,
      detalle: 'Quedaron registrados como evidencia y no cuentan como completados.',
    });
  }
  const proximosSemana = proximos.filter((item) => (item.dias_restantes ?? 99) <= 7).length;
  if (proximosSemana > 0) {
    alertas.push({
      tone: 'info',
      titulo: `${proximosSemana} servicio${proximosSemana === 1 ? '' : 's'} en los próximos 7 días`,
      detalle: 'Revisa la agenda para asegurar técnico y repuestos.',
    });
  }
  if (sinPreventivo.total > 0) {
    alertas.push({
      tone: 'warning',
      titulo: `${sinPreventivo.total} activo${sinPreventivo.total === 1 ? '' : 's'} sin preventivo en ${anio}`,
      detalle: 'Programa su mantenimiento para evitar equipos sin cobertura anual.',
    });
  }

  if (alertas.length === 0) {
    alertas.push({
      tone: 'success',
      titulo: 'Sin alertas críticas',
      detalle: 'No hay mantenimientos vencidos ni incumplidos pendientes de atender.',
    });
  }

  return alertas;
}

interface AlertasTableroProps {
  mantenimientos: MantenimientosResumen;
  anio: number;
}

export function AlertasTablero({ mantenimientos, anio }: AlertasTableroProps) {
  const alertas = construirAlertas(mantenimientos, anio);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
      {alertas.map((alerta, index) => (
        <div
          key={`${alerta.tone}-${index}`}
          role={alerta.tone === 'danger' ? 'alert' : 'status'}
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px',
            padding: '10px 14px',
            borderRadius: 'var(--radius-card)',
            backgroundColor: ESTILOS[alerta.tone].bg,
            color: ESTILOS[alerta.tone].color,
          }}
        >
          <span style={{ marginTop: '1px', flexShrink: 0 }}>{icono(alerta.tone)}</span>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600 }}>{alerta.titulo}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{alerta.detalle}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
