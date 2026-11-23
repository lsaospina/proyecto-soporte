import client from '../../../api/client';

const BASE = '/api/v1';

export const activosApi = {
  list: (params?: Record<string, unknown>) =>
    client.get(`${BASE}/activos/`, { params }).then((r) => r.data),
  create: (data: unknown) =>
    client.post(`${BASE}/activos/`, data).then((r) => r.data),
  update: (id: number, data: unknown) =>
    client.patch(`${BASE}/activos/${id}/`, data).then((r) => r.data),
  retrieve: (id: number) =>
    client.get(`${BASE}/activos/${id}/`).then((r) => r.data),
  inactivar: (id: number) =>
    client.post(`${BASE}/activos/${id}/inactivar/`).then((r) => r.data),
  reactivar: (id: number) =>
    client.post(`${BASE}/activos/${id}/reactivar/`).then((r) => r.data),
  historial: (id: number) =>
    client.get(`${BASE}/activos/${id}/historial/`).then((r) => r.data),
};