import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Pencil, KeyRound, ShieldOff, UserX, UserCheck, Users } from 'lucide-react';
import { PageHeader } from '../../../components/shared/PageHeader';
import { DataTable, type DataTableColumn } from '../../../components/shared/DataTable';
import { StatusBadge } from '../../../components/shared/StatusBadge';
import { EmptyState } from '../../../components/shared/EmptyState';
import { ErrorState } from '../../../components/shared/ErrorState';
import { LoadingSkeleton } from '../../../components/shared/LoadingSkeleton';
import {
  activarUsuario,
  desactivarUsuario,
  listUsuarios,
  resetMfa,
  resetPassword,
} from '../api/usuarios.api';
import type { Usuario } from '../types';
import { TempPasswordModal } from '../components/TempPasswordModal';
import { ConfirmResetMfaDialog } from '../components/ConfirmResetMfaDialog';

const roleLabels: Record<string, string> = {
  ADMINISTRADOR: 'Administrador',
  TECNICO: 'Técnico',
  USUARIO_RESPONSABLE: 'Usuario responsable',
};

export function UsuariosListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [rol, setRol] = useState('');
  const [isActive, setIsActive] = useState('');
  const [tempPassword, setTempPassword] = useState<string | null>(null);
  const [resetMfaTarget, setResetMfaTarget] = useState<Usuario | null>(null);
  const [feedback, setFeedback] = useState<string>('');

  const queryKey = ['usuarios', { page, search, rol, is_active: isActive }];
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey,
    queryFn: () =>
      listUsuarios({
        page,
        search: search || undefined,
        rol: rol || undefined,
        is_active: isActive || undefined,
      }),
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['usuarios'] });

  const resetPasswordMutation = useMutation({
    mutationFn: (id: number) => resetPassword(id),
    gcTime: 0,
    onSuccess: (res) => {
      setTempPassword(res.password_temporal);
      resetPasswordMutation.reset();
      invalidate();
    },
  });

  const resetMfaMutation = useMutation({
    mutationFn: (id: number) => resetMfa(id),
    gcTime: 0,
    onSuccess: () => {
      setResetMfaTarget(null);
      setFeedback('MFA reseteado correctamente.');
      resetMfaMutation.reset();
      invalidate();
    },
  });

  const activarMutation = useMutation({
    mutationFn: (id: number) => activarUsuario(id),
    onSuccess: () => {
      setFeedback('Usuario reactivado.');
      invalidate();
    },
  });

  const desactivarMutation = useMutation({
    mutationFn: (id: number) => desactivarUsuario(id),
    onSuccess: () => {
      setFeedback('Usuario inactivado.');
      invalidate();
    },
  });

  const columns: DataTableColumn<Usuario>[] = [
    {
      key: 'nombre',
      header: 'Nombre',
      render: (u) => (
        <div>
          <div style={{ fontWeight: 500 }}>{u.nombre_completo}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{u.email}</div>
        </div>
      ),
    },
    { key: 'rol', header: 'Rol', render: (u) => roleLabels[u.rol] ?? u.rol },
    {
      key: 'estado',
      header: 'Estado',
      render: (u) => (
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          <StatusBadge variant={u.is_active ? 'success' : 'neutral'} label={u.is_active ? 'Activo' : 'Inactivo'} />
          {u.esta_bloqueado && <StatusBadge variant="danger" label="Bloqueado" />}
          {u.debe_cambiar_password && <StatusBadge variant="warning" label="Cambio pendiente" />}
        </div>
      ),
    },
    {
      key: 'mfa',
      header: 'MFA',
      render: (u) => (
        <StatusBadge variant={u.mfa_activo ? 'success' : 'warning'} label={u.mfa_activo ? 'Activo' : 'Pendiente'} />
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (u) => (
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          <ActionButton label="Editar" icon={<Pencil size={14} />} onClick={() => navigate(`/usuarios/${u.id}/editar`)} />
          <ActionButton
            label="Reset contraseña"
            icon={<KeyRound size={14} />}
            onClick={() => resetPasswordMutation.mutate(u.id)}
          />
          <ActionButton label="Reset MFA" icon={<ShieldOff size={14} />} onClick={() => setResetMfaTarget(u)} />
          {u.is_active ? (
            <ActionButton label="Inactivar" icon={<UserX size={14} />} onClick={() => desactivarMutation.mutate(u.id)} />
          ) : (
            <ActionButton label="Activar" icon={<UserCheck size={14} />} onClick={() => activarMutation.mutate(u.id)} />
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Gestión de usuarios"
        subtitle="Administración de cuentas, roles y acceso"
        actions={
          <button
            type="button"
            onClick={() => navigate('/usuarios/nuevo')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              backgroundColor: 'var(--primary)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <Plus size={16} /> Nuevo usuario
          </button>
        }
      />

      {feedback && (
        <div
          role="status"
          style={{
            marginBottom: '12px',
            padding: '10px 12px',
            borderRadius: '6px',
            backgroundColor: 'var(--success-bg)',
            color: 'var(--success-fg)',
            fontSize: '13px',
          }}
        >
          {feedback}
        </div>
      )}

      <div
        style={{
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          marginBottom: '16px',
          alignItems: 'center',
        }}
      >
        <input
          aria-label="Buscar usuarios"
          placeholder="Buscar por correo o nombre"
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
          style={inputStyle}
        />
        <select aria-label="Filtrar por rol" value={rol} onChange={(e) => { setPage(1); setRol(e.target.value); }} style={inputStyle}>
          <option value="">Todos los roles</option>
          <option value="ADMINISTRADOR">Administrador</option>
          <option value="TECNICO">Técnico</option>
          <option value="USUARIO_RESPONSABLE">Usuario responsable</option>
        </select>
        <select aria-label="Filtrar por estado" value={isActive} onChange={(e) => { setPage(1); setIsActive(e.target.value); }} style={inputStyle}>
          <option value="">Todos los estados</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </select>
      </div>

      {isLoading && <LoadingSkeleton lines={6} />}
      {isError && <ErrorState message="No se pudieron cargar los usuarios." onRetry={() => refetch()} />}
      {!isLoading && !isError && (
        <>
          <DataTable
            columns={columns}
            data={data?.results ?? []}
            rowKey={(u) => u.id}
            emptyState={
              <EmptyState
                icon={<Users size={40} />}
                title="Sin usuarios"
                description="No hay usuarios que coincidan con los filtros."
              />
            }
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px', fontSize: '13px', color: 'var(--text-muted)' }}>
            <span>Total: {data?.count ?? 0}</span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button type="button" disabled={!data?.previous} onClick={() => setPage((p) => Math.max(1, p - 1))} style={pagerBtn(!!data?.previous)}>Anterior</button>
              <span>Página {page}</span>
              <button type="button" disabled={!data?.next} onClick={() => setPage((p) => p + 1)} style={pagerBtn(!!data?.next)}>Siguiente</button>
            </div>
          </div>
        </>
      )}

      <TempPasswordModal
        open={!!tempPassword}
        password={tempPassword}
        title="Contraseña temporal (reset)"
        onClose={() => setTempPassword(null)}
      />
      <ConfirmResetMfaDialog
        open={!!resetMfaTarget}
        userName={resetMfaTarget?.nombre_completo}
        isLoading={resetMfaMutation.isPending}
        onConfirm={() => resetMfaTarget && resetMfaMutation.mutate(resetMfaTarget.id)}
        onCancel={() => setResetMfaTarget(null)}
      />
    </div>
  );
}

function ActionButton({ label, icon, onClick }: { label: string; icon: React.ReactNode; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 8px',
        borderRadius: '6px',
        border: '1px solid var(--border)',
        backgroundColor: 'var(--surface-lowest)',
        color: 'var(--text)',
        fontSize: '12px',
        cursor: 'pointer',
      }}
    >
      {icon}
      {label}
    </button>
  );
}

const inputStyle: React.CSSProperties = {
  padding: '8px 10px',
  border: '1px solid var(--border)',
  borderRadius: '6px',
  fontSize: '13px',
  backgroundColor: 'var(--surface-lowest)',
  color: 'var(--text)',
  minWidth: '180px',
};

function pagerBtn(enabled: boolean): React.CSSProperties {
  return {
    padding: '4px 10px',
    border: '1px solid var(--border)',
    borderRadius: '6px',
    backgroundColor: 'var(--surface-lowest)',
    color: enabled ? 'var(--text)' : 'var(--text-muted)',
    cursor: enabled ? 'pointer' : 'not-allowed',
    fontSize: '13px',
  };
}
