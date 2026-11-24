import type { CSSProperties } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  Archive,
  ArrowRight,
  CheckCircle2,
  Monitor,
  ShieldCheck,
  Wallet,
  Wrench,
} from 'lucide-react';

import { ErrorState } from '../../../components/shared/ErrorState';
import { KpiCard, type KpiTone } from '../../../components/shared/KpiCard';
import { LoadingSkeleton } from '../../../components/shared/LoadingSkeleton';
import { PageHeader } from '../../../components/shared/PageHeader';
import { useAuth } from '../../auth/hooks/useAuth';
import { AlertasTablero } from '../components/AlertasTablero';
import { BarrasHorizontales, type BarraItem } from '../components/BarrasHorizontales';
import { CumplimientoMensual } from '../components/CumplimientoMensual';
import { ListaMantenimientos } from '../components/ListaMantenimientos';
import { SeccionPanel } from '../components/SeccionPanel';
import { UltimasAdquisiciones } from '../components/UltimasAdquisiciones';
import { useDashboardResumen } from '../hooks/useDashboardResumen';
import type { DashboardResumen, EstadoActivo } from '../types';
import { formatearFecha, formatearMoneda } from '../../../lib/format';

const TONO_ESTADO: Record<EstadoActivo, KpiTone> = {
  DISPONIBLE: 'info',
  ASIGNADO: 'success',
  EN_MANTENIMIENTO: 'warning',
  DADO_DE_BAJA: 'danger',
};

const enlaceAccion: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '4px',
  fontSize: '12px',
  fontWeight: 600,
  color: 'var(--primary)',
};

const botonPrimario: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '6px',
  padding: '8px 14px',
  borderRadius: 'var(--radius-control)',
  backgroundColor: 'var(--primary)',
  color: 'var(--text-inverse)',
  fontSize: '13px',
  fontWeight: 600,
};

const botonSecundario: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '6px',
  padding: '8px 14px',
  borderRadius: 'var(--radius-control)',
  backgroundColor: 'var(--surface-lowest)',
  border: '1px solid var(--border)',
  color: 'var(--text)',
  fontSize: '13px',
  fontWeight: 500,
};

const gridDosColumnas: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
  gap: '16px',
  marginBottom: '16px',
};

const gridTresColumnas: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
  gap: '16px',
  marginBottom: '16px',
};

function tonoDeCumplimiento(porcentaje: number, agendados: number): KpiTone {
  if (agendados === 0) return 'neutral';
  if (porcentaje >= 80) return 'success';
  if (porcentaje >= 50) return 'warning';
  return 'danger';
}

function Contenido({ data, puedeVerMantenimientos }: { data: DashboardResumen; puedeVerMantenimientos: boolean }) {
  const activos = data.activos;
  const mantenimientos = puedeVerMantenimientos ? data.mantenimientos : null;
  const disponibilidad = activos.total > 0 ? Math.round((activos.operativos * 100) / activos.total) : 0;
  const preventivos = mantenimientos?.preventivos_anio;

  const barrasEstado: BarraItem[] = activos.por_estado.map((item) => ({
    label: item.etiqueta,
    value: item.total,
    tone: TONO_ESTADO[item.estado],
  }));

  const categorias: BarraItem[] = activos.por_categoria.map((item) => ({
    label: item.nombre,
    value: item.total,
    tone: 'primary',
  }));
  const marcas: BarraItem[] = activos.por_marca.map((item) => ({
    label: item.nombre,
    value: item.total,
    tone: 'info',
  }));

  return (
    <>
      {mantenimientos && <AlertasTablero mantenimientos={mantenimientos} anio={data.anio} />}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
          gap: '16px',
          marginBottom: '20px',
        }}
      >
        <KpiCard
          label="Activos vigentes"
          value={String(activos.total)}
          hint={`${activos.inactivos} inactivo${activos.inactivos === 1 ? '' : 's'} en el inventario`}
          icon={<Monitor size={16} />}
          tone="primary"
        />
        <KpiCard
          label="Operativos"
          value={`${disponibilidad}%`}
          hint={`${activos.operativos} disponibles o asignados`}
          icon={<ShieldCheck size={16} />}
          tone="success"
        />
        <KpiCard
          label="En mantenimiento"
          value={String(activos.en_mantenimiento)}
          hint="Equipos fuera de operación"
          icon={<Wrench size={16} />}
          tone="warning"
        />
        <KpiCard
          label="Dados de baja"
          value={String(activos.dados_de_baja)}
          hint="Histórico de bajas del inventario"
          icon={<Archive size={16} />}
          tone="neutral"
        />
        {preventivos && (
          <>
            <KpiCard
              label="Preventivos vencidos"
              value={String(preventivos.vencidos)}
              hint="Requieren reprogramación o cierre"
              icon={<AlertTriangle size={16} />}
              tone="danger"
            />
            <KpiCard
              label="Cumplimiento preventivo"
              value={`${preventivos.porcentaje_cumplimiento}%`}
              hint={`${preventivos.completados} de ${preventivos.agendados} agendados en ${data.anio}`}
              icon={<CheckCircle2 size={16} />}
              tone={tonoDeCumplimiento(preventivos.porcentaje_cumplimiento, preventivos.agendados)}
            />
          </>
        )}
        {mantenimientos && activos.valor_total !== null && (
          <KpiCard
            label="Valor del inventario"
            value={formatearMoneda(activos.valor_total)}
            hint={`Costo de mantenimiento ${data.anio}: ${formatearMoneda(mantenimientos.costo_anio)}`}
            icon={<Wallet size={16} />}
            tone="info"
          />
        )}
      </div>

      {mantenimientos && preventivos && (
        <>
          <div style={gridDosColumnas}>
            <SeccionPanel
              title={`Cumplimiento preventivo ${data.anio}`}
              subtitle={`${preventivos.completados} de ${preventivos.agendados} agendados · ${preventivos.porcentaje_cumplimiento}% de cumplimiento`}
              action={
                <Link to="/mantenimientos" style={enlaceAccion}>
                  Ver calendario <ArrowRight size={12} />
                </Link>
              }
            >
              <CumplimientoMensual meses={mantenimientos.mensual} />
            </SeccionPanel>

            <SeccionPanel
              title="Estado del inventario"
              subtitle={`${activos.total} activos vigentes`}
              action={
                <Link to="/activos" style={enlaceAccion}>
                  Ver inventario <ArrowRight size={12} />
                </Link>
              }
            >
              <BarrasHorizontales items={barrasEstado} vacio="Aún no hay activos registrados." />
            </SeccionPanel>
          </div>

          <div style={gridTresColumnas}>
            <SeccionPanel
              title="Próximos 14 días"
              subtitle="Preventivos pendientes en agenda"
              action={
                <Link to="/mantenimientos" style={enlaceAccion}>
                  Ver todos <ArrowRight size={12} />
                </Link>
              }
            >
              <ListaMantenimientos
                items={mantenimientos.proximos}
                variante="proximo"
                vacio="No hay mantenimientos programados en los próximos 14 días."
              />
            </SeccionPanel>

            <SeccionPanel
              title="Atención inmediata"
              subtitle={`${preventivos.vencidos} preventivos vencidos`}
              action={
                <Link to="/mantenimientos" style={enlaceAccion}>
                  Resolver <ArrowRight size={12} />
                </Link>
              }
            >
              <ListaMantenimientos
                items={mantenimientos.vencidos}
                variante="vencido"
                vacio="No hay mantenimientos vencidos."
              />
            </SeccionPanel>

            <SeccionPanel
              title="Correctivos recientes"
              subtitle={`${mantenimientos.correctivos.registrados_30_dias} en 30 días · ${formatearMoneda(mantenimientos.correctivos.costo_30_dias)}`}
            >
              <ListaMantenimientos
                items={mantenimientos.correctivos.recientes}
                variante="correctivo"
                vacio="Sin correctivos registrados."
              />
            </SeccionPanel>
          </div>
        </>
      )}

      <div style={gridTresColumnas}>
        <SeccionPanel title="Activos por categoría" subtitle="Distribución del inventario vigente">
          <BarrasHorizontales items={categorias} vacio="Aún no hay activos registrados." />
        </SeccionPanel>
        <SeccionPanel title="Marcas principales" subtitle="Equipos por fabricante">
          <BarrasHorizontales items={marcas} vacio="Aún no hay activos registrados." />
        </SeccionPanel>
        <SeccionPanel
          title="Últimas adquisiciones"
          subtitle="Ingresos más recientes al inventario"
          action={
            <Link to="/activos" style={enlaceAccion}>
              Ver inventario <ArrowRight size={12} />
            </Link>
          }
        >
          <UltimasAdquisiciones activos={activos.ultimas_adquisiciones} />
        </SeccionPanel>
      </div>

      {mantenimientos && mantenimientos.activos_sin_preventivo.total > 0 && (
        <SeccionPanel
          title={`Activos sin preventivo en ${data.anio}`}
          subtitle={`${mantenimientos.activos_sin_preventivo.total} activos gestionables sin mantenimiento programado este año`}
          action={
            <Link to="/mantenimientos" style={enlaceAccion}>
              Programar <ArrowRight size={12} />
            </Link>
          }
        >
          <UltimasAdquisiciones activos={mantenimientos.activos_sin_preventivo.activos} />
        </SeccionPanel>
      )}
    </>
  );
}

export function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading, isError, refetch } = useDashboardResumen();
  const puedeVerMantenimientos = user?.rol === 'ADMINISTRADOR' || user?.rol === 'TECNICO';

  const subtitulo = data
    ? `Panorama del inventario${puedeVerMantenimientos ? ' y la operación de mantenimiento' : ''} al ${formatearFecha(data.hoy)}.`
    : 'Panorama del inventario tecnológico y la operación de mantenimiento.';

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle={subtitulo}
        actions={
          puedeVerMantenimientos ? (
            <>
              <Link to="/activos" style={botonSecundario}>
                Ver inventario
              </Link>
              <Link to="/mantenimientos" style={botonPrimario}>
                Mantenimientos
              </Link>
            </>
          ) : undefined
        }
      />

      {isLoading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '16px' }}>
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={index}
              style={{
                padding: '16px',
                minHeight: '112px',
                backgroundColor: 'var(--surface-lowest)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-card)',
              }}
            >
              <LoadingSkeleton lines={2} />
            </div>
          ))}
        </div>
      )}

      {isError && (
        <ErrorState message="No se pudo cargar el tablero." onRetry={() => refetch()} />
      )}

      {data && !isLoading && !isError && (
        <Contenido data={data} puedeVerMantenimientos={puedeVerMantenimientos} />
      )}
    </div>
  );
}
