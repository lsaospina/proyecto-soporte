import client from '../../../api/client';

const BASE = '/api/v1';

export const catalogosApi = {
  list: (resource: string, params?: Record<string, unknown>) =>
    client.get(`${BASE}/${resource}/`, { params }).then((r) => r.data),
  create: (resource: string, data: unknown) =>
    client.post(`${BASE}/${resource}/`, data).then((r) => r.data),
  update: (resource: string, id: number, data: unknown) =>
    client.patch(`${BASE}/${resource}/${id}/`, data).then((r) => r.data),
};
