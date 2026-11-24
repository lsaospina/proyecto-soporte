import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PageHeader } from '../../../components/shared/PageHeader';
import { DataTable } from '../../../components/shared/DataTable';
import { activosApi } from '../api/activos.api';
import { useAuth } from '../../auth/hooks/useAuth';

type EstadoFiltro = 'activos' | 'inactivos' | 'todos';

function paramsFor(estado: EstadoFiltro, search: string): Record<string, unknown> {
  const params: Record<string, unknown> = { page_size: 100, estado_no: 'DADO_DE_BAJA' };
  if (estado === 'activos') params.is_active = true;
  if (estado === 'inactivos') params.is_active = false;
  if (estado === 'todos') params.todos = 1;
  if (search.trim()) params.search = search.trim();
  return params;
}

export function ActivosListPage() {
  const { user } = useAuth();
  const esAdmin = user?.rol === 'ADMINISTRADOR';
  const [estado, setEstado] = useState<EstadoFiltro>('activos');
  const [search, setSearch] = useState('');
  const qc = useQueryClient();
  const [serverError, setServerError] = useState('');

  const params = paramsFor(estado, search);
  const { data, isError } = useQuery({ queryKey: ['activos', params], queryFn: () => activosApi.list(params) });

  const toggle = useMutation({
    mutationFn: ({ id, activar }: { id: number; activar: boolean }) =>
      activar ? activosApi.reactivar(id) : activosApi.inactivar(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['activos'] }),
  });

  const rows = data?.results ?? [];

  const columns = [
    { key: 'codigo_qr', header: 'Código', render: (r: any) => r.codigo_qr },
    { key: 'serial', header: 'Serial', render: (r: any) => r.serial },
    { key: 'modelo', header: 'Modelo', render: (r: any) => `${r.marca_nombre} / ${r.modelo_nombre}` },
    { key: 'categoria', header: 'Categoría', render: (r: any) => r.categoria_nombre },
    { key: 'estado', header: 'Estado', render: (r: any) => r.estado },
    { key: 'responsable', header: 'Responsable', render: (r: any) => r.responsable_actual ?? '—' },
    { key: 'is_active', header: 'Activo', render: (r: any) => (r.is_active ? 'Sí' : 'No') },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (r: any) => (
        <div style={{ display: 'flex', gap: 8 }}>
          {esAdmin && r.is_active && (
            <button
              onClick={() => {
                setServerError('');
                toggle.mutate(
                  { id: r.id, activar: false },
                  { onError: (e: any) => setServerError(e?.response?.data?.detail || 'No se pudo inactivar.') },
                );
              }}
              style={{ color: 'var(--danger-fg)', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              Inactivar
            </button>
          )}
          {esAdmin && !r.is_active && (
            <button
              onClick={() => {
                setServerError('');
                toggle.mutate(
                  { id: r.id, activar: true },
                  { onError: (e: any) => setServerError(e?.response?.data?.detail || 'No se pudo reactivar.') },
                );
              }}
              style={{ color: 'var(--success-fg)', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              Reactivar
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader title="Activos" subtitle="Inventario de activos tecnológicos" />

      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar serial, código, MAC, marca o modelo"
          style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6, minWidth: 280 }}
        />
        {(['activos', 'inactivos', 'todos'] as EstadoFiltro[]).map((e) => (
          <button
            key={e}
            onClick={() => setEstado(e)}
            style={{
              padding: '4px 10px',
              borderRadius: 6,
              border: '1px solid var(--border)',
              background: estado === e ? 'var(--primary-light)' : 'var(--surface-lowest)',
              cursor: 'pointer',
            }}
          >
            {e}
          </button>
        ))}
      </div>

      {serverError && <div style={{ color: 'var(--danger-fg)', marginBottom: 8 }}>{serverError}</div>}

      {isError ? (
        <div role="alert" style={{ color: 'var(--danger-fg)' }}>No se pudieron cargar los activos.</div>
      ) : (
        <DataTable columns={columns} data={rows} rowKey={(r: any) => r.id} />
      )}
    </div>
  );
}
