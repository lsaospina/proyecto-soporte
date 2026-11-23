export type UserRole = 'ADMINISTRADOR' | 'TECNICO' | 'USUARIO_RESPONSABLE';

export interface Usuario {
  id: number;
  email: string;
  nombre_completo: string;
  rol: UserRole;
  is_active: boolean;
  mfa_activo: boolean;
  debe_cambiar_password: boolean;
  esta_bloqueado: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface UsuarioListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Usuario[];
}

export interface UsuarioCreatePayload {
  email: string;
  nombre_completo: string;
  rol: UserRole;
}

export interface UsuarioUpdatePayload {
  nombre_completo: string;
  rol: UserRole;
}

export interface UsuarioCreateResponse {
  usuario: Usuario;
  password_temporal: string;
}

export interface ResetPasswordResponse {
  password_temporal: string;
}
