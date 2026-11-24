import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, afterEach, beforeAll, afterAll } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { ActivosListPage } from '../pages/ActivosListPage';

const authState = vi.hoisted(() => ({ rol: 'ADMINISTRADOR' }));

vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => ({ user: { rol: authState.rol } }),
}));

const activo = {
  id: 1,
  serial: 'SN1',
  codigo_qr: 'AST-2024-000001',
  marca_nombre: 'Dell',
  modelo_nombre: 'Latitude',
  categoria_nombre: 'Portátiles',
  estado: 'DISPONIBLE',
  is_active: true,
};

const inactivo = { ...activo, id: 2, serial: 'SN2', codigo_qr: 'AST-2024-000002', is_active: false };

const requests: URLSearchParams[] = [];

const server = setupServer(
  http.get(/\/api\/v1\/activos\/$/, ({ request }) => {
    requests.push(new URL(request.url).searchParams);
    return HttpResponse.json({ count: 2, next: null, previous: null, results: [activo, inactivo] });
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  requests.length = 0;
  authState.rol = 'ADMINISTRADOR';
});
afterAll(() => server.close());

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

describe('ActivosListPage', () => {
  it('carga', async () => {
    renderPage();
    expect(await screen.findByText('SN1')).toBeInTheDocument();
    expect(screen.getAllByText('Dell / Latitude').length).toBeGreaterThan(0);
  });

  it('vacío', async () => {
    server.use(
      http.get(/\/api\/v1\/activos\/$/, () =>
        HttpResponse.json({ count: 0, next: null, previous: null, results: [] }),
      ),
    );
    renderPage();
    expect(await screen.findByText('Serial')).toBeInTheDocument();
    expect(screen.queryByText('SN1')).not.toBeInTheDocument();
  });

  it('error', async () => {
    server.use(
      http.get(/\/api\/v1\/activos\/$/, () =>
        HttpResponse.json({ detail: 'Error' }, { status: 500 }),
      ),
    );
    renderPage();
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudieron cargar los activos.');
  });

  it('búsqueda y filtro de estado envían los parámetros correctos', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('SN1');

    await user.type(screen.getByPlaceholderText(/Buscar serial/), 'SN1');
    await waitFor(() => expect(requests[requests.length - 1]?.get('search')).toBe('SN1'));
    expect(requests[requests.length - 1]?.get('is_active')).toBe('true');

    await user.click(screen.getByRole('button', { name: 'inactivos' }));
    await waitFor(() => expect(requests[requests.length - 1]?.get('is_active')).toBe('false'));
    expect(requests[requests.length - 1]?.get('search')).toBe('SN1');
  });

  it('TECNICO no ve Inactivar/Reactivar', async () => {
    authState.rol = 'TECNICO';
    renderPage();
    await screen.findByText('SN1');
    expect(screen.queryByRole('button', { name: 'Inactivar' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Reactivar' })).not.toBeInTheDocument();
  });

  it('ADMINISTRADOR ve Inactivar/Reactivar', async () => {
    authState.rol = 'ADMINISTRADOR';
    renderPage();
    await screen.findByText('SN1');
    expect(screen.getByRole('button', { name: 'Inactivar' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reactivar' })).toBeInTheDocument();
  });
});
