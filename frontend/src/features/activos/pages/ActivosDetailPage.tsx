import { useState } from 'react';
import type { ReactNode } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  ClipboardList,
  History as HistoryIcon,
  Laptop,
  ShieldCheck,
  UserCheck,
  Wrench,
} from 'lucide-react';

import { PageHeader } from '../../../components/shared/PageHeader';
import { FormSection } from '../../../components/shared/FormSection';
import { DataTable, type DataTableColumn } from '../../../components/shared/DataTable';
import { EmptyState } from '../../../components/shared/EmptyState';
import { LoadingSkeleton } from '../../../components/shared/LoadingSkeleton';
import { StatusBadge, type BadgeVariant } from '../../../components/shared/StatusBadge';
import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { formatearFecha } from '../../../lib/format';
import { activosApi } from '../api/activos.api';
import { asignacionesApi } from '../../asignaciones/api/asignaciones.api';
import { mantenimientosApi } from '../../mantenimientos/api/mantenimientos.api';
import { incidentesApi } from '../../incidentes/api/incidentes.api';
import { documentosApi } from '../../documentos/api/documentos.api';
import { DocumentosTab } from '../../documentos/components/DocumentosTab';
import { useAuth } from '../../auth/hooks/useAuth';

const ESTADO_VARIANT: Record<string, BadgeVariant> = {
  DISPONIBLE: 'success',
  ASIGNADO: 'info',
  EN_MANTENIMIENTO: 'warning',
  DADO_DE_BAJA: 'danger',
};

const GARANTIA_VARIANT: Record<string, BadgeVariant> = {
  VIGENTE: 'success',
  POR_VENCER: 'warning',
  VENCIDA: 'danger',
  SIN_GARANTIA: 'neutral',
};

const INCIDENTE_ESTADO_VARIANT: Record<string, BadgeVariant> = {
  REPORTADO: 'info',
  EN_PROCESO: 'warning',
  RESUELTO: 'success',
  CERRADO: 'neutral',
  CANCELADO: 'danger',
};

const SITUACION_VARIANT: Record<string, BadgeVariant> = {
  PENDIENTE: 'info',
  COMPLETADO: 'success',
  VENCIDO: 'warning',
  INCUMPLIDO: 'danger',
  CANCELADO: 'neutral',
};

type Pestaña = 'resumen' | 'asignaciones' | 'mantenimientos' | 'incidentes' | 'documentos' | 'historial';

const estiloBotonSecundario = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  padding: '8px 14px',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-control)',
  background: 'var(--surface-lowest)',
  color: 'var(--text)',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
} as const;

const estiloBotonPrimario = {
  ...estiloBotonSecundario,
  background: 'var(--primary)',
  borderColor: 'var(--primary)',
  color: 'var(--text-inverse)',
} as const;

function Campo({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 500 }}>{label}</span>
      <span style={{ fontSize: 14, color: 'var(--text)' }}>{children}</span>
    </div>
  );
}

const gridCampos = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
  gap: '16px 24px',
} as const;

export function ActivosDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { user } = useAuth();
  const esAdmin = user?.rol === 'ADMINISTRADOR';
  const [pestana, setPestana] = useState<Pestaña>('resumen');
  const [confirm, setConfirm] = useState(false);
  const [serverError, setServerError] = useState('');

  const activoId = Number(id);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['activos', activoId],
    queryFn: () => activosApi.retrieve(activoId),
  });
  const { data: historial } = useQuery({
    queryKey: ['activos', activoId, 'historial'],
    queryFn: () => activosApi.historial(activoId),
  });
  const { data: asignaciones } = useQuery({
    queryKey: ['asignaciones', 'activo', activoId],
    queryFn: () => asignacionesApi.list({ activo: activoId, page_size: 100 }),
  });
  const { data: mantenimientos } = useQuery({
    queryKey: ['mantenimientos', 'activo', activoId],
    queryFn: () => mantenimientosApi.list({ activo: activoId, page_size: 100, tipo: 'PREVENTIVO' }),
  });
  const { data: correctivos } = useQuery({
    queryKey: ['mantenimientos-correctivos', 'activo', activoId],
    queryFn: () => mantenimientosApi.list({ activo: activoId, page_size: 100, tipo: 'CORRECTIVO' }),
  });
  const { data: incidentes } = useQuery({
    queryKey: ['incidentes', 'activo', activoId],
    queryFn: () => incidentesApi.list({ activo: activoId, page_size: 100 }),
  });
  const { data: documentos } = useQuery({
    queryKey: ['documentos', 'activo', activoId],
    queryFn: () => documentosApi.list({ activo: activoId, page_size: 100 }),
    enabled: pestana === 'documentos' && !!user,
  });

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Detalle del activo" />
        <LoadingSkeleton lines={6} />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div>
        <PageHeader title="Detalle del activo" />
        <EmptyState
          title="No se pudo cargar el activo"
          description="El activo no existe o no tienes acceso."
          action={
            <button type="button" onClick={() => refetch()} style={estiloBotonSecundario}>
              Reintentar
            </button>
          }
        />
      </div>
    );
  }

  const toggleActivo = async () => {
    setServerError('');
    try {
      if (data.is_active) {
        await activosApi.inactivar(activoId);
      } else {
        await activosApi.reactivar(activoId);
      }
      await qc.invalidateQueries({ queryKey: ['activos'] });
      navigate('/activos');
    } catch (e: any) {
      setServerError(e?.response?.data?.detail || 'No se pudo cambiar el estado.');
    } finally {
      setConfirm(false);
    }
  };

  const listaMantenimientos = [...(mantenimientos?.results ?? []), ...(correctivos?.results ?? [])].sort(
    (a: any, b: any) => (b.fecha_programada ?? '').localeCompare(a.fecha_programada ?? ''),
  );
  const listaIncidentes = incidentes?.results ?? [];
  const listaAsignaciones = asignaciones?.results ?? [];

  const pestañas: Array<{ value: Pestaña; label: string; count: number }> = [
    { value: 'resumen', label: 'Resumen', count: 0 },
    { value: 'asignaciones', label: 'Asignaciones', count: listaAsignaciones.length },
    { value: 'mantenimientos', label: 'Mantenimientos', count: listaMantenimientos.length },
    { value: 'incidentes', label: 'Incidentes', count: listaIncidentes.length },
    { value: 'documentos', label: 'Documentos', count: documentos?.count ?? 0 },
    { value: 'historial', label: 'Historial', count: historial?.length ?? 0 },
  ];

  const columnasAsignaciones: DataTableColumn<any>[] = [
    {
      key: 'responsable',
      header: 'Responsable',
      render: (a) => (
        <div>
          <div style={{ fontWeight: 500 }}>{a.usuario_nombre}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{a.usuario_email}</div>
        </div>
      ),
    },
    { key: 'desde', header: 'Desde', render: (a) => formatearFecha(a.fecha_inicio) },
    { key: 'hasta', header: 'Hasta', render: (a) => (a.fecha_fin ? formatearFecha(a.fecha_fin) : 'Actual') },
    {
      key: 'estado',
      header: 'Estado',
      render: (a) => (
        <StatusBadge variant={a.activa ? 'success' : 'neutral'}>{a.activa ? 'Vigente' : 'Cerrada'}</StatusBadge>
      ),
    },
    { key: 'registrado', header: 'Registrado por', render: (a) => a.asignado_por_nombre },
  ];

  const columnasMantenimientos: DataTableColumn<any>[] = [
    {
      key: 'tipo',
      header: 'Tipo',
      render: (m) => (
        <StatusBadge variant={m.tipo === 'CORRECTIVO' ? 'warning' : 'info'}>
          {m.tipo === 'CORRECTIVO' ? 'Correctivo' : 'Preventivo'}
        </StatusBadge>
      ),
    },
    { key: 'fecha', header: 'Fecha', render: (m) => formatearFecha(m.fecha_programada) },
    {
      key: 'situacion',
      header: 'Situación',
      render: (m) => <StatusBadge variant={SITUACION_VARIANT[m.situacion] ?? 'neutral'}>{m.situacion}</StatusBadge>,
    },
    { key: 'tecnico', header: 'Técnico', render: (m) => m.tecnico_nombre ?? '—' },
    { key: 'descripcion', header: 'Descripción', render: (m) => m.observacion || '—' },
  ];

  const columnasIncidentes: DataTableColumn<any>[] = [
    { key: 'fecha', header: 'Fecha', render: (i) => formatearFecha(i.fecha) },
    {
      key: 'estado',
      header: 'Estado',
      render: (i) => (
        <StatusBadge variant={INCIDENTE_ESTADO_VARIANT[i.estado] ?? 'neutral'}>{i.estado}</StatusBadge>
      ),
    },
    { key: 'descripcion', header: 'Descripción', render: (i) => i.descripcion },
    { key: 'reportado', header: 'Reportado por', render: (i) => i.reportado_por_nombre },
  ];

  return (
    <div>
      <PageHeader
        title={data.serial}
        subtitle={`${data.marca_nombre} / ${data.modelo_nombre} · ${data.codigo_qr}`}
        breadcrumbs={[{ label: 'Activos', href: '/activos' }, { label: data.serial }]}
        actions={
          <>
            <button type="button" onClick={() => navigate(`/activos/${id}/editar`)} style={estiloBotonSecundario}>
              <Wrench size={16} /> Editar
            </button>
            {esAdmin && (
              <button
                type="button"
                onClick={() => setConfirm(true)}
                style={
                  data.is_active
                    ? { ...estiloBotonSecundario, color: 'var(--danger-fg)', borderColor: 'var(--danger-fg)' }
                    : estiloBotonPrimario
                }
              >
                {data.is_active ? 'Inactivar' : 'Reactivar'}
              </button>
            )}
          </>
        }
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <StatusBadge variant={ESTADO_VARIANT[data.estado] ?? 'neutral'}>{data.estado}</StatusBadge>
        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          {data.is_active ? 'Registro activo' : 'Registro inactivo'}
        </span>
        {data.plazo_garantia_meses != null && (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--text-muted)' }}>
            <ShieldCheck size={16} /> Garantía:{' '}
            <StatusBadge variant={GARANTIA_VARIANT[data.estado_garantia] ?? 'neutral'}>
              {data.estado_garantia}
            </StatusBadge>
          </span>
        )}
      </div>

      {serverError && (
        <div role="alert" style={{ color: 'var(--danger-fg)', marginBottom: 12, fontSize: 13 }}>
          {serverError}
        </div>
      )}

      <div
        role="tablist"
        style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 20, borderBottom: '1px solid var(--border)' }}
      >
        {pestañas.map((p) => {
          const activa = pestana === p.value;
          return (
            <button
              key={p.value}
              type="button"
              role="tab"
              aria-selected={activa}
              onClick={() => setPestana(p.value)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 12px',
                marginBottom: -1,
                border: 'none',
                borderBottom: `2px solid ${activa ? 'var(--primary)' : 'transparent'}`,
                background: 'none',
                color: activa ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: activa ? 600 : 500,
                fontSize: 14,
                cursor: 'pointer',
              }}
            >
              {p.label}
              {p.count > 0 && (
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    padding: '1px 7px',
                    borderRadius: 9999,
                    background: activa ? 'var(--primary-light)' : 'var(--neutral-bg)',
                    color: activa ? 'var(--primary)' : 'var(--neutral-fg)',
                  }}
                >
                  {p.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {pestana === 'resumen' && (
        <div>
          <FormSection title="Información del activo" description="Datos técnicos y de identificación del equipo.">
            <div style={gridCampos}>
              <Campo label="Serial">{data.serial}</Campo>
              <Campo label="Código QR">{data.codigo_qr}</Campo>
              <Campo label="Marca">{data.marca_nombre}</Campo>
              <Campo label="Modelo">{data.modelo_nombre}</Campo>
              <Campo label="Categoría">{data.categoria_nombre}</Campo>
              <Campo label="Estado">
                <StatusBadge variant={ESTADO_VARIANT[data.estado] ?? 'neutral'}>{data.estado}</StatusBadge>
              </Campo>
              <Campo label="Responsable actual">{data.responsable_actual ?? 'Sin asignar'}</Campo>
              <Campo label="Fecha de adquisición">{formatearFecha(data.fecha_adquisicion)}</Campo>
              <Campo label="Valor de adquisición">
                {data.valor_adquisicion != null
                  ? new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(
                      Number(data.valor_adquisicion),
                    )
                  : '—'}
              </Campo>
              <Campo label="Procesador">{data.procesador || '—'}</Campo>
              <Campo label="RAM (GB)">{data.ram_gb ?? '—'}</Campo>
              <Campo label="Almacenamiento (GB)">{data.almacenamiento_gb ?? '—'}</Campo>
              <Campo label="Dirección MAC">{data.direccion_mac || '—'}</Campo>
            </div>
          </FormSection>

          <FormSection title="Garantía" description="Calculada a partir de la fecha de adquisición y el plazo definido.">
            {data.plazo_garantia_meses != null ? (
              <div style={gridCampos}>
                <Campo label="Plazo">{data.plazo_garantia_meses} meses</Campo>
                <Campo label="Vencimiento estimado">{formatearFecha(data.fecha_vencimiento_garantia)}</Campo>
                <Campo label="Estado de la garantía">
                  <StatusBadge variant={GARANTIA_VARIANT[data.estado_garantia] ?? 'neutral'}>
                    {data.estado_garantia}
                  </StatusBadge>
                </Campo>
              </div>
            ) : (
              <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: 0 }}>
                No se ha registrado un plazo de garantía para este activo.
              </p>
            )}
          </FormSection>

          {data.observaciones && (
            <FormSection title="Observaciones">
              <p style={{ fontSize: 14, color: 'var(--text)', margin: 0, whiteSpace: 'pre-wrap' }}>{data.observaciones}</p>
            </FormSection>
          )}
        </div>
      )}

      {pestana === 'asignaciones' && (
        <FormSection
          title="Historial de asignaciones"
          description="Entregas y devoluciones del equipo con su responsable."
        >
          <div style={{ marginBottom: listaAsignaciones.length > 0 ? 16 : 0 }}>
            <Link to={`/asignaciones?search=${encodeURIComponent(data.codigo_qr)}`} style={{ fontSize: 13, color: 'var(--primary)' }}>
              Gestionar asignaciones de este equipo
            </Link>
          </div>
          <DataTable
            columns={columnasAsignaciones}
            data={listaAsignaciones}
            rowKey={(a) => a.id}
            emptyState={
              <EmptyState
                icon={<UserCheck size={32} />}
                title="Sin asignaciones"
                description="Este equipo no tiene asignaciones registradas."
              />
            }
          />
        </FormSection>
      )}

      {pestana === 'mantenimientos' && (
        <FormSection
          title="Mantenimientos"
          description="Preventivos y correctivos registrados para este activo."
        >
          <DataTable
            columns={columnasMantenimientos}
            data={listaMantenimientos}
            rowKey={(m) => m.id}
            emptyState={
              <EmptyState
                icon={<Wrench size={32} />}
                title="Sin mantenimientos"
                description="No hay mantenimientos preventivos ni correctivos para este activo."
              />
            }
          />
        </FormSection>
      )}

      {pestana === 'incidentes' && (
        <FormSection title="Incidentes" description="Fallas reportadas y su estado de atención.">
          <DataTable
            columns={columnasIncidentes}
            data={listaIncidentes}
            rowKey={(i) => i.id}
            emptyState={
              <EmptyState
                icon={<ClipboardList size={32} />}
                title="Sin incidentes"
                description="No se han reportado incidentes para este activo."
              />
            }
          />
        </FormSection>
      )}

      {pestana === 'documentos' && <DocumentosTab activoId={activoId} />}

      {pestana === 'historial' && (
        <FormSection title="Historial de cambios" description="Registro de auditoría de las modificaciones del activo.">
          {(historial ?? []).length === 0 ? (
            <EmptyState
              icon={<HistoryIcon size={32} />}
              title="Sin cambios registrados"
              description="Aún no hay cambios de auditoría para este activo."
            />
          ) : (
            <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
              {(historial ?? []).map((h: any, idx: number) => (
                <li
                  key={idx}
                  style={{
                    display: 'flex',
                    gap: 12,
                    paddingBottom: 12,
                    borderBottom: idx < (historial ?? []).length - 1 ? '1px solid var(--border)' : 'none',
                  }}
                >
                  <Laptop size={16} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: 2 }} />
                  <div style={{ fontSize: 13 }}>
                    <div style={{ color: 'var(--text)', fontWeight: 500 }}>
                      {new Date(h.fecha).toLocaleString('es-CO')} · {h.tipo === '+' ? 'Creación' : h.tipo === '~' ? 'Modificación' : 'Eliminación'}
                    </div>
                    <div style={{ color: 'var(--text-muted)' }}>
                      {h.usuario ? `Por ${h.usuario}` : 'Sistema'}
                      {(h.campos ?? []).length > 0 ? ` · Campos: ${(h.campos ?? []).join(', ')}` : ''}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </FormSection>
      )}

      <ConfirmDialog
        open={confirm}
        title={data.is_active ? 'Inactivar activo' : 'Reactivar activo'}
        description={data.is_active ? '¿Inactivar este activo?' : '¿Reactivar este activo?'}
        onConfirm={toggleActivo}
        onCancel={() => setConfirm(false)}
      />
    </div>
  );
}
