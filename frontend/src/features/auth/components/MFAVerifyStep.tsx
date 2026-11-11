import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ShieldCheck, ArrowLeft, KeyRound, Loader2 } from 'lucide-react';
import { mfaCodeSchema, recoveryCodeSchema, type MFACodeFormData, type RecoveryCodeFormData } from '../schemas/mfa.schema';
import { mfaVerify } from '../api/auth.api';
import { FormField } from '../../../components/shared/FormField';

interface MFAVerifyStepProps {
  mfaToken: string;
  onSuccess: (accessToken: string) => void;
  onBack: () => void;
}

export function MFAVerifyStep({ mfaToken, onSuccess, onBack }: MFAVerifyStepProps) {
  const [mode, setMode] = useState<'totp' | 'recovery'>('totp');
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const totpForm = useForm<MFACodeFormData>({
    resolver: zodResolver(mfaCodeSchema),
  });

  const recoveryForm = useForm<RecoveryCodeFormData>({
    resolver: zodResolver(recoveryCodeSchema),
  });

  const onSubmitTOTP = async (data: MFACodeFormData) => {
    setServerError('');
    setIsSubmitting(true);
    try {
      const result = await mfaVerify(mfaToken, data.code);
      onSuccess(result.access);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setServerError(axiosError.response?.data?.detail || 'Código incorrecto. Intente nuevamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onSubmitRecovery = async (data: RecoveryCodeFormData) => {
    setServerError('');
    setIsSubmitting(true);
    try {
      const result = await mfaVerify(mfaToken, undefined, data.recovery_code);
      onSuccess(result.access);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setServerError(axiosError.response?.data?.detail || 'Código de recuperación inválido.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <button
        onClick={onBack}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          background: 'none',
          border: 'none',
          color: 'var(--text-muted)',
          fontSize: '13px',
          padding: '0',
          marginBottom: '24px',
        }}
      >
        <ArrowLeft size={16} />
        Volver
      </button>

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
          <ShieldCheck size={24} color="var(--primary)" />
        </div>
        <h2 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text)', margin: '0 0 4px' }}>
          Verificación de segundo factor
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
          {mode === 'totp'
            ? 'Ingrese el código de 6 dígitos de su aplicación de autenticación.'
            : 'Ingrese uno de sus códigos de recuperación de emergencia.'}
        </p>
      </div>

      {serverError && (
        <div
          style={{
            backgroundColor: 'var(--danger-bg)',
            color: 'var(--danger-fg)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-control)',
            fontSize: '13px',
            marginBottom: '16px',
          }}
        >
          {serverError}
        </div>
      )}

      {mode === 'totp' ? (
        <form onSubmit={totpForm.handleSubmit(onSubmitTOTP)}>
          <FormField
            label="Código de verificación"
            htmlFor="mfa-code"
            required
            error={totpForm.formState.errors.code?.message}
          >
            <input
              id="mfa-code"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              autoFocus
              maxLength={6}
              placeholder="000000"
              {...totpForm.register('code')}
              style={{
                width: '100%',
                padding: '12px 16px',
                border: `1px solid ${totpForm.formState.errors.code ? 'var(--danger-fg)' : 'var(--border)'}`,
                borderRadius: 'var(--radius-control)',
                fontSize: '20px',
                fontWeight: 600,
                letterSpacing: '0.3em',
                textAlign: 'center',
                backgroundColor: 'var(--surface)',
                color: 'var(--text)',
                outline: 'none',
              }}
            />
          </FormField>
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: 'var(--primary)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: 'var(--radius-control)',
              fontSize: '14px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            {isSubmitting && <Loader2 size={16} className="spin" />}
            Verificar
          </button>
        </form>
      ) : (
        <form onSubmit={recoveryForm.handleSubmit(onSubmitRecovery)}>
          <FormField
            label="Código de recuperación"
            htmlFor="recovery-code"
            required
            error={recoveryForm.formState.errors.recovery_code?.message}
          >
            <input
              id="recovery-code"
              type="text"
              autoComplete="off"
              autoFocus
              placeholder="Ingrese su código de recuperación"
              {...recoveryForm.register('recovery_code')}
              style={{
                width: '100%',
                padding: '10px 14px',
                border: `1px solid ${recoveryForm.formState.errors.recovery_code ? 'var(--danger-fg)' : 'var(--border)'}`,
                borderRadius: 'var(--radius-control)',
                fontSize: '14px',
                backgroundColor: 'var(--surface)',
                color: 'var(--text)',
                outline: 'none',
              }}
            />
          </FormField>
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: 'var(--primary)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: 'var(--radius-control)',
              fontSize: '14px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            {isSubmitting && <Loader2 size={16} className="spin" />}
            Usar código de recuperación
          </button>
        </form>
      )}

      <div style={{ textAlign: 'center', marginTop: '16px' }}>
        <button
          type="button"
          onClick={() => {
            setMode(mode === 'totp' ? 'recovery' : 'totp');
            setServerError('');
          }}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--primary)',
            fontSize: '13px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          <KeyRound size={14} />
          {mode === 'totp' ? 'Usar código de recuperación' : 'Usar código TOTP'}
        </button>
      </div>
    </div>
  );
}
