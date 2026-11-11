import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Shield, Eye, EyeOff, Loader2 } from 'lucide-react';
import { loginSchema, type LoginFormData } from '../schemas/login.schema';
import { login } from '../api/auth.api';
import { useAuth } from '../hooks/useAuth';
import { MFAVerifyStep } from '../components/MFAVerifyStep';
import { MFASetupStep } from '../components/MFASetupStep';
import { FormField } from '../../../components/shared/FormField';
import type { AuthStep } from '../types';

export function LoginPage() {
  const navigate = useNavigate();
  const { setAccessToken, refreshUser } = useAuth();
  const [step, setStep] = useState<AuthStep>('credentials');
  const [mfaToken, setMfaToken] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmitCredentials = async (data: LoginFormData) => {
    setServerError('');
    setIsSubmitting(true);
    try {
      const result = await login(data);

      if (result.status === 'ok' && result.access) {
        setAccessToken(result.access);
        await refreshUser();
        navigate('/dashboard', { replace: true });
      } else if (result.status === 'mfa_required' && result.mfa_token) {
        setMfaToken(result.mfa_token);
        setStep('mfa_verify');
      } else if (result.status === 'mfa_setup_required' && result.mfa_token) {
        setMfaToken(result.mfa_token);
        setStep('mfa_setup');
      }
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setServerError(
        axiosError.response?.data?.detail || 'Error al iniciar sesión. Verifique sus credenciales.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMFASuccess = async (accessToken: string) => {
    setAccessToken(accessToken);
    await refreshUser();
    navigate('/dashboard', { replace: true });
  };

  // MFA verify step
  if (step === 'mfa_verify') {
    return (
      <LoginWrapper>
        <MFAVerifyStep mfaToken={mfaToken} onSuccess={handleMFASuccess} onBack={() => setStep('credentials')} />
      </LoginWrapper>
    );
  }

  // MFA setup step
  if (step === 'mfa_setup' || step === 'recovery_codes') {
    return (
      <LoginWrapper>
        <MFASetupStep mfaToken={mfaToken} onSuccess={handleMFASuccess} />
      </LoginWrapper>
    );
  }

  // Credentials step
  return (
    <LoginWrapper>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div
          style={{
            width: '56px',
            height: '56px',
            borderRadius: '12px',
            backgroundColor: 'var(--primary)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '16px',
          }}
        >
          <Shield size={28} color="#FFFFFF" />
        </div>
        <h1 style={{ fontSize: '24px', fontWeight: 600, color: 'var(--text)', margin: '0 0 4px' }}>
          ITAM
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)', margin: 0 }}>
          Sistema de Gestión de Inventarios y Activos Tecnológicos
        </p>
      </div>

      <div
        style={{
          backgroundColor: 'var(--neutral-bg)',
          borderRadius: 'var(--radius-control)',
          padding: '10px 16px',
          marginBottom: '24px',
          textAlign: 'center',
          fontSize: '12px',
          fontWeight: 500,
          color: 'var(--neutral-fg)',
          letterSpacing: '0.03em',
          textTransform: 'uppercase',
        }}
      >
        Portal de autenticación
      </div>

      {serverError && (
        <div
          style={{
            backgroundColor: 'var(--danger-bg)',
            color: 'var(--danger-fg)',
            padding: '12px 16px',
            borderRadius: 'var(--radius-control)',
            fontSize: '13px',
            marginBottom: '16px',
          }}
        >
          {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmitCredentials)}>
        <FormField
          label="Correo electrónico"
          htmlFor="email"
          required
          error={errors.email?.message}
        >
          <input
            id="email"
            type="email"
            autoComplete="email"
            autoFocus
            placeholder="usuario@empresa.com"
            {...register('email')}
            style={{
              width: '100%',
              padding: '10px 14px',
              border: `1px solid ${errors.email ? 'var(--danger-fg)' : 'var(--border)'}`,
              borderRadius: 'var(--radius-control)',
              fontSize: '14px',
              backgroundColor: 'var(--surface)',
              color: 'var(--text)',
              outline: 'none',
              transition: 'border-color var(--transition-fast)',
            }}
          />
        </FormField>

        <FormField
          label="Contraseña"
          htmlFor="password"
          required
          error={errors.password?.message}
        >
          <div style={{ position: 'relative' }}>
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              placeholder="••••••••"
              {...register('password')}
              style={{
                width: '100%',
                padding: '10px 42px 10px 14px',
                border: `1px solid ${errors.password ? 'var(--danger-fg)' : 'var(--border)'}`,
                borderRadius: 'var(--radius-control)',
                fontSize: '14px',
                backgroundColor: 'var(--surface)',
                color: 'var(--text)',
                outline: 'none',
                transition: 'border-color var(--transition-fast)',
              }}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                padding: '4px',
                display: 'flex',
              }}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
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
            fontSize: '15px',
            fontWeight: 600,
            marginTop: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
          }}
        >
          {isSubmitting && <Loader2 size={18} className="spin" />}
          {isSubmitting ? 'Verificando…' : 'Iniciar sesión'}
        </button>
      </form>

      <p
        style={{
          textAlign: 'center',
          fontSize: '12px',
          color: 'var(--text-muted)',
          marginTop: '24px',
        }}
      >
        Autenticación de segundo factor (MFA) requerida
      </p>
    </LoginWrapper>
  );
}

/** Wrapper centrado para las pantallas de login */
function LoginWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: 'var(--background)',
        padding: '24px',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '420px',
          backgroundColor: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-card)',
          padding: '40px 32px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        {children}
      </div>
    </div>
  );
}
