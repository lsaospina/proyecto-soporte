import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Archive, Plus } from 'lucide-react';

import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { DataTable, type DataTableColumn } from '../../../components/shared/DataTable';
import { EmptyState } from '../../../components/shared/EmptyState';
import { ErrorState } from '../../../components/shared/ErrorState';
import { FormField } from '../../../components/shared/FormField';
import { LoadingSkeleton } from '../../../components/shared/LoadingSkeleton';
import { PageHeader } from '../../../components/shared/PageHeader';
import { activosApi } from '../../activos/api/activos.api';
import { documentosApi } from '../../documentos/api/documentos.api';
import { bajasApi, type Baja } from '../api/bajas.api';

const PAGE_SIZE = 20;

function hoyISO(): string {
  return new Date().toISOString().slice(0, 10);
}

const estiloPrimario = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  padding: '8px 14px',
  borderRadius: 'var(--radius-control)',
  backgroundColor: 'var(--primary)',
  color: 'var(--text-inverse)',
  fontSize: 13,
  fontWeight: 600,
  border: 'none',
  cursor: 'pointer',
} as const;

const estiloSecundario = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  padding: '8px 14px',
  borderRadius: 'var(--radius-control)',
  backgroundColor: 'var(--surface-lowest)',
  color: 'var(--text)',
  border: '1px solid var(--border)',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
} as const;

function RegistrarBajaDialog({
  onClose,
  onDone,
}: {
  onClose: () => void;
  onDone: (mensaje: string) => void;
}) {
  const qc = useQueryClient();
  const [activoId, setActivoId] = useState<number | ''>('');
  const [fecha, setFecha] = useState(hoyISO());
  const [motivo, setMotivo] = useState('');
  const [documentoId, setDocumentoId] = useState<number | ''>('');
  const [error, setError] = useState('');

  const activosQ = useQuery({
    queryKey: ['activos-baja-opciones'],
    queryFn: () =>
      activosApi.list({ page_size: 100, is_active: true, estado_no: 'DADO_DE_BAJA' }),
  });
  const documentosQ = useQuery({
    queryKey: ['documentos', 'activo', activoId],
    queryFn: () => documentosApi.list({ activo: Number(activoId), page_size: 100 }),
    enabled: activoId !== '',
  });

  const crear = useMutation({
    mutationFn: () =>
      bajasApi.create({
        activo: Number(activoId),
        fecha: fecha || undefined,
        motivo: motivo.trim(),
        documento: documentoId === '' ? null : Number(documentoId),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['bajas'] });
      qc.invalidateQueries({ queryKey: ['activos'] });
      onDone('Baja registrada correctamente.');
    },
    onError: (e: any) => {
      const data = e?.response?.data;
      const campos = data?.errors?.map((x: any) => x.message).join(' ');
      setError(campos || data?.detail || 'No se pudo registrar la baja.');
    },
  });

  const enviar = () => {
    setError('');
    if (activoId === '') {
      setError('Selecciona el activo a dar de baja.');
      return;
    }
    if (!motivo.trim()) {
      setError('Indica el motivo de la baja.');
      return;
    }
    crear.mutate();
  };

  const activos = activosQ.data?.results ?? [];
  const documentos = documentosQ.data?.results ?? [];

  return (
    <ConfirmDialog
      open
      title="Registrar baja de activo"
      description="La baja es definitiva y marca el activo como dado de baja."
      confirmLabel={crear.isPending ? 'Registrando…' : 'Registrar baja'}
      destructive
      isLoading={crear.isPending}
      onCancel={onClose}
      onConfirm={enviar}
    >
      <FormField label="Activo" htmlFor="baja_activo" required>
        <select
          id="baja_activo"
          value={activoId}
          onChange={(e) => {
            setActivoId(e.target.value ? Number(e.target.value) : '');
            setDocumentoId('');
          }}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        >
          <option value="">{activosQ.isLoading ? 'Cargando…' : '-- Selecciona --'}</option>
          {activos.map((a: any) => (
            <option key={a.id} value={a.id}>
              {a.codigo_qr} · {a.serial} · {a.marca_nombre}/{a.modelo_nombre}
            </option>
          ))}
        </select>
      </FormField>
      <FormField label="Fecha de baja" htmlFor="baja_fecha">
        <input
          id="baja_fecha"
          type="date"
          max={hoyISO()}
          value={fecha}
          onChange={(e) => setFecha(e.target.value)}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      <FormField label="Motivo" htmlFor="baja_motivo" required>
        <textarea
          id="baja_motivo"
          value={motivo}
          onChange={(e) => setMotivo(e.target.value)}
          placeholder="Motivo de la baja (obsolescencia, daño irreparable, etc.)"
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      <FormField label="Documento soporte (opcional)" htmlFor="baja_documento">
        <select
          id="baja_documento"
          value={documentoId}
          onChange={(e) => setDocumentoId(e.target.value ? Number(e.target.value) : '')}
          disabled={activoId === '' || documentosQ.isLoading}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        >
          <option value="">
            {activoId === '' ? 'Selecciona primero un activo' : '-- Sin documento --'}
          </option>
          {documentos.map((d: any) => (
            <option key={d.id} value={d.id}>
              {d.nombre}
            </option>
          ))}
        </select>
      </FormField>
      {error && (
        <div role="alert" style={{ color: 'var(--danger-fg)', fontSize: 13 }}>
          {error}
        </div>
      )}
    </ConfirmDialog>
  );
}

export function BajasPage() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [aviso, setAviso] = useState('');
  const [nuevaAbierta, setNuevaAbierta] = useState(false);

  const params: Record<string, unknown> = {
    page,
    page_size: PAGE_SIZE,
    ...(search.trim() ? { search: search.trim() } : {}),
  };

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['bajas', params],
    queryFn: () => bajasApi.list(params),
  });

  const bajas = data?.results ?? [];
  const totalPaginas = Math.max(1, Math.ceil((data?.count ?? 0) / PAGE_SIZE));

  const columnas: DataTableColumn<Baja>[] = [
    {
      key: 'equipo',
      header: 'Equipo',
      render: (b) => (
        <div>
          <div style={{ fontWeight: 600 }}>{b.activo_codigo}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {b.marca_nombre} {b.modelo_nombre} · {b.activo_serial}
          </div>
        </div>
      ),
    },
    { key: 'fecha', header: 'Fecha de baja', render: (b) => b.fecha },
    { key: 'motivo', header: 'Motivo', render: (b) => b.motivo },
    { key: 'autorizado', header: 'Autorizado por', render: (b) => b.autorizado_por_nombre },
    { key: 'documento', header: 'Documento', render: (b) => b.documento_nombre ?? '—' },
  ];

  return (
    <div>
      <PageHeader
        title="Bajas"
        subtitle="Registro de activos dados de baja definitiva."
        actions={
          <button type="button" onClick={() => setNuevaAbierta(true)} style={estiloPrimario}>
            <Plus size={14} /> Registrar baja
          </button>
        }
      />

      {aviso && (
        <div
          role="status"
          style={{
            padding: '10px 14px',
            marginBottom: 16,
            borderRadius: 'var(--radius-card)',
            backgroundColor: 'var(--success-bg)',
            color: 'var(--success-fg)',
            fontSize: 13,
            fontWeight: 500,
          }}
        >
          {aviso}
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        <input
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder="Buscar serial, código o motivo"
          style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6, minWidth: 280 }}
        />
      </div>

      {isLoading ? (
        <LoadingSkeleton lines={5} />
      ) : isError ? (
        <ErrorState message="No se pudieron cargar las bajas." onRetry={() => refetch()} />
      ) : (
        <DataTable
          columns={columnas}
          data={bajas}
          rowKey={(b) => b.id}
          emptyState={
            <EmptyState
              icon={<Archive size={32} />}
              title="Sin bajas registradas"
              description="Cuando des de baja un activo, aparecerá aquí con su motivo y soporte."
              action={
                <button type="button" onClick={() => setNuevaAbierta(true)} style={estiloPrimario}>
                  Registrar baja
                </button>
              }
            />
          }
        />
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 12 }}>
        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          {data?.count ?? 0} registro{(data?.count ?? 0) === 1 ? '' : 's'}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button type="button" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))} style={estiloSecundario}>
            Anterior
          </button>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            Página {page} de {totalPaginas}
          </span>
          <button type="button" disabled={!data?.next} onClick={() => setPage((p) => p + 1)} style={estiloSecundario}>
            Siguiente
          </button>
        </div>
      </div>

      {nuevaAbierta && (
        <RegistrarBajaDialog
          onClose={() => setNuevaAbierta(false)}
          onDone={(mensaje) => {
            setAviso(mensaje);
            setNuevaAbierta(false);
          }}
        />
      )}
    </div>
  );
}
