import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { QRCodeSVG } from 'qrcode.react';
import { Smartphone, Copy, Check, Loader2 } from 'lucide-react';
import { mfaCodeSchema, type MFACodeFormData } from '../schemas/mfa.schema';
import { mfaSetup, mfaConfirm } from '../api/auth.api';
import { FormField } from '../../../components/shared/FormField';
import { RecoveryCodesDisplay } from './RecoveryCodesDisplay';
import { useEffect } from 'react';

interface MFASetupStepProps {
  mfaToken: string;
  onSuccess: (accessToken: string) => void;
}

export function MFASetupStep({ mfaToken, onSuccess }: MFASetupStepProps) {
  const [phase, setPhase] = useState<'qr' | 'recovery'>('qr');
  const [setupData, setSetupData] = useState<{ secret: string; otpauth_uri: string } | null>(null);
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([]);
  const [accessToken, setAccessToken] = useState('');
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [secretCopied, setSecretCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const form = useForm<MFACodeFormData>({
    resolver: zodResolver(mfaCodeSchema),
  });

  // Fetch setup data on mount
  useEffect(() => {
    const fetchSetup = async () => {
      try {
        const data = await mfaSetup(mfaToken);
        setSetupData(data);
      } catch (err: unknown) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setServerError(axiosError.response?.data?.detail || 'Error al configurar MFA.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchSetup();
  }, [mfaToken]);

  const onSubmitCode = async (data: MFACodeFormData) => {
    setServerError('');
    setIsSubmitting(true);
    try {
      const result = await mfaConfirm(mfaToken, data.code);
      setRecoveryCodes(result.recovery_codes);
      setAccessToken(result.access);
      setPhase('recovery');
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setServerError(axiosError.response?.data?.detail || 'Código incorrecto. Intente nuevamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCopySecret = async () => {
    if (setupData?.secret) {
      await navigator.clipboard.writeText(setupData.secret);
      setSecretCopied(true);
      setTimeout(() => setSecretCopied(false), 2000);
    }
  };

  // Recovery codes phase
  if (phase === 'recovery') {
    return (
      <RecoveryCodesDisplay
        codes={recoveryCodes}
        onContinue={() => onSuccess(accessToken)}
      />
    );
  }

  // Loading
  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '24px' }}>
        <Loader2 size={32} className="spin" style={{ color: 'var(--primary)', margin: '0 auto 16px' }} />
        <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Generando configuración MFA…</p>
      </div>
    );
  }

  // QR setup phase
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
          <Smartphone size={24} color="var(--primary)" />
        </div>
        <h2 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text)', margin: '0 0 4px' }}>
          Configurar segundo factor
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
          Escanee el código QR con su aplicación de autenticación (Google Authenticator, Authy, etc.)
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

      {setupData && (
        <>
          {/* QR Code */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              padding: '24px',
              backgroundColor: '#FFFFFF',
              borderRadius: 'var(--radius-card)',
              border: '1px solid var(--border)',
              marginBottom: '16px',
            }}
          >
            <QRCodeSVG value={setupData.otpauth_uri} size={180} />
          </div>

          {/* Manual key */}
          <div
            style={{
              backgroundColor: 'var(--neutral-bg)',
              borderRadius: 'var(--radius-control)',
              padding: '12px 16px',
              marginBottom: '20px',
            }}
          >
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Clave manual
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
              <code style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text)', wordBreak: 'break-all' }}>
                {setupData.secret}
              </code>
              <button
                onClick={handleCopySecret}
                aria-label="Copiar clave"
                style={{
                  background: 'none',
                  border: 'none',
                  color: secretCopied ? 'var(--success-fg)' : 'var(--text-muted)',
                  padding: '4px',
                  flexShrink: 0,
                }}
              >
                {secretCopied ? <Check size={16} /> : <Copy size={16} />}
              </button>
            </div>
          </div>

          {/* Confirm with first code */}
          <form onSubmit={form.handleSubmit(onSubmitCode)}>
            <FormField
              label="Código de verificación"
              htmlFor="setup-code"
              required
              error={form.formState.errors.code?.message}
              helpText="Ingrese el código de 6 dígitos que muestra su aplicación"
            >
              <input
                id="setup-code"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                placeholder="000000"
                {...form.register('code')}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: `1px solid ${form.formState.errors.code ? 'var(--danger-fg)' : 'var(--border)'}`,
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
              Activar segundo factor
            </button>
          </form>
        </>
      )}
    </div>
  );
}
