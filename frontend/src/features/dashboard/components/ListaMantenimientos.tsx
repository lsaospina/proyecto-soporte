import type { MantenimientoBreve } from '../types';
import { diaYMes } from '../../../lib/format';

type Variante = 'proximo' | 'vencido' | 'correctivo';

interface ListaMantenimientosProps {
  items: MantenimientoBreve[];
  variante: Variante;
  vacio: string;
}

function detalleDerecha(item: MantenimientoBreve, variante: Variante): { texto: string; color: string } | null {
  if (variante === 'proximo') {
    const dias = item.dias_restantes ?? 0;
    return { texto: dias === 0 ? 'Hoy' : `En ${dias} día${dias === 1 ? '' : 's'}`, color: 'var(--info-fg)' };
  }
  if (variante === 'vencido') {
    const dias = item.dias_atraso ?? 0;
    return { texto: `${dias} día${dias === 1 ? '' : 's'}`, color: 'var(--danger-fg)' };
  }
  return null;
}

export function ListaMantenimientos({ items, variante, vacio }: ListaMantenimientosProps) {
  if (items.length === 0) {
    return <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>{vacio}</p>;
  }

  return (
    <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', listStyle: 'none', margin: 0, padding: 0 }}>
      {items.map((item) => {
        const { dia, mes } = diaYMes(item.fecha_programada);
        const derecha = detalleDerecha(item, variante);
        const secundario =
          variante === 'correctivo'
            ? item.observacion || 'Sin detalle'
            : item.tecnico ?? 'Sin técnico asignado';

        return (
          <li key={item.id} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              aria-hidden
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                width: '42px',
                height: '42px',
                flexShrink: 0,
                borderRadius: 'var(--radius-control)',
                backgroundColor:
                  variante === 'vencido' ? 'var(--danger-bg)' : variante === 'proximo' ? 'var(--info-bg)' : 'var(--neutral-bg)',
                color:
                  variante === 'vencido' ? 'var(--danger-fg)' : variante === 'proximo' ? 'var(--info-fg)' : 'var(--neutral-fg)',
              }}
            >
              <span style={{ fontSize: '15px', fontWeight: 700, lineHeight: 1 }}>{dia}</span>
              <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{mes}</span>
            </div>

            <div style={{ minWidth: 0, flex: 1 }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text)' }}>{item.activo_codigo}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {item.marca} {item.modelo} · {secundario}
              </div>
            </div>

            {derecha && (
              <span style={{ fontSize: '12px', fontWeight: 600, color: derecha.color, whiteSpace: 'nowrap' }}>
                {derecha.texto}
              </span>
            )}
          </li>
        );
      })}
    </ul>
  );
}
