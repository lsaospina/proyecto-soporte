export type UserRole = 'ADMINISTRADOR' | 'TECNICO' | 'USUARIO_RESPONSABLE';

export interface User {
  id: number;
  email: string;
  nombre_completo: string;
  rol: UserRole;
  mfa_activo: boolean;
}

export type AuthStep =
  | 'credentials'
  | 'password_change'
  | 'mfa_verify'
  | 'mfa_setup'
  | 'recovery_codes';
