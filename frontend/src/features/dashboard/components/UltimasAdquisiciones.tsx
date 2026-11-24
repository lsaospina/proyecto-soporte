import { StatusBadge, type BadgeVariant } from '../../../components/shared/StatusBadge';
import type { ActivoBreve, EstadoActivo } from '../types';
import { formatearFecha } from '../../../lib/format';

const VARIANTE: Record<EstadoActivo, BadgeVariant> = {
  DISPONIBLE: 'info',
  ASIGNADO: 'success',
  EN_MANTENIMIENTO: 'warning',
  DADO_DE_BAJA: 'danger',
};

const ETIQUETA: Record<EstadoActivo, string> = {
  DISPONIBLE: 'Disponible',
  ASIGNADO: 'Asignado',
  EN_MANTENIMIENTO: 'En mantenimiento',
  DADO_DE_BAJA: 'Dado de baja',
};

interface UltimasAdquisicionesProps {
  activos: ActivoBreve[];
}

export function UltimasAdquisiciones({ activos }: UltimasAdquisicionesProps) {
  if (activos.length === 0) {
    return <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>Aún no hay activos registrados.</p>;
  }

  return (
    <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', listStyle: 'none', margin: 0, padding: 0 }}>
      {activos.map((activo) => (
        <li key={activo.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text)' }}>{activo.codigo_qr}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {activo.marca} {activo.modelo} · {formatearFecha(activo.fecha_adquisicion)}
            </div>
          </div>
          <StatusBadge variant={VARIANTE[activo.estado]} label={ETIQUETA[activo.estado]} />
        </li>
      ))}
    </ul>
  );
}
