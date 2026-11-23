import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PageHeader } from '../../../components/shared/PageHeader';
import { DataTable } from '../../../components/shared/DataTable';
import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { catalogosApi } from '../api/catalogos.api';
import type { CatalogoResource } from '../types';

const RESOURCES: { key: CatalogoResource; label: string; endpoint: string }[] = [
  { key: 'sedes', label: 'Sedes', endpoint: 'sedes' },
  { key: 'ubicaciones', label: 'Ubicaciones', endpoint: 'ubicaciones' },
  { key: 'categorias', label: 'Categorías', endpoint: 'categorias' },
  { key: 'marcas', label: 'Marcas', endpoint: 'marcas' },
  { key: 'modelos', label: 'Modelos', endpoint: 'modelos' },
];

type EstadoFiltro = 'activos' | 'inactivos' | 'todos';

export function CatalogosPage() {
  const [resource, setResource] = useState<CatalogoResource>('sedes');
  const [estado, setEstado] = useState<EstadoFiltro>('activos');
  const qc = useQueryClient();
  const endpoint = RESOURCES.find((r) => r.key === resource)!.endpoint;

  const params: Record<string, unknown> = { page_size: 100 };
  if (estado === 'activos') params.is_active = true;
  if (estado === 'inactivos') params.is_active = false;

  const { data } = useQuery({
    queryKey: ['catalogos', resource, estado],
    queryFn: () => catalogosApi.list(endpoint, params),
  });

  const toggle = useMutation({
    mutationFn: ({ id, activar }: { id: number; activar: boolean }) =>
      catalogosApi.update(endpoint, id, { is_active: activar }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['catalogos', resource] }),
  });

  const [serverError, setServerError] = useState('');
  const [confirm, setConfirm] = useState<{ id: number; activar: boolean } | null>(null);

  const rows = (data?.results ?? data ?? []) as Record<string, unknown>[];

  const columns = [
    { key: 'nombre', header: 'Nombre', render: (row: any) => row.nombre },
    { key: 'is_active', header: 'Activo', render: (row: any) => (row.is_active ? 'Sí' : 'No') },
    {
      key: 'acciones', header: 'Acciones', render: (row: any) => (
        <div style={{ display: 'flex', gap: 8 }}>
          {row.is_active ? (
            <button onClick={() => { setServerError(''); toggle.mutate({ id: row.id, activar: false }, { onError: (e: any) => setServerError(e?.response?.data?.detail || 'No se pudo inactivar.') }); }} style={{ color: 'var(--danger-fg)', background: 'none', border: 'none', cursor: 'pointer' }}>
              Inactivar
            </button>
          ) : (
            <button onClick={() => { setServerError(''); toggle.mutate({ id: row.id, activar: true }, { onError: (e: any) => setServerError(e?.response?.data?.detail || 'No se pudo reactivar.') }); }} style={{ color: 'var(--success-fg)', background: 'none', border: 'none', cursor: 'pointer' }}>
              Reactivar
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader title="Catálogos" subtitle="Gestión de sedes, ubicaciones, categorías, marcas y modelos" />
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {RESOURCES.map((r) => (
          <button key={r.key} onClick={() => setResource(r.key)} style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border)', background: resource === r.key ? 'var(--primary)' : 'var(--surface-lowest)', color: resource === r.key ? '#fff' : 'var(--text)', cursor: 'pointer' }}>
            {r.label}
          </button>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {(['activos', 'inactivos', 'todos'] as EstadoFiltro[]).map((e) => (
          <button key={e} onClick={() => setEstado(e)} style={{ padding: '4px 10px', borderRadius: 6, border: '1px solid var(--border)', background: estado === e ? 'var(--primary-light)' : 'var(--surface-lowest)', cursor: 'pointer' }}>
            {e}
          </button>
        ))}
      </div>
      {serverError && <div style={{ color: 'var(--danger-fg)', marginBottom: 8 }}>{serverError}</div>}
      <DataTable
        columns={columns}
        data={rows}
        rowKey={(row: any) => row.id}
      />
      <ConfirmDialog open={confirm !== null} title="Confirmar" description="¿Cambiar estado?" onConfirm={() => { if (confirm) toggle.mutate(confirm); setConfirm(null); }} onCancel={() => setConfirm(null)} />
    </div>
  );
}
