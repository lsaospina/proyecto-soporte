import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

import { LicenciasPage } from '../pages/LicenciasPage';
import type { Licencia } from '../types';

function baseLicencia(id: number, overrides: Partial<Licencia> = {}): Licencia {
  return {
    id,
    proveedor: 1,
    proveedor_nombre: 'Microsoft',
    servicio: 'Microsoft 365 Familia',
    periodicidad: 'ANUAL',
    fecha_renovacion: '2026-12-14',
    cantidad: 6,
    valor: '459999.00',
    renovacion_automatica: true,
    medio_pago: 'Facturación electrónica',
    cuenta_vinculada: 'admin@empresa.com',
    responsable_uso: 'Equipo administrativo',
    observacion: '',
    is_active: true,
    dias_para_renovacion: 29,
    estado_renovacion: 'POR_VENCER',
    estado_renovacion_etiqueta: 'Por vencer',
    created_at: '2026-11-01T10:00:00Z',
    updated_at: '2026-11-01T10:00:00Z',
    ...overrides,
  };
}

const resumen = {
  hoy: '2026-11-15',
  total: 3,
  activas: 2,
  inactivas: 1,
  por_vencer: 1,
  vencidas: 4,
  renovacion_automatica: 1,
  costo_anual_estimado: '21229344.50',
  costo_por_vencer: '7206614.00',
  por_periodicidad: [{ periodicidad: 'ANUAL', total: 2 }],
  por_proveedor: [{ nombre: 'Microsoft', total: 2 }],
};

let resultados: Licencia[] = [baseLicencia(1)];
const listParams: URLSearchParams[] = [];
let renovarBody: Record<string, unknown> | null = null;
let inactivarLlamado = false;

const server = setupServer(
  http.get(/\/api\/v1\/licencias\/resumen\/$/, () => HttpResponse.json(resumen)),
  http.get(/\/api\/v1\/licencias\/proveedores\/$/, () =>
    HttpResponse.json([
      { id: 1, nombre: 'Microsoft' },
      { id: 2, nombre: 'Google' },
    ]),
  ),
  http.get(/\/api\/v1\/licencias\/$/, ({ request }) => {
    listParams.push(new URL(request.url).searchParams);
    return HttpResponse.json({
      count: resultados.length,
      next: null,
      previous: null,
      results: resultados,
      hoy: '2026-11-15',
    });
  }),
  http.post(/\/api\/v1\/licencias\/(\d+)\/renovar\/$/, async ({ request, params }) => {
    renovarBody = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json(
      baseLicencia(Number(params[0]), {
        fecha_renovacion: '2027-12-14',
        dias_para_renovacion: 394,
        estado_renovacion: 'VIGENTE',
        estado_renovacion_etiqueta: 'Vigente',
      }),
    );
  }),
  http.post(/\/api\/v1\/licencias\/(\d+)\/inactivar\/$/, () => {
    inactivarLlamado = true;
    return HttpResponse.json(
      baseLicencia(1, {
        is_active: false,
        estado_renovacion: 'INACTIVA',
        estado_renovacion_etiqueta: 'Inactiva',
      }),
    );
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  resultados = [baseLicencia(1)];
  listParams.length = 0;
  renovarBody = null;
  inactivarLlamado = false;
});
afterAll(() => server.close());

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <LicenciasPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('LicenciasPage', () => {
  it('muestra KPIs, alertas y licencias', async () => {
    renderPage();

    expect(await screen.findByText('Microsoft 365 Familia')).toBeInTheDocument();
    expect(screen.getByText('Licencias activas')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent('4 licencias vencidas requieren gestión');
    expect(screen.getByText('En 29 días')).toBeInTheDocument();
    expect(screen.getByText(/21\.229\.34/)).toBeInTheDocument();
  });

  it('filtra por estado y proveedor', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('Microsoft 365 Familia');

    await user.click(screen.getByRole('button', { name: 'Vencidas' }));
    await waitFor(() => {
      expect(listParams.at(-1)?.get('estado_renovacion')).toBe('VENCIDA');
    });

    await user.selectOptions(screen.getByLabelText('Filtrar por proveedor'), '2');
    await waitFor(() => {
      expect(listParams.at(-1)?.get('proveedor')).toBe('2');
    });
  });

  it('renueva una licencia desde el diálogo', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('Microsoft 365 Familia');

    await user.click(screen.getByRole('button', { name: 'Renovar' }));
    const dialog = await screen.findByRole('dialog', { name: 'Renovar licencia' });
    await user.click(within(dialog).getByRole('button', { name: 'Renovar' }));

    expect(await screen.findByText('Licencia renovada.')).toBeInTheDocument();
    expect(renovarBody?.valor).toBe('459999.00');
    expect(String(renovarBody?.fecha_renovacion)).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it('inactiva una licencia con confirmación', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('Microsoft 365 Familia');

    await user.click(screen.getByRole('button', { name: 'Inactivar' }));
    const dialog = await screen.findByRole('dialog', { name: 'Inactivar licencia' });
    await user.click(within(dialog).getByRole('button', { name: 'Inactivar' }));

    expect(await screen.findByText('Licencia inactivada.')).toBeInTheDocument();
    expect(inactivarLlamado).toBe(true);
  });

  it('muestra estado vacío', async () => {
    resultados = [];
    renderPage();
    expect(await screen.findByText('Sin licencias registradas')).toBeInTheDocument();
  });

  it('muestra el error de carga con reintento', async () => {
    server.use(
      http.get(/\/api\/v1\/licencias\/$/, () =>
        HttpResponse.json({ detail: 'Error' }, { status: 500 }),
      ),
    );
    renderPage();
    expect(await screen.findByText('No se pudieron cargar las licencias.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reintentar' })).toBeInTheDocument();
  });
});
