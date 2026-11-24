import client from '../../../api/client';
import type { DashboardResumen } from '../types';

export const dashboardApi = {
  resumen: () =>
    client.get<DashboardResumen>('/api/v1/dashboard/resumen/').then((r) => r.data),
};
