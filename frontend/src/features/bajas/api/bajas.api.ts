import client from '../../../api/client';

const BASE = '/api/v1/bajas';

export interface Baja {
  id: number;
  activo: number;
  activo_serial: string;
  activo_codigo: string;
  marca_nombre: string;
  modelo_nombre: string;
  fecha: string;
  motivo: string;
  autorizado_por: number;
  autorizado_por_nombre: string;
  documento: number | null;
  documento_nombre: string | null;
  created_at: string;
  updated_at: string;
}

interface Paginated<T> {
  count: number;
  results: T[];
  next: string | null;
  previous: string | null;
}

export interface BajaPayload {
  activo: number;
  fecha?: string;
  motivo: string;
  documento?: number | null;
}

export const bajasApi = {
  list: (params?: Record<string, unknown>) =>
    client.get<Paginated<Baja>>(`${BASE}/`, { params }).then((r) => r.data),
  create: (data: BajaPayload) => client.post<Baja>(`${BASE}/`, data).then((r) => r.data),
};
