import client from '../../../api/client';
import type {
  ResetPasswordResponse,
  Usuario,
  UsuarioCreatePayload,
  UsuarioCreateResponse,
  UsuarioListResponse,
  UsuarioUpdatePayload,
} from '../types';

export interface ListUsuariosParams {
  page?: number;
  rol?: string;
  is_active?: string;
  search?: string;
}

export async function listUsuarios(params: ListUsuariosParams = {}): Promise<UsuarioListResponse> {
  const response = await client.get<UsuarioListResponse>('/api/v1/usuarios/', { params });
  return response.data;
}

export async function getUsuario(id: number): Promise<Usuario> {
  const response = await client.get<Usuario>(`/api/v1/usuarios/${id}/`);
  return response.data;
}

export async function createUsuario(payload: UsuarioCreatePayload): Promise<UsuarioCreateResponse> {
  const response = await client.post<UsuarioCreateResponse>('/api/v1/usuarios/', payload);
  return response.data;
}

export async function updateUsuario(
  id: number,
  payload: UsuarioUpdatePayload,
): Promise<Usuario> {
  const response = await client.patch<Usuario>(`/api/v1/usuarios/${id}/`, payload);
  return response.data;
}

export async function resetPassword(id: number): Promise<ResetPasswordResponse> {
  const response = await client.post<ResetPasswordResponse>(`/api/v1/usuarios/${id}/reset_password/`);
  return response.data;
}

export async function resetMfa(id: number): Promise<void> {
  await client.post(`/api/v1/usuarios/${id}/reset_mfa/`);
}

export async function activarUsuario(id: number): Promise<Usuario> {
  const response = await client.post<Usuario>(`/api/v1/usuarios/${id}/activar/`);
  return response.data;
}

export async function desactivarUsuario(id: number): Promise<Usuario> {
  const response = await client.post<Usuario>(`/api/v1/usuarios/${id}/desactivar/`);
  return response.data;
}
