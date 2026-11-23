import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft } from 'lucide-react';
import { PageHeader } from '../../../components/shared/PageHeader';
import { FormSection } from '../../../components/shared/FormSection';
import { FormField } from '../../../components/shared/FormField';
import { LoadingSkeleton } from '../../../components/shared/LoadingSkeleton';
import { ErrorState } from '../../../components/shared/ErrorState';
import { createUsuario, getUsuario, updateUsuario } from '../api/usuarios.api';
import { usuarioSchema, usuarioUpdateSchema, type UsuarioFormData, type UsuarioUpdateFormData } from '../schemas/usuario.schema';
import { TempPasswordModal } from '../components/TempPasswordModal';

export function UsuarioFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const userId = id ? Number(id) : null;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [tempPassword, setTempPassword] = useState<string | null>(null);
  const [serverError, setServerError] = useState('');

  const { data: user, isLoading, isError, refetch } = useQuery({
    queryKey: ['usuario', userId],
    queryFn: () => getUsuario(userId!),
    enabled: isEdit && userId !== null,
  });

  const createForm = useForm<UsuarioFormData>({ resolver: zodResolver(usuarioSchema) });
  const editForm = useForm<UsuarioUpdateFormData>({ resolver: zodResolver(usuarioUpdateSchema) });

  useEffect(() => {
    if (isEdit && user) {
      editForm.reset({ nombre_completo: user.nombre_completo, rol: user.rol });
    }
  }, [isEdit, user, editForm]);

  const createMutation = useMutation({
    mutationFn: (data: UsuarioFormData) => createUsuario(data),
    gcTime: 0,
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
      setTempPassword(res.password_temporal);
      createMutation.reset();
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setServerError(axiosError.response?.data?.detail || 'No se pudo crear el usuario.');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: UsuarioUpdateFormData) => updateUsuario(userId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
      queryClient.invalidateQueries({ queryKey: ['usuario', userId] });
      navigate('/usuarios');
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setServerError(axiosError.response?.data?.detail || 'No se pudo actualizar el usuario.');
    },
  });

  if (isEdit && isLoading) return <LoadingSkeleton lines={6} />;
  if (isEdit && isError) return <ErrorState message="No se pudo cargar el usuario." onRetry={() => refetch()} />;

  const onCreate = (data: UsuarioFormData) => {
    setServerError('');
    createMutation.mutate(data);
  };

  const onUpdate = (data: UsuarioUpdateFormData) => {
    setServerError('');
    updateMutation.mutate(data);
  };

  const form = isEdit ? editForm : createForm;
  const errors = form.formState.errors as Record<string, { message?: string } | undefined>;

  return (
    <div>
      <button
        type="button"
        onClick={() => navigate('/usuarios')}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          background: 'none',
          border: 'none',
          color: 'var(--text-muted)',
          fontSize: '13px',
          padding: 0,
          marginBottom: '12px',
          cursor: 'pointer',
        }}
      >
        <ArrowLeft size={16} /> Volver a usuarios
      </button>

      <PageHeader
        title={isEdit ? 'Editar usuario' : 'Nuevo usuario'}
        subtitle={isEdit ? `Actualización de ${user?.email ?? ''}` : 'Registro de nuevo usuario del sistema'}
      />

      {serverError && (
        <div role="alert" style={{ marginBottom: '16px', padding: '10px 12px', borderRadius: '6px', backgroundColor: 'var(--danger-bg)', color: 'var(--danger-fg)', fontSize: '13px' }}>
          {serverError}
        </div>
      )}

      <form onSubmit={isEdit ? editForm.handleSubmit(onUpdate) : createForm.handleSubmit(onCreate)}>
        <FormSection title="Información del usuario" description="Datos básicos y rol de acceso.">
          {!isEdit && (
            <FormField label="Correo electrónico" htmlFor="email" required error={(errors as any).email?.message}>
              <input
                id="email"
                type="email"
                {...(createForm as any).register('email')}
                style={fieldStyle(!!(errors as any).email)}
                placeholder="usuario@empresa.com"
              />
            </FormField>
          )}
          {isEdit && (
            <FormField label="Correo electrónico" htmlFor="email-readonly">
              <input id="email-readonly" value={user?.email ?? ''} disabled style={{ ...fieldStyle(false), opacity: 0.7 }} />
            </FormField>
          )}
          <FormField label="Nombre completo" htmlFor="nombre_completo" required error={errors.nombre_completo?.message}>
            <input
              id="nombre_completo"
              type="text"
              {...(form as any).register('nombre_completo')}
              style={fieldStyle(!!errors.nombre_completo)}
            />
          </FormField>
          <FormField label="Rol" htmlFor="rol" required error={errors.rol?.message}>
            <select id="rol" {...(form as any).register('rol')} style={fieldStyle(!!errors.rol)}>
              <option value="">Seleccione un rol</option>
              <option value="ADMINISTRADOR">Administrador</option>
              <option value="TECNICO">Técnico</option>
              <option value="USUARIO_RESPONSABLE">Usuario responsable</option>
            </select>
          </FormField>
        </FormSection>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
          <button type="button" onClick={() => navigate('/usuarios')} style={secondaryBtn}>Cancelar</button>
          <button
            type="submit"
            disabled={createMutation.isPending || updateMutation.isPending}
            style={{
              padding: '10px 16px',
              backgroundColor: 'var(--primary)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              opacity: createMutation.isPending || updateMutation.isPending ? 0.7 : 1,
            }}
          >
            {isEdit ? 'Guardar cambios' : 'Crear usuario'}
          </button>
        </div>
      </form>

      <TempPasswordModal
        open={!!tempPassword}
        password={tempPassword}
        title="Usuario creado - contraseña temporal"
        onClose={() => {
          setTempPassword(null);
          navigate('/usuarios');
        }}
      />
    </div>
  );
}

function fieldStyle(hasError: boolean): React.CSSProperties {
  return {
    width: '100%',
    padding: '10px 12px',
    border: `1px solid ${hasError ? 'var(--danger-fg)' : 'var(--border)'}`,
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: 'var(--surface-lowest)',
    color: 'var(--text)',
  };
}

const secondaryBtn: React.CSSProperties = {
  padding: '10px 16px',
  backgroundColor: 'var(--surface-lowest)',
  color: 'var(--text)',
  border: '1px solid var(--border)',
  borderRadius: '6px',
  fontSize: '14px',
  fontWeight: 500,
  cursor: 'pointer',
};
