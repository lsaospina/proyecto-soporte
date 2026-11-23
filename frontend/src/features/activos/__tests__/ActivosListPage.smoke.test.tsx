import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { ActivosListPage } from '../pages/ActivosListPage';

vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => ({ user: { rol: 'ADMINISTRADOR' } }),
}));

vi.mock('../api/activos.api', () => ({
  activosApi: {
    list: vi.fn().mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          serial: 'SN1',
          modelo_nombre: 'Latitude',
          marca_nombre: 'Dell',
          categoria_nombre: 'HW',
          estado: 'DISPONIBLE',
          codigo_qr: 'AST-2024-000001',
          fecha_adquisicion: '2024-01-01',
          is_active: true,
        },
      ],
    }),
    inactivar: vi.fn(),
    reactivar: vi.fn(),
  },
}));

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <ActivosListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ActivosListPage smoke', () => {
  it('renders', async () => {
    renderPage();
    expect(await screen.findByText('SN1')).toBeInTheDocument();
  });
});
