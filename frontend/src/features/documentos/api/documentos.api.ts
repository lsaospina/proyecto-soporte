import client from '../../../api/client';

const BASE = '/api/v1/documentos';

export interface Documento {
  id: number;
  activo: number;
  activo_serial: string;
  nombre: string;
  tipo: string;
  tipo_etiqueta: string;
  descripcion: string;
  subido_por: number;
  subido_por_nombre: string;
  archivo_nombre: string | null;
  created_at: string;
  updated_at: string;
}

interface Paginated<T> {
  count: number;
  results: T[];
}

export const documentosApi = {
  list: (params?: Record<string, unknown>) =>
    client.get<Paginated<Documento>>(`${BASE}/`, { params }).then((r) => r.data),
  create: (data: FormData) =>
    client.post<Documento>(`${BASE}/`, data).then((r) => r.data),
  remove: (id: number) => client.delete(`${BASE}/${id}/`).then((r) => r.data),
  descargar: (id: number) =>
    client.get(`${BASE}/${id}/descargar/`, { responseType: 'blob' }).then((r) => r.data as Blob),
};
