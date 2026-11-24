import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

import { AsignacionesPage } from '../pages/AsignacionesPage';
import type { Asignacion } from '../types';

const authState = vi.hoisted(() => ({ rol: 'ADMINISTRADOR' }));

vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => ({ user: { id: 1, rol: authState.rol, nombre_completo: 'Admin Uno' } }),
}));

function baseAsignacion(id: number, overrides: Partial<Asignacion> = {}): Asignacion {
  return {
    id,
    activo: 10,
    activo_serial: 'SN-00010',
    activo_codigo: 'AST-2026-000010',
    marca_nombre: 'Dell',
    modelo_nombre: 'Latitude 5420',
    categoria_nombre: 'Computo',
    usuario: 2,
    usuario_nombre: 'Ana Perez',
    usuario_email: 'ana@empresa.com',
    asignado_por: 1,
    asignado_por_nombre: 'Admin Uno',
    fecha_inicio: '2026-11-01',
    fecha_fin: null,
    activa: true,
    dias_asignado: 22,
    observacion: 'Acta de entrega',
    created_at: '2026-11-01T10:00:00Z',
    updated_at: '2026-11-01T10:00:00Z',
    ...overrides,
  };
}

const resumen = {
  hoy: '2026-11-23',
  activos_operativos: 29,
  asignados: 14,
  disponibles: 5,
  en_mantenimiento: 10,
  colaboradores: 3,
  asignaciones_historicas: 18,
};

let resultados: Asignacion[] = [baseAsignacion(1)];
const listParams: URLSearchParams[] = [];
let crearBody: Record<string, unknown> | null = null;
let reasignarBody: Record<string, unknown> | null = null;
let cerrarBody: Record<string, unknown> | null = null;

const server = setupServer(
  http.get(/\/api\/v1\/asignaciones\/resumen\/$/, () => HttpResponse.json(resumen)),
  http.get(/\/api\/v1\/asignaciones\/usuarios\/$/, () =>
    HttpResponse.json([
      { id: 2, nombre_completo: 'Ana Perez', email: 'ana@empresa.com', rol: 'USUARIO_RESPONSABLE' },
      { id: 3, nombre_completo: 'Luis Gomez', email: 'luis@empresa.com', rol: 'USUARIO_RESPONSABLE' },
    ]),
  ),
  http.get(/\/api\/v1\/activos\/$/, () =>
    HttpResponse.json({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 10,
          serial: 'SN-00010',
          codigo_qr: 'AST-2026-000010',
          marca_nombre: 'Dell',
          modelo_nombre: 'Latitude 5420',
          categoria_nombre: 'Computo',
          estado: 'DISPONIBLE',
          is_active: true,
        },
      ],
    }),
  ),
  http.get(/\/api\/v1\/asignaciones\/$/, ({ request }) => {
    listParams.push(new URL(request.url).searchParams);
    return HttpResponse.json({
      count: resultados.length,
      next: null,
      previous: null,
      results: resultados,
    });
  }),
  http.post(/\/api\/v1\/asignaciones\/reasignar\/$/, async ({ request }) => {
    reasignarBody = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json(baseAsignacion(9, { usuario: 3, usuario_nombre: 'Luis Gomez' }), {
      status: 201,
    });
  }),
  http.post(/\/api\/v1\/asignaciones\/(\d+)\/cerrar\/$/, async ({ request }) => {
    cerrarBody = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json(baseAsignacion(1, { fecha_fin: '2026-11-23', activa: false }));
  }),
  http.post(/\/api\/v1\/asignaciones\/$/, async ({ request }) => {
    crearBody = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json(baseAsignacion(11), { status: 201 });
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  resultados = [baseAsignacion(1)];
  listParams.length = 0;
  crearBody = null;
  reasignarBody = null;
  cerrarBody = null;
  authState.rol = 'ADMINISTRADOR';
});
afterAll(() => server.close());

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <AsignacionesPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AsignacionesPage', () => {
  it('muestra KPIs, asignaciones activas y su responsable', async () => {
    renderPage();
    expect(await screen.findByText('AST-2026-000010')).toBeInTheDocument();
    expect(screen.getByText('Equipos asignados')).toBeInTheDocument();
    expect(screen.getByText('14')).toBeInTheDocument();
    expect(screen.getByText('Ana Perez')).toBeInTheDocument();
    expect(screen.getByText('Actual')).toBeInTheDocument();
    expect(screen.getByText('22 días')).toBeInTheDocument();
  });

  it('filtra el historial con abierta=false', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('AST-2026-000010');
    await user.click(screen.getByRole('button', { name: 'Historial' }));
    await waitFor(() => {
      expect(listParams.at(-1)?.get('abierta')).toBe('false');
    });
  });

  it('crea una asignación desde el diálogo', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('AST-2026-000010');

    await user.click(screen.getByRole('button', { name: 'Nueva asignación' }));
    const dialog = await screen.findByRole('dialog', { name: 'Nueva asignación' });
    await waitFor(() => {
      expect(within(dialog).getByRole('option', { name: /AST-2026-000010/ })).toBeInTheDocument();
    });
    await user.selectOptions(within(dialog).getByLabelText(/^Equipo/), '10');
    await user.selectOptions(within(dialog).getByLabelText(/^Colaborador/), '3');
    await user.click(within(dialog).getByRole('button', { name: 'Asignar' }));

    expect(await screen.findByText('Equipo asignado.')).toBeInTheDocument();
    expect(crearBody).toMatchObject({ activo: 10, usuario: 3 });
  });

  it('reasigna un equipo activo', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('AST-2026-000010');

    await user.click(screen.getByRole('button', { name: 'Reasignar' }));
    const dialog = await screen.findByRole('dialog', { name: 'Reasignar activo' });
    await user.selectOptions(within(dialog).getByLabelText(/^Colaborador/), '3');
    await user.click(within(dialog).getByRole('button', { name: 'Reasignar' }));

    expect(await screen.findByText('Equipo reasignado.')).toBeInTheDocument();
    expect(reasignarBody).toMatchObject({ activo: 10, usuario: 3 });
  });

  it('registra la devolución de un equipo', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText('AST-2026-000010');

    await user.click(screen.getByRole('button', { name: 'Devolver' }));
    const dialog = await screen.findByRole('dialog', { name: 'Registrar devolución' });
    await user.click(within(dialog).getByRole('button', { name: 'Registrar devolución' }));

    expect(await screen.findByText('Devolución registrada.')).toBeInTheDocument();
    expect(String(cerrarBody?.fecha_fin)).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it('el técnico solo puede consultar', async () => {
    authState.rol = 'TECNICO';
    renderPage();
    await screen.findByText('AST-2026-000010');
    expect(screen.queryByRole('button', { name: 'Nueva asignación' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Reasignar' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Devolver' })).not.toBeInTheDocument();
  });

  it('muestra el error de carga', async () => {
    server.use(
      http.get(/\/api\/v1\/asignaciones\/$/, () =>
        HttpResponse.json({ detail: 'Error' }, { status: 500 }),
      ),
    );
    renderPage();
    expect(
      await screen.findByText('No se pudieron cargar las asignaciones.'),
    ).toBeInTheDocument();
  });
});
