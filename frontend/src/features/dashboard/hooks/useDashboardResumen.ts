import { useQuery } from '@tanstack/react-query';

import { dashboardApi } from '../api/dashboard.api';

export function useDashboardResumen() {
  return useQuery({
    queryKey: ['dashboard', 'resumen'],
    queryFn: dashboardApi.resumen,
    staleTime: 60_000,
  });
}
