import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { PageHeader } from '../../../components/shared/PageHeader';
import { StatusBadge, type BadgeVariant } from '../../../components/shared/StatusBadge';
import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { activosApi } from '../api/activos.api';
import { useAuth } from '../../auth/hooks/useAuth';

const ESTADO_VARIANT: Record<string, BadgeVariant> = {
  DISPONIBLE: 'success',
  ASIGNADO: 'info',
  EN_MANTENIMIENTO: 'warning',
  DADO_DE_BAJA: 'danger',
};

export function ActivosDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { user } = useAuth();
  const esAdmin = user?.rol === 'ADMINISTRADOR';
  const [confirm, setConfirm] = useState(false);
  const [serverError, setServerError] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['activos', id],
    queryFn: () => activosApi.retrieve(Number(id)),
  });
  const { data: historial } = useQuery({
    queryKey: ['activos', id, 'historial'],
    queryFn: () => activosApi.historial(Number(id)),
  });

  if (isLoading || !data) return <div>Cargando…</div>;

  const toggleActivo = async () => {
    setServerError('');
    try {
      if (data.is_active) {
        await activosApi.inactivar(Number(id));
      } else {
        await activosApi.reactivar(Number(id));
      }
      await qc.invalidateQueries({ queryKey: ['activos'] });
      navigate('/activos');
    } catch (e: any) {
      setServerError(e?.response?.data?.detail || 'No se pudo cambiar el estado.');
    } finally {
      setConfirm(false);
    }
  };

  return (
    <div>
      <PageHeader title={data.serial} subtitle={data.codigo_qr} />
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button
          onClick={() => navigate(`/activos/${id}/editar`)}
          style={{ padding: '8px 16px', border: '1px solid var(--border)', background: 'var(--surface-lowest)', cursor: 'pointer' }}
        >
          Editar
        </button>
        {esAdmin && (
          <button
            onClick={() => setConfirm(true)}
            style={{ padding: '8px 16px', border: '1px solid var(--border)', background: 'var(--surface-lowest)', cursor: 'pointer' }}
          >
            {data.is_active ? 'Inactivar' : 'Reactivar'}
          </button>
        )}
      </div>

      {serverError && <div style={{ color: 'var(--danger-fg)', marginBottom: 8 }}>{serverError}</div>}

      <div>
        <h3>Resumen</h3>
        <p>Serial: {data.serial}</p>
        <p>Modelo: {data.marca_nombre} / {data.modelo_nombre}</p>
        <p>Categoría: {data.categoria_nombre}</p>
        <p>
          Estado: <StatusBadge variant={ESTADO_VARIANT[data.estado] ?? 'neutral'}>{data.estado}</StatusBadge>
        </p>
        <p>Activo: {data.is_active ? 'Sí' : 'No'}</p>
      </div>

      <div>
        <h3>Historial de cambios</h3>
        <ul>
          {(historial ?? []).map((h: any, i: number) => (
            <li key={i}>
              {new Date(h.fecha).toLocaleString()} — {h.tipo} — {(h.campos ?? []).join(', ')}
            </li>
          ))}
        </ul>
      </div>

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
