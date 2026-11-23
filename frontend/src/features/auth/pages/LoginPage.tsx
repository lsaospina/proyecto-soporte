import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Shield, Eye, EyeOff, Loader2, Lock, Mail, ArrowRight } from 'lucide-react';
import { loginSchema, type LoginFormData } from '../schemas/login.schema';
import { login } from '../api/auth.api';
import { useAuth } from '../hooks/useAuth';
import { MFAVerifyStep } from '../components/MFAVerifyStep';
import { MFASetupStep } from '../components/MFASetupStep';
import { PasswordChangeStep } from '../components/PasswordChangeStep';
import { FormField } from '../../../components/shared/FormField';
import type { AuthStep } from '../types';

export function LoginPage() {
  const navigate = useNavigate();
  const { setAccessToken, refreshUser } = useAuth();
  const [step, setStep] = useState<AuthStep>('credentials');
  const [mfaToken, setMfaToken] = useState('');
  const [passwordToken, setPasswordToken] = useState('');
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
      } else if (result.status === 'password_change_required' && result.password_token) {
        setPasswordToken(result.password_token);
        setStep('password_change');
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
        axiosError.response?.data?.detail || 'Error al iniciar sesión. Verifique sus credenciales.',
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

  const handlePasswordNext = (status: string, token: string) => {
    if (status === 'mfa_required') {
      setMfaToken(token);
      setStep('mfa_verify');
    } else if (status === 'mfa_setup_required') {
      setMfaToken(token);
      setStep('mfa_setup');
    }
  };

  if (step === 'password_change') {
    return (
      <LoginWrapper>
        <PasswordChangeStep
          passwordToken={passwordToken}
          onSuccess={handleMFASuccess}
          onNext={handlePasswordNext}
        />
      </LoginWrapper>
    );
  }

  if (step === 'mfa_verify') {
    return (
      <LoginWrapper>
        <MFAVerifyStep mfaToken={mfaToken} onSuccess={handleMFASuccess} onBack={() => setStep('credentials')} />
      </LoginWrapper>
    );
  }

  if (step === 'mfa_setup' || step === 'recovery_codes') {
    return (
      <LoginWrapper>
        <MFASetupStep mfaToken={mfaToken} onSuccess={handleMFASuccess} />
      </LoginWrapper>
    );
  }

  return (
    <LoginWrapper>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', marginBottom: '32px' }}>
        <div
          style={{
            width: '56px',
            height: '56px',
            borderRadius: '12px',
            backgroundColor: 'var(--surface-low)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '16px',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <Shield size={24} color="var(--primary)" />
        </div>
        <h1 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text)', margin: '0 0 4px', letterSpacing: '-0.01em' }}>
          Compañia
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)', margin: 0, fontWeight: 500 }}>
          Sistema de Gestión de Inventarios y Activos Tecnológicos
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmitCredentials)} style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
        {serverError && (
          <div
            style={{
              backgroundColor: 'var(--danger-bg)',
              color: 'var(--danger-fg)',
              padding: '10px 14px',
              borderRadius: '6px',
              fontSize: '13px',
              lineHeight: 1.4,
            }}
          >
            {serverError}
          </div>
        )}

        <FormField label="Correo Electrónico Corporativo" htmlFor="corporateEmail" required error={errors.email?.message}>
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Mail size={18} style={{ position: 'absolute', left: '10px', color: 'var(--text-muted)' }} />
            <input
              id="corporateEmail"
              type="email"
              autoComplete="email"
              autoFocus
              placeholder="usuario@empresa.com"
              {...register('email')}
              style={{
                width: '100%',
                padding: '8px 10px 8px 36px',
                border: `1px solid ${errors.email ? 'var(--danger-fg)' : 'var(--border)'}`,
                borderRadius: '6px',
                fontSize: '14px',
                backgroundColor: 'var(--surface-low)',
                color: 'var(--text)',
                outline: 'none',
              }}
            />
          </div>
        </FormField>

        <FormField label="Contraseña" htmlFor="corporatePassword" required error={errors.password?.message}>
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Lock size={18} style={{ position: 'absolute', left: '10px', color: 'var(--text-muted)' }} />
            <input
              id="corporatePassword"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              placeholder="••••••••••••"
              {...register('password')}
              style={{
                width: '100%',
                padding: '8px 36px 8px 36px',
                border: `1px solid ${errors.password ? 'var(--danger-fg)' : 'var(--border)'}`,
                borderRadius: '6px',
                fontSize: '14px',
                backgroundColor: 'var(--surface-low)',
                color: 'var(--text)',
                outline: 'none',
              }}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              style={{
                position: 'absolute',
                right: '8px',
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                padding: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
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
            gap: '6px',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            opacity: isSubmitting ? 0.7 : 1,
          }}
        >
          {isSubmitting && <Loader2 size={16} />}
          {isSubmitting ? 'Autenticando…' : 'Iniciar sesión'}
          {!isSubmitting && <ArrowRight size={16} />}
        </button>
      </form>
    </LoginWrapper>
  );
}

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
          maxWidth: '480px',
          backgroundColor: 'var(--surface-lowest)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          padding: '40px 32px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        {children}
      </div>
    </div>
  );
}
