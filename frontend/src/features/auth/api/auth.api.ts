import client from '../../../api/client';

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  status: 'ok' | 'mfa_required' | 'mfa_setup_required';
  access?: string;
  mfa_token?: string;
}

interface MFASetupResponse {
  secret: string;
  otpauth_uri: string;
}

interface MFAConfirmResponse {
  status: string;
  access: string;
  recovery_codes: string[];
}

interface MFAVerifyResponse {
  status: string;
  access: string;
}

interface UserMe {
  id: number;
  email: string;
  nombre_completo: string;
  rol: 'ADMINISTRADOR' | 'TECNICO' | 'USUARIO_RESPONSABLE';
  mfa_activo: boolean;
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await client.post<LoginResponse>('/api/v1/auth/login/', data);
  return response.data;
}

export async function mfaSetup(mfaToken: string): Promise<MFASetupResponse> {
  const response = await client.post<MFASetupResponse>('/api/v1/auth/mfa/setup/', { mfa_token: mfaToken });
  return response.data;
}

export async function mfaConfirm(mfaToken: string, code: string): Promise<MFAConfirmResponse> {
  const response = await client.post<MFAConfirmResponse>('/api/v1/auth/mfa/confirm/', { mfa_token: mfaToken, code });
  return response.data;
}

export async function mfaVerify(mfaToken: string, code?: string, recoveryCode?: string): Promise<MFAVerifyResponse> {
  const response = await client.post<MFAVerifyResponse>('/api/v1/auth/mfa/verify/', {
    mfa_token: mfaToken,
    code: code || '',
    recovery_code: recoveryCode || '',
  });
  return response.data;
}

export async function refreshToken(): Promise<string> {
  const response = await client.post<{ access: string }>('/api/v1/auth/refresh/');
  return response.data.access;
}

export async function logout(): Promise<void> {
  await client.post('/api/v1/auth/logout/');
}

export async function getMe(): Promise<UserMe> {
  const response = await client.get<UserMe>('/api/v1/auth/me/');
  return response.data;
}

export type { LoginRequest, LoginResponse, MFASetupResponse, MFAConfirmResponse, MFAVerifyResponse, UserMe };
