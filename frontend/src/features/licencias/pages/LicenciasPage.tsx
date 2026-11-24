import { useState, type CSSProperties } from 'react';
import { Link } from 'react-router-dom';
import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { AlertTriangle, CalendarClock, KeyRound, Plus, Wallet } from 'lucide-react';

import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { DataTable, type DataTableColumn } from '../../../components/shared/DataTable';
import { EmptyState } from '../../../components/shared/EmptyState';
import { ErrorState } from '../../../components/shared/ErrorState';
import { KpiCard } from '../../../components/shared/KpiCard';
import { PageHeader } from '../../../components/shared/PageHeader';
import { StatusBadge } from '../../../components/shared/StatusBadge';
import { formatearFecha, formatearMoneda } from '../../../lib/format';
import { licenciasApi } from '../api/licencias.api';
import { estiloCampo } from '../components/campos';
import { RenovarLicenciaDialog } from '../components/RenovarLicenciaDialog';
import type { EstadoRenovacion, Licencia, Periodicidad } from '../types';
import {
  ETIQUETA_ESTADO,
  ETIQUETA_PERIODICIDAD,
  OPCIONES_PERIODICIDAD,
  VARIANTE_ESTADO,
  textoDias,
} from '../utils/licencias';

const PAGE_SIZE = 20;
type FiltroEstado = 'TODAS' | EstadoRenovacion;

const ESTADOS_FILTRO: Array<{ value: FiltroEstado; label: string }> = [
  { value: 'TODAS', label: 'Todas' },
  { value: 'VIGENTE', label: 'Vigentes' },
  { value: 'POR_VENCER', label: 'Por vencer' },
  { value: 'VENCIDA', label: 'Vencidas' },
  { value: 'INACTIVA', label: 'Inactivas' },
];

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

function accion(texto: string, onClick: () => void, color = 'var(--primary)') {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{ background: 'none', border: 'none', color, fontSize: '12px', fontWeight: 600, padding: 0 }}
    >
      {texto}
    </button>
  );
}

function chipStyle(activo: boolean): CSSProperties {
  return {
    padding: '5px 12px',
    fontSize: '12px',
    fontWeight: 500,
    borderRadius: '9999px',
    border: `1px solid ${activo ? 'var(--primary)' : 'var(--border)'}`,
    backgroundColor: activo ? 'var(--primary-light)' : 'var(--surface-lowest)',
    color: activo ? 'var(--primary)' : 'var(--text-muted)',
  };
}

export function LicenciasPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [estado, setEstado] = useState<FiltroEstado>('TODAS');
  const [proveedor, setProveedor] = useState('');
  const [periodicidad, setPeriodicidad] = useState<'' | Periodicidad>('');
  const [page, setPage] = useState(1);
  const [aviso, setAviso] = useState('');
  const [serverError, setServerError] = useState('');
  const [renovar, setRenovar] = useState<Licencia | null>(null);
  const [inactivar, setInactivar] = useState<Licencia | null>(null);

  const params: Record<string, unknown> = {
    page,
    page_size: PAGE_SIZE,
    ...(search.trim() ? { search: search.trim() } : {}),
    ...(estado !== 'TODAS' ? { estado_renovacion: estado } : {}),
    ...(proveedor ? { proveedor } : {}),
    ...(periodicidad ? { periodicidad } : {}),
  };

  const listQ = useQuery({
    queryKey: ['licencias', params],
    queryFn: () => licenciasApi.list(params),
    placeholderData: keepPreviousData,
  });
  const resumenQ = useQuery({
    queryKey: ['licencias', 'resumen'],
    queryFn: licenciasApi.resumen,
  });
  const proveedoresQ = useQuery({
    queryKey: ['licencias', 'proveedores'],
    queryFn: licenciasApi.proveedores,
  });

  const invalidar = () => queryClient.invalidateQueries({ queryKey: ['licencias'] });

  const toggle = useMutation({
    mutationFn: ({ id, activar }: { id: number; activar: boolean }) =>
      activar ? licenciasApi.reactivar(id) : licenciasApi.inactivar(id),
    onSuccess: (_data, variables) => {
      setAviso(variables.activar ? 'Licencia reactivada.' : 'Licencia inactivada.');
      setInactivar(null);
      setServerError('');
      invalidar();
    },
    onError: (error: unknown) => {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setServerError(axiosError.response?.data?.detail || 'No se pudo actualizar la licencia.');
      setInactivar(null);
    },
  });

  const aplicarFiltro = (accion: () => void) => {
    setPage(1);
    accion();
  };

  const resumen = resumenQ.data;
  const totalPaginas = Math.max(1, Math.ceil((listQ.data?.count ?? 0) / PAGE_SIZE));

  const columns: DataTableColumn<Licencia>[] = [
    {
      key: 'servicio',
      header: 'Servicio',
      render: (licencia) => (
        <div>
          <div style={{ fontWeight: 600, color: 'var(--text)' }}>{licencia.servicio}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {licencia.proveedor_nombre} · {licencia.cantidad} licencia{licencia.cantidad === 1 ? '' : 's'}
          </div>
        </div>
      ),
    },
    {
      key: 'renovacion',
      header: 'Renovación',
      render: (licencia) => (
        <div>
          <div>{formatearFecha(licencia.fecha_renovacion)}</div>
          <div style={{ fontSize: '12px', color: `var(--${VARIANTE_ESTADO[licencia.estado_renovacion] === 'neutral' ? 'neutral' : VARIANTE_ESTADO[licencia.estado_renovacion]}-fg)` }}>
            {textoDias(licencia.dias_para_renovacion)}
          </div>
        </div>
      ),
    },
    {
      key: 'periodicidad',
      header: 'Periodicidad',
      render: (licencia) => ETIQUETA_PERIODICIDAD[licencia.periodicidad],
    },
    {
      key: 'valor',
      header: 'Valor',
      render: (licencia) => (licencia.valor ? formatearMoneda(licencia.valor) : 'Variable'),
    },
    {
      key: 'automatica',
      header: 'Automática',
      render: (licencia) => (licencia.renovacion_automatica ? 'Sí' : 'No'),
    },
    {
      key: 'uso',
      header: 'Uso',
      render: (licencia) => (
        <span style={{ display: 'inline-block', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', verticalAlign: 'bottom' }}>
          {licencia.responsable_uso || '—'}
        </span>
      ),
    },
    {
      key: 'estado',
      header: 'Estado',
      render: (licencia) => (
        <StatusBadge
          variant={VARIANTE_ESTADO[licencia.estado_renovacion]}
          label={ETIQUETA_ESTADO[licencia.estado_renovacion]}
        />
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (licencia) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {licencia.is_active && accion('Renovar', () => setRenovar(licencia))}
          <Link to={`/licencias/${licencia.id}/editar`} style={{ fontSize: '12px', fontWeight: 600 }}>
            Editar
          </Link>
          {licencia.is_active
            ? accion('Inactivar', () => setInactivar(licencia), 'var(--danger-fg)')
            : accion('Reactivar', () => toggle.mutate({ id: licencia.id, activar: true }), 'var(--success-fg)')}
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Licencias"
        subtitle="Suscripciones, renovaciones y costos de servicios tecnológicos."
        actions={
          <Link to="/licencias/nueva" style={botonPrimario}>
            <Plus size={14} /> Nueva licencia
          </Link>
        }
      />

      {resumen && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
            gap: '16px',
            marginBottom: '20px',
          }}
        >
          <KpiCard
            label="Licencias activas"
            value={String(resumen.activas)}
            hint={`${resumen.renovacion_automatica} con renovación automática`}
            icon={<KeyRound size={16} />}
            tone="primary"
          />
          <KpiCard
            label="Por vencer"
            value={String(resumen.por_vencer)}
            hint="En los próximos 30 días"
            icon={<CalendarClock size={16} />}
            tone="warning"
          />
          <KpiCard
            label="Vencidas"
            value={String(resumen.vencidas)}
            hint={resumen.vencidas > 0 ? 'Requieren renovación' : 'Sin pendientes'}
            icon={<AlertTriangle size={16} />}
            tone={resumen.vencidas > 0 ? 'danger' : 'success'}
          />
          <KpiCard
            label="Costo anual estimado"
            value={formatearMoneda(resumen.costo_anual_estimado)}
            hint={`${formatearMoneda(resumen.costo_por_vencer)} por renovar en 30 días`}
            icon={<Wallet size={16} />}
            tone="info"
          />
        </div>
      )}

      {resumen && resumen.vencidas > 0 && (
        <div
          role="alert"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 14px',
            marginBottom: '8px',
            borderRadius: 'var(--radius-card)',
            backgroundColor: 'var(--danger-bg)',
            color: 'var(--danger-fg)',
            fontSize: '13px',
            fontWeight: 500,
          }}
        >
          <AlertTriangle size={16} aria-hidden />
          {resumen.vencidas} licencia{resumen.vencidas === 1 ? '' : 's'} vencida
          {resumen.vencidas === 1 ? '' : 's'} requiere
          {resumen.vencidas === 1 ? '' : 'n'} gestión de renovación.
        </div>
      )}

      {resumen && resumen.por_vencer > 0 && (
        <div
          role="status"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 14px',
            marginBottom: '16px',
            borderRadius: 'var(--radius-card)',
            backgroundColor: 'var(--warning-bg)',
            color: 'var(--warning-fg)',
            fontSize: '13px',
            fontWeight: 500,
          }}
        >
          <CalendarClock size={16} aria-hidden />
          {resumen.por_vencer} licencia{resumen.por_vencer === 1 ? '' : 's'} se renueva
          {resumen.por_vencer === 1 ? '' : 'n'} en los próximos 30 días.
        </div>
      )}

      {aviso && (
        <div
          role="status"
          style={{
            padding: '10px 14px',
            marginBottom: '16px',
            borderRadius: 'var(--radius-card)',
            backgroundColor: 'var(--success-bg)',
            color: 'var(--success-fg)',
            fontSize: '13px',
            fontWeight: 500,
          }}
        >
          {aviso}
        </div>
      )}

      {serverError && (
        <div role="alert" style={{ color: 'var(--danger-fg)', fontSize: '13px', marginBottom: '12px' }}>
          {serverError}
        </div>
      )}

      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          alignItems: 'center',
          padding: '12px',
          marginBottom: '16px',
          backgroundColor: 'var(--surface-lowest)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-card)',
        }}
      >
        <input
          value={search}
          onChange={(event) => aplicarFiltro(() => setSearch(event.target.value))}
          placeholder="Buscar servicio, proveedor, cuenta o responsable"
          aria-label="Buscar licencias"
          style={{ ...estiloCampo(), minWidth: '280px', flex: '1 1 280px' }}
        />
        <select
          value={proveedor}
          onChange={(event) => aplicarFiltro(() => setProveedor(event.target.value))}
          aria-label="Filtrar por proveedor"
          style={{ ...estiloCampo(), width: 'auto' }}
        >
          <option value="">Todos los proveedores</option>
          {(proveedoresQ.data ?? []).map((opcion) => (
            <option key={opcion.id} value={opcion.id}>
              {opcion.nombre}
            </option>
          ))}
        </select>
        <select
          value={periodicidad}
          onChange={(event) => aplicarFiltro(() => setPeriodicidad(event.target.value as '' | Periodicidad))}
          aria-label="Filtrar por periodicidad"
          style={{ ...estiloCampo(), width: 'auto' }}
        >
          <option value="">Todas las periodicidades</option>
          {OPCIONES_PERIODICIDAD.map((opcion) => (
            <option key={opcion.value} value={opcion.value}>
              {opcion.label}
            </option>
          ))}
        </select>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {ESTADOS_FILTRO.map((opcion) => (
            <button
              key={opcion.value}
              type="button"
              aria-pressed={estado === opcion.value}
              onClick={() => aplicarFiltro(() => setEstado(opcion.value))}
              style={chipStyle(estado === opcion.value)}
            >
              {opcion.label}
            </button>
          ))}
        </div>
      </div>

      {listQ.isError ? (
        <ErrorState message="No se pudieron cargar las licencias." onRetry={() => listQ.refetch()} />
      ) : (
        <DataTable
          columns={columns}
          data={listQ.data?.results ?? []}
          rowKey={(licencia) => licencia.id}
          emptyState={
            <EmptyState
              icon={<KeyRound size={32} />}
              title="Sin licencias registradas"
              description="Registra la primera suscripción para controlar renovaciones, costos y responsables."
              action={
                <Link to="/licencias/nueva" style={botonPrimario}>
                  Nueva licencia
                </Link>
              }
            />
          }
        />
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '12px' }}>
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          {listQ.data?.count ?? 0} licencia{(listQ.data?.count ?? 0) === 1 ? '' : 's'}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            type="button"
            disabled={!listQ.data?.previous}
            onClick={() => setPage((actual) => Math.max(1, actual - 1))}
            style={chipStyle(false)}
          >
            Anterior
          </button>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Página {page} de {totalPaginas}
          </span>
          <button
            type="button"
            disabled={!listQ.data?.next}
            onClick={() => setPage((actual) => actual + 1)}
            style={chipStyle(false)}
          >
            Siguiente
          </button>
        </div>
      </div>

      {renovar && (
        <RenovarLicenciaDialog
          licencia={renovar}
          onClose={() => setRenovar(null)}
          onDone={(mensaje) => {
            setAviso(mensaje);
            setServerError('');
            setRenovar(null);
            invalidar();
          }}
        />
      )}

      <ConfirmDialog
        open={!!inactivar}
        title="Inactivar licencia"
        description={
          inactivar
            ? `${inactivar.servicio} (${inactivar.proveedor_nombre}) dejará de contar en los indicadores y renovaciones.`
            : undefined
        }
        confirmLabel="Inactivar"
        destructive
        isLoading={toggle.isPending}
        onConfirm={() => inactivar && toggle.mutate({ id: inactivar.id, activar: false })}
        onCancel={() => setInactivar(null)}
      />
    </div>
  );
}
