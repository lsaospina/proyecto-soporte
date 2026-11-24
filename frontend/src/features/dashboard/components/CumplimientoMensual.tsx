import type { MesResumen } from '../types';

const MESES_CORTOS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

const SERIES = [
  { key: 'completados', etiqueta: 'Completados', color: 'var(--success-fg)' },
  { key: 'pendientes', etiqueta: 'Pendientes', color: 'var(--info-fg)' },
  { key: 'vencidos', etiqueta: 'Vencidos', color: 'var(--warning-fg)' },
  { key: 'incumplidos', etiqueta: 'Incumplidos', color: 'var(--danger-fg)' },
] as const;

const ALTO_BARRAS = 150;

interface CumplimientoMensualProps {
  meses: MesResumen[];
}

export function CumplimientoMensual({ meses }: CumplimientoMensualProps) {
  const maximo = Math.max(...meses.map((mes) => mes.agendados), 1);
  const hayDatos = meses.some((mes) => mes.agendados > 0);

  const segmentos = (mes: MesResumen) => {
    const pendientes = Math.max(mes.agendados - mes.completados - mes.vencidos - mes.incumplidos, 0);
    return { completados: mes.completados, pendientes, vencidos: mes.vencidos, incumplidos: mes.incumplidos };
  };

  return (
    <figure style={{ margin: 0 }} aria-label="Cumplimiento preventivo por mes">
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${meses.length}, minmax(0, 1fr))`,
          gap: '6px',
          alignItems: 'end',
        }}
      >
        {meses.map((mes) => {
          const valores = segmentos(mes);
          const altoTotal = mes.agendados > 0 ? Math.max((mes.agendados / maximo) * ALTO_BARRAS, 4) : 0;
          const etiqueta = `${MESES_CORTOS[mes.mes - 1]}: ${mes.agendados} agendados, ${mes.completados} completados, ${mes.vencidos} vencidos, ${mes.incumplidos} incumplidos`;
          return (
            <div
              key={mes.mes}
              title={etiqueta}
              aria-label={etiqueta}
              style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'center' }}
            >
              <div style={{ height: `${ALTO_BARRAS}px`, width: '100%', display: 'flex', alignItems: 'flex-end' }}>
                {mes.agendados > 0 ? (
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column-reverse',
                      width: '100%',
                      height: `${altoTotal}px`,
                      borderRadius: '4px 4px 0 0',
                      overflow: 'hidden',
                      backgroundColor: 'var(--surface-high)',
                    }}
                  >
                    {SERIES.map((serie) => {
                      const valor = valores[serie.key];
                      if (valor <= 0) return null;
                      return (
                        <div
                          key={serie.key}
                          style={{
                            height: `${(valor / mes.agendados) * 100}%`,
                            backgroundColor: serie.color,
                          }}
                        />
                      );
                    })}
                  </div>
                ) : (
                  <div style={{ width: '100%', height: '2px', backgroundColor: 'var(--surface-high)' }} />
                )}
              </div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{MESES_CORTOS[mes.mes - 1]}</span>
            </div>
          );
        })}
      </div>

      <figcaption style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', marginTop: '14px' }}>
        {SERIES.map((serie) => (
          <span key={serie.key} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-muted)' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: serie.color }} />
            {serie.etiqueta}
          </span>
        ))}
      </figcaption>
      {!hayDatos && (
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '12px 0 0' }}>
          Aún no hay mantenimientos preventivos programados este año.
        </p>
      )}
    </figure>
  );
}
