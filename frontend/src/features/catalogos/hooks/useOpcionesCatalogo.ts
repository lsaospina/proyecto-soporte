import { useQuery } from '@tanstack/react-query';
import { catalogosApi } from '../api/catalogos.api';

export function useOpcionesCatalogo(resource: string, currentId?: number | null) {
  return useQuery({
    queryKey: ['opciones', resource, currentId],
    queryFn: async () => {
      const activos = await catalogosApi.list(resource, { page_size: 100, is_active: true });
      const items = activos?.results ?? activos ?? [];
      if (currentId != null && !items.some((x: any) => x.id === currentId)) {
        try {
          const one = await catalogosApi.list(resource, { id: currentId });
          const found = (one?.results ?? one ?? []).find((x: any) => x.id === currentId);
          if (found) items.unshift(found);
        } catch {
          // ignore
        }
      }
      return items;
    },
  });
}
