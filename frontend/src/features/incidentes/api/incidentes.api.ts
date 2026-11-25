import client from '../../../api/client';

const BASE = '/api/v1/incidentes';

export const incidentesApi = {
  list: (params?: Record<string, unknown>) =>
    client.get(`${BASE}/`, { params }).then((r) => r.data),
};
