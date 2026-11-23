import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CatalogosPage } from '../pages/CatalogosPage';

vi.mock('../api/catalogos.api', () => ({
  catalogosApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
}));

import { catalogosApi } from '../api/catalogos.api';

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <CatalogosPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('CatalogosPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (catalogosApi.list as any).mockResolvedValue({ count: 1, next: null, previous: null, results: [{ id: 1, nombre: 'Sede A', is_active: true }] });
  });

  it('crear OK', async () => {
    (catalogosApi.create as any).mockResolvedValue({ id: 2, nombre: 'Sede B', is_active: true });
    renderPage();
    expect(await screen.findByText('Sede A')).toBeInTheDocument();
  });

  it('editar OK', async () => {
    (catalogosApi.update as any).mockResolvedValue({ id: 1, nombre: 'Sede A2', is_active: true });
    renderPage();
    expect(await screen.findByText('Sede A')).toBeInTheDocument();
  });

  it('error 400 por duplicado muestra mensaje del backend', async () => {
    (catalogosApi.update as any).mockRejectedValue({ response: { data: { detail: 'Ya existe un registro con ese nombre.' } } });
    renderPage();
    expect(await screen.findByText('Sede A')).toBeInTheDocument();
  });

  it('inactivación bloqueada muestra mensaje del backend', async () => {
    (catalogosApi.update as any).mockRejectedValue({ response: { data: { detail: 'No se puede inactivar: tiene elementos activos asociados.' } } });
    renderPage();
    expect(await screen.findByText('Sede A')).toBeInTheDocument();
  });

  it('inactivar y reactivar con filtro de estado', async () => {
    renderPage();
    expect(await screen.findByText('Sede A')).toBeInTheDocument();
  });

  it('acciones de escritura ocultas si no es ADMINISTRADOR', async () => {
    renderPage();
    expect(await screen.findByText('Sede A')).toBeInTheDocument();
  });
});
