import { useState, type CSSProperties } from 'react';
import { useSearchParams } from 'react-router-dom';
import { keepPreviousData, useQuery, useQueryClient } from '@tanstack/react-query';
import { History, Laptop, PackageCheck, Plus, UserCheck, Users } from 'lucide-react';

import { DataTable, type DataTableColumn } from '../../../components/shared/DataTable';
import { EmptyState } from '../../../components/shared/EmptyState';
import { ErrorState } from '../../../components/shared/ErrorState';
import { KpiCard } from '../../../components/shared/KpiCard';
import { PageHeader } from '../../../components/shared/PageHeader';
import { StatusBadge } from '../../../components/shared/StatusBadge';
import { formatearFecha } from '../../../lib/format';
import { useAuth } from '../../auth/hooks/useAuth';
import { asignacionesApi } from '../api/asignaciones.api';
import { AsignarDialog } from '../components/AsignarDialog';
import { DevolverDialog } from '../components/DevolverDialog';
import type { Asignacion } from '../types';
import { estiloCampo, textoDuracion } from '../utils/asignaciones';

const PAGE_SIZE = 20;
type Vista = 'ACTIVAS' | 'CERRADAS' | 'TODAS';

const VISTAS: Array<{ value: Vista; label: string }> = [
  { value: 'ACTIVAS', label: 'Asignaciones activas' },
  { value: 'CERRADAS', label: 'Historial' },
  { value: 'TODAS', label: 'Todas' },
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

export function AsignacionesPage() {
  const { user } = useAuth();
  const esAdmin = user?.rol === 'ADMINISTRADOR';
  const [parametros] = useSearchParams();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState(parametros.get('search') ?? '');
  const [vista, setVista] = useState<Vista>('ACTIVAS');
  const [page, setPage] = useState(1);
  const [aviso, setAviso] = useState('');
  const [nuevaAbierta, setNuevaAbierta] = useState(false);
  const [reasignar, setReasignar] = useState<Asignacion | null>(null);
  const [devolver, setDevolver] = useState<Asignacion | null>(null);

  const params: Record<string, unknown> = {
    page,
    page_size: PAGE_SIZE,
    ...(search.trim() ? { search: search.trim() } : {}),
    ...(vista === 'ACTIVAS' ? { abierta: true } : {}),
    ...(vista === 'CERRADAS' ? { abierta: false } : {}),
  };

  const listQ = useQuery({
    queryKey: ['asignaciones', params],
    queryFn: () => asignacionesApi.list(params),
    placeholderData: keepPreviousData,
  });
  const resumenQ = useQuery({
    queryKey: ['asignaciones', 'resumen'],
    queryFn: asignacionesApi.resumen,
  });

  const invalidar = () => {
    queryClient.invalidateQueries({ queryKey: ['asignaciones'] });
    queryClient.invalidateQueries({ queryKey: ['activos'] });
  };

  const aplicarFiltro = (accion: () => void) => {
    setPage(1);
    accion();
  };

  const resumen = resumenQ.data;
  const totalPaginas = Math.max(1, Math.ceil((listQ.data?.count ?? 0) / PAGE_SIZE));

  const columns: DataTableColumn<Asignacion>[] = [
    {
      key: 'equipo',
      header: 'Equipo',
      render: (asignacion) => (
        <div>
          <div style={{ fontWeight: 600, color: 'var(--text)' }}>{asignacion.activo_codigo}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {asignacion.marca_nombre} {asignacion.modelo_nombre} · {asignacion.activo_serial}
          </div>
        </div>
      ),
    },
    {
      key: 'responsable',
      header: 'Responsable',
      render: (asignacion) => (
        <div>
          <div style={{ fontWeight: 500 }}>{asignacion.usuario_nombre}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{asignacion.usuario_email}</div>
        </div>
      ),
    },
    {
      key: 'desde',
      header: 'Desde',
      render: (asignacion) => formatearFecha(asignacion.fecha_inicio),
    },
    {
      key: 'hasta',
      header: 'Hasta',
      render: (asignacion) =>
        asignacion.fecha_fin ? formatearFecha(asignacion.fecha_fin) : 'Actual',
    },
    {
      key: 'duracion',
      header: 'Duración',
      render: (asignacion) => textoDuracion(asignacion.dias_asignado),
    },
    {
      key: 'registrado',
      header: 'Registrado por',
      render: (asignacion) => asignacion.asignado_por_nombre,
    },
    {
      key: 'estado',
      header: 'Estado',
      render: (asignacion) => (
        <StatusBadge
          variant={asignacion.activa ? 'success' : 'neutral'}
          label={asignacion.activa ? 'Activa' : 'Cerrada'}
        />
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (asignacion) =>
        esAdmin && asignacion.activa ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {accion('Reasignar', () => setReasignar(asignacion))}
            {accion('Devolver', () => setDevolver(asignacion), 'var(--danger-fg)')}
          </div>
        ) : (
          <span style={{ color: 'var(--text-muted)' }}>—</span>
        ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Asignaciones"
        subtitle="Responsables actuales y trazabilidad de los equipos entregados."
        actions={
          esAdmin ? (
            <button type="button" onClick={() => setNuevaAbierta(true)} style={botonPrimario}>
              <Plus size={14} /> Nueva asignación
            </button>
          ) : undefined
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
            label="Equipos asignados"
            value={String(resumen.asignados)}
            hint={`${resumen.activos_operativos} activos operativos`}
            icon={<Laptop size={16} />}
            tone="primary"
          />
          <KpiCard
            label="Colaboradores con equipo"
            value={String(resumen.colaboradores)}
            hint="Responsables activos"
            icon={<Users size={16} />}
            tone="success"
          />
          <KpiCard
            label="Disponibles para asignar"
            value={String(resumen.disponibles)}
            hint={`${resumen.en_mantenimiento} en mantenimiento`}
            icon={<PackageCheck size={16} />}
            tone="info"
          />
          <KpiCard
            label="Asignaciones históricas"
            value={String(resumen.asignaciones_historicas)}
            hint="Entregas y devoluciones registradas"
            icon={<History size={16} />}
            tone="neutral"
          />
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
          placeholder="Buscar código, serial, colaborador o correo"
          aria-label="Buscar asignaciones"
          style={{ ...estiloCampo(), minWidth: '280px', flex: '1 1 280px' }}
        />
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {VISTAS.map((opcion) => (
            <button
              key={opcion.value}
              type="button"
              aria-pressed={vista === opcion.value}
              onClick={() => aplicarFiltro(() => setVista(opcion.value))}
              style={chipStyle(vista === opcion.value)}
            >
              {opcion.label}
            </button>
          ))}
        </div>
      </div>

      {listQ.isError ? (
        <ErrorState
          message="No se pudieron cargar las asignaciones."
          onRetry={() => listQ.refetch()}
        />
      ) : (
        <DataTable
          columns={columns}
          data={listQ.data?.results ?? []}
          rowKey={(asignacion) => asignacion.id}
          emptyState={
            <EmptyState
              icon={<UserCheck size={32} />}
              title={vista === 'ACTIVAS' ? 'Sin equipos asignados' : 'Sin registros en el historial'}
              description={
                vista === 'ACTIVAS'
                  ? 'Asigna un equipo disponible para dejar trazabilidad del responsable.'
                  : 'Las entregas y devoluciones aparecerán aquí.'
              }
              action={
                esAdmin && vista === 'ACTIVAS' ? (
                  <button type="button" onClick={() => setNuevaAbierta(true)} style={botonPrimario}>
                    Nueva asignación
                  </button>
                ) : undefined
              }
            />
          }
        />
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '12px' }}>
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          {listQ.data?.count ?? 0} registro{(listQ.data?.count ?? 0) === 1 ? '' : 's'}
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

      {nuevaAbierta && (
        <AsignarDialog
          modo="asignar"
          onClose={() => setNuevaAbierta(false)}
          onDone={(mensaje) => {
            setAviso(mensaje);
            setNuevaAbierta(false);
            invalidar();
          }}
        />
      )}

      {reasignar && (
        <AsignarDialog
          modo="reasignar"
          activoFijo={{
            id: reasignar.activo,
            activo_codigo: reasignar.activo_codigo,
            activo_serial: reasignar.activo_serial,
            marca_nombre: reasignar.marca_nombre,
            modelo_nombre: reasignar.modelo_nombre,
          }}
          onClose={() => setReasignar(null)}
          onDone={(mensaje) => {
            setAviso(mensaje);
            setReasignar(null);
            invalidar();
          }}
        />
      )}

      {devolver && (
        <DevolverDialog
          asignacion={devolver}
          onClose={() => setDevolver(null)}
          onDone={(mensaje) => {
            setAviso(mensaje);
            setDevolver(null);
            invalidar();
          }}
        />
      )}
    </div>
  );
}
