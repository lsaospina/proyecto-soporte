import client from '../../../api/client';
import type {
  Asignacion,
  AsignacionPayload,
  CerrarPayload,
  Paginated,
  ReasignarPayload,
  ResumenAsignaciones,
  UsuarioAsignable,
} from '../types';

const BASE = '/api/v1/asignaciones';

export const asignacionesApi = {
  list: (params?: Record<string, unknown>) =>
    client.get<Paginated<Asignacion>>(`${BASE}/`, { params }).then((r) => r.data),
  resumen: () => client.get<ResumenAsignaciones>(`${BASE}/resumen/`).then((r) => r.data),
  usuarios: () => client.get<UsuarioAsignable[]>(`${BASE}/usuarios/`).then((r) => r.data),
  crear: (data: AsignacionPayload) =>
    client.post<Asignacion>(`${BASE}/`, data).then((r) => r.data),
  cerrar: (id: number, data: CerrarPayload) =>
    client.post<Asignacion>(`${BASE}/${id}/cerrar/`, data).then((r) => r.data),
  reasignar: (data: ReasignarPayload) =>
    client.post<Asignacion>(`${BASE}/reasignar/`, data).then((r) => r.data),
};
