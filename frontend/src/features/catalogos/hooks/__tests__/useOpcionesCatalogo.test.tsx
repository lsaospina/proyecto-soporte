import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useOpcionesCatalogo } from '../useOpcionesCatalogo';

vi.mock('../../api/catalogos.api', () => ({
  catalogosApi: {
    list: vi.fn(),
  },
}));
import { catalogosApi } from '../../api/catalogos.api';

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe('useOpcionesCatalogo', () => {
  beforeEach(() => vi.clearAllMocks());

  it('pide page_size=100 e is_active=true', async () => {
    (catalogosApi.list as any).mockResolvedValue({ results: [{ id: 1, nombre: 'A', is_active: true }] });
    const { result } = renderHook(() => useOpcionesCatalogo('sedes'), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(catalogosApi.list).toHaveBeenCalledWith('sedes', { page_size: 100, is_active: true });
  });

  it('devuelve solo activos', async () => {
    (catalogosApi.list as any).mockResolvedValue({ results: [{ id: 1, nombre: 'A', is_active: true }] });
    const { result } = renderHook(() => useOpcionesCatalogo('sedes'), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
  });

  it('incluye padre inactivo al editar', async () => {
    (catalogosApi.list as any)
      .mockResolvedValueOnce({ results: [{ id: 2, nombre: 'B', is_active: true }] })
      .mockResolvedValueOnce({ results: [{ id: 1, nombre: 'Inactivo', is_active: false }] });
    const { result } = renderHook(() => useOpcionesCatalogo('sedes', 1), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.some((x: any) => x.id === 1)).toBe(true);
  });
});
