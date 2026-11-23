import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { KeyRound, Loader2 } from 'lucide-react';
import { changePassword, type AuthFlowStatus } from '../api/auth.api';
import { passwordChangeSchema, type PasswordChangeFormData } from '../schemas/login.schema';
import { FormField } from '../../../components/shared/FormField';

interface PasswordChangeStepProps {
  passwordToken: string;
  onSuccess: (accessToken: string) => void;
  onNext: (status: AuthFlowStatus, token: string) => void;
}

export function PasswordChangeStep({ passwordToken, onSuccess, onNext }: PasswordChangeStepProps) {
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PasswordChangeFormData>({
    resolver: zodResolver(passwordChangeSchema),
  });

  const onSubmit = async (data: PasswordChangeFormData) => {
    setServerError('');
    setIsSubmitting(true);
    try {
      const result = await changePassword({
        password_token: passwordToken,
        new_password: data.new_password,
        confirm_password: data.confirm_password,
      });

      if (result.status === 'ok' && result.access) {
        onSuccess(result.access);
        return;
      }
      if (result.status === 'mfa_required' && result.mfa_token) {
        onNext('mfa_required', result.mfa_token);
        return;
      }
      if (result.status === 'mfa_setup_required' && result.mfa_token) {
        onNext('mfa_setup_required', result.mfa_token);
        return;
      }
      setServerError('Respuesta inesperada del servidor.');
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setServerError(
        axiosError.response?.data?.detail || 'No se pudo cambiar la contraseña. Intente nuevamente.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            backgroundColor: 'var(--primary-light)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '12px',
          }}
        >
          <KeyRound size={24} color="var(--primary)" />
        </div>
        <h2 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text)', margin: '0 0 4px' }}>
          Cambio de contraseña obligatorio
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
          Debe establecer una nueva contraseña para continuar.
        </p>
      </div>

      {serverError && (
        <div
          role="alert"
          style={{
            backgroundColor: 'var(--danger-bg)',
            color: 'var(--danger-fg)',
            padding: '10px 14px',
            borderRadius: '6px',
            fontSize: '13px',
            marginBottom: '16px',
          }}
        >
          {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <FormField label="Nueva contraseña" htmlFor="new-password" required error={errors.new_password?.message}>
          <input
            id="new-password"
            type="password"
            autoComplete="new-password"
            {...register('new_password')}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: `1px solid ${errors.new_password ? 'var(--danger-fg)' : 'var(--border)'}`,
              borderRadius: '6px',
              fontSize: '14px',
              backgroundColor: 'var(--surface-low)',
              color: 'var(--text)',
            }}
          />
        </FormField>
        <FormField
          label="Confirmar contraseña"
          htmlFor="confirm-password"
          required
          error={errors.confirm_password?.message}
        >
          <input
            id="confirm-password"
            type="password"
            autoComplete="new-password"
            {...register('confirm_password')}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: `1px solid ${errors.confirm_password ? 'var(--danger-fg)' : 'var(--border)'}`,
              borderRadius: '6px',
              fontSize: '14px',
              backgroundColor: 'var(--surface-low)',
              color: 'var(--text)',
            }}
          />
        </FormField>

        <button
          type="submit"
          disabled={isSubmitting}
          style={{
            width: '100%',
            marginTop: '8px',
            padding: '10px',
            backgroundColor: 'var(--primary)',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            opacity: isSubmitting ? 0.7 : 1,
          }}
        >
          {isSubmitting && <Loader2 size={16} />}
          {isSubmitting ? 'Guardando…' : 'Cambiar contraseña'}
        </button>
      </form>
    </div>
  );
}
