import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeAll, afterAll, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { MantenimientosPage } from '../pages/MantenimientosPage';

const authState = vi.hoisted(() => ({ rol: 'ADMINISTRADOR' }));

vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => ({ user: { id: 7, rol: authState.rol, nombre_completo: 'Técnico Siete' } }),
}));

const hoy = '2026-11-15';

function baseMantenimiento(id: number, overrides: Record<string, unknown> = {}) {
  return {
    id,
    activo: 1,
    activo_serial: `SN${id}`,
    activo_codigo: `AST-2026-00000${id}`,
    marca_nombre: 'Dell',
    modelo_nombre: 'Latitude',
    categoria_nombre: 'Portátiles',
    tipo: 'PREVENTIVO',
    fecha_programada: '2026-11-20',
    fecha_realizacion: null,
    tecnico: null,
    tecnico_nombre: null,
    costo: null,
    observacion: '',
    motivo_cancelacion: '',
    estado: 'PROGRAMADO',
    situacion: 'PENDIENTE',
    es_evidencia: false,
    reprogramado_como: null,
    reprogramacion_de: null,
    created_at: '2026-11-01T10:00:00Z',
    updated_at: '2026-11-01T10:00:00Z',
    ...overrides,
  };
}

const pendiente = baseMantenimiento(1);
const vencido = baseMantenimiento(2, { situacion: 'VENCIDO', fecha_programada: '2026-11-10' });
const incumplido = baseMantenimiento(3, {
  situacion: 'INCUMPLIDO',
  es_evidencia: true,
  fecha_programada: '2026-11-05',
  reprogramado_como: 4,
});
const reprogramado = baseMantenimiento(4, {
  fecha_programada: '2026-12-10',
  reprogramacion_de: 3,
});
const correctivo = baseMantenimiento(10, {
  tipo: 'CORRECTIVO',
  estado: 'COMPLETADO',
  situacion: 'COMPLETADO',
  observacion: 'No enciende; se cambió la fuente.',
  fecha_programada: '2026-11-10',
  fecha_realizacion: '2026-11-10',
  fecha_seguimiento: '2026-12-01',
});

const resumen = {
  anio: 2026,
  hoy,
  meses: Array.from({ length: 12 }, (_, i) => ({
    mes: i + 1,
    agendados: i === 10 ? 3 : 0,
    completados: i === 10 ? 1 : 0,
    vencidos: i === 10 ? 1 : 0,
    incumplidos: i === 10 ? 1 : 0,
    porcentaje_cumplimiento: i === 10 ? 33 : 0,
  })),
};

let calendarioMantenimientos = [pendiente, vencido, incumplido];
let reprogramarStatus = 201;
let programadoBody: any = null;
let correctivoBody: any = null;
let canceladoBody: any = null;
const listParams: URLSearchParams[] = [];
const activosParams: URLSearchParams[] = [];

const server = setupServer(
  http.get(/\/api\/v1\/mantenimientos\/resumen\/$/, () => HttpResponse.json(resumen)),
  http.get(/\/api\/v1\/mantenimientos\/calendario\/$/, () =>
    HttpResponse.json({
      anio: 2026,
      mes: 11,
      hoy,
      mantenimientos: calendarioMantenimientos,
    }),
  ),
  http.get(/\/api\/v1\/mantenimientos\/tecnicos\/$/, () =>
    HttpResponse.json([{ id: 7, nombre_completo: 'Técnico Siete' }]),
  ),
  http.get(/\/api\/v1\/mantenimientos\/$/, ({ request }) => {
    const params = new URL(request.url).searchParams;
    listParams.push(params);
    const esCorrectivo = params.get('tipo') === 'CORRECTIVO';
    return HttpResponse.json({
      count: 1,
      next: null,
      previous: null,
      hoy,
      results: esCorrectivo ? [correctivo] : [pendiente],
    });
  }),
  http.get(/\/api\/v1\/mantenimientos\/(\d+)\/historial\/$/, () => HttpResponse.json([])),
  http.get(/\/api\/v1\/mantenimientos\/(\d+)\/$/, ({ params }) => {
    const id = Number(params[0]);
    const encontrado = [pendiente, vencido, incumplido, reprogramado].find((m) => m.id === id);
    return HttpResponse.json(encontrado ?? pendiente);
  }),
  http.post(/\/api\/v1\/mantenimientos\/$/, async ({ request }) => {
    programadoBody = await request.json();
    return HttpResponse.json(baseMantenimiento(9), { status: 201 });
  }),
  http.post(/\/api\/v1\/mantenimientos\/correctivos\/$/, async ({ request }) => {
    correctivoBody = await request.json();
    return HttpResponse.json(correctivo, { status: 201 });
  }),
  http.post(/\/api\/v1\/mantenimientos\/(\d+)\/completar\/$/, () =>
    HttpResponse.json(baseMantenimiento(1, { situacion: 'COMPLETADO' })),
  ),
  http.post(/\/api\/v1\/mantenimientos\/(\d+)\/reprogramar\/$/, () =>
    HttpResponse.json(reprogramado, { status: reprogramarStatus }),
  ),
  http.post(/\/api\/v1\/mantenimientos\/(\d+)\/cancelar\/$/, async ({ request }) => {
    canceladoBody = await request.json();
    return HttpResponse.json(baseMantenimiento(2, { situacion: 'CANCELADO' }));
  }),
  http.get(/\/api\/v1\/activos\/$/, ({ request }) => {
    activosParams.push(new URL(request.url).searchParams);
    return HttpResponse.json({
      count: 1,
      next: null,
      previous: null,
      results: [{ id: 9, serial: 'SN9', codigo_qr: 'AST-2026-000009' }],
    });
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  calendarioMantenimientos = [pendiente, vencido, incumplido];
  reprogramarStatus = 201;
  programadoBody = null;
  correctivoBody = null;
  canceladoBody = null;
  listParams.length = 0;
  activosParams.length = 0;
  authState.rol = 'ADMINISTRADOR';
});
afterAll(() => server.close());

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <MantenimientosPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

async function abrirDetalle(codigo: string, situacion: string) {
  const chip = await screen.findByRole('button', { name: `${codigo} ${situacion}` });
  await userEvent.setup().click(chip);
  return screen.findByRole('heading', { name: new RegExp(codigo) });
}

describe('MantenimientosPage', () => {
  it('carga calendario y resumen', async () => {
    renderPage();
    expect(
      await screen.findByRole('button', { name: 'AST-2026-000001 Pendiente' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Mes Noviembre' })).toHaveTextContent('33% avance');
    expect(screen.getByRole('grid', { name: 'Calendario mensual' })).toBeInTheDocument();
  });

  it('mes vacío', async () => {
    calendarioMantenimientos = [];
    renderPage();
    expect(
      await screen.findByText('Sin mantenimientos programados en este mes.'),
    ).toBeInTheDocument();
  });

  it('error del calendario', async () => {
    server.use(
      http.get(/\/api\/v1\/mantenimientos\/calendario\/$/, () =>
        HttpResponse.json({ detail: 'Error' }, { status: 500 }),
      ),
    );
    renderPage();
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo cargar el calendario.');
  });

  it('chips por situación', async () => {
    renderPage();
    expect(
      await screen.findByRole('button', { name: 'AST-2026-000001 Pendiente' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'AST-2026-000002 Vencido' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'AST-2026-000003 Incumplido' })).toBeInTheDocument();
    expect(screen.getByText('Evidencia')).toBeInTheDocument();
  });

  it('programa desde un día vacío', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(await screen.findByRole('button', { name: 'Programar 2026-11-16' }));
    const dialog = await screen.findByRole('dialog');
    await within(dialog).findByRole('option', { name: /AST-2026-000009/ });
    await user.selectOptions(within(dialog).getByLabelText(/^Equipo\*/), '9');
    const paramsActivos = activosParams[activosParams.length - 1];
    expect(paramsActivos?.get('is_active')).toBe('true');
    expect(paramsActivos?.get('estado_no')).toBe('DADO_DE_BAJA');
    await user.click(within(dialog).getByRole('button', { name: 'Programar' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Mantenimiento programado.');
    expect(programadoBody?.activo).toBe(9);
    expect(programadoBody?.fecha_programada).toBe('2026-11-16');
  });

  it('TECNICO no ve Cancelar y un vencido ofrece Completar y Reprogramar', async () => {
    authState.rol = 'TECNICO';
    renderPage();
    await abrirDetalle('AST-2026-000002', 'Vencido');
    expect(screen.getByRole('button', { name: 'Completar' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reprogramar' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Cancelar' })).not.toBeInTheDocument();
  });

  it('ADMINISTRADOR ve Cancelar en un vencido', async () => {
    renderPage();
    await abrirDetalle('AST-2026-000002', 'Vencido');
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeInTheDocument();
  });

  it('reprogramar vencido crea un registro nuevo (201)', async () => {
    const user = userEvent.setup();
    renderPage();
    await abrirDetalle('AST-2026-000002', 'Vencido');
    await user.click(screen.getByRole('button', { name: 'Reprogramar' }));
    const dialog = await screen.findByRole('dialog');
    expect(within(dialog).getByRole('note')).toHaveTextContent('quedará como evidencia');
    fireEvent.change(within(dialog).getByLabelText(/Nueva fecha/), {
      target: { value: '2026-12-10' },
    });
    await user.click(within(dialog).getByRole('button', { name: 'Reprogramar' }));
    expect(await screen.findByRole('status')).toHaveTextContent(
      'Se creó un nuevo registro; el original queda como evidencia.',
    );
  });

  it('reprogramar pendiente mueve el registro (200)', async () => {
    const user = userEvent.setup();
    reprogramarStatus = 200;
    renderPage();
    await abrirDetalle('AST-2026-000001', 'Pendiente');
    await user.click(screen.getByRole('button', { name: 'Reprogramar' }));
    const dialog = await screen.findByRole('dialog');
    fireEvent.change(within(dialog).getByLabelText(/Nueva fecha/), {
      target: { value: '2026-11-25' },
    });
    await user.click(within(dialog).getByRole('button', { name: 'Reprogramar' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Mantenimiento reprogramado.');
  });

  it('INCUMPLIDO solo muestra el enlace a la reprogramación', async () => {
    renderPage();
    await abrirDetalle('AST-2026-000003', 'Incumplido');
    expect(screen.getByRole('button', { name: 'Ver reprogramación' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Reprogramar' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Completar' })).not.toBeInTheDocument();
  });

  it('cancelar envía el motivo', async () => {
    const user = userEvent.setup();
    renderPage();
    await abrirDetalle('AST-2026-000002', 'Vencido');
    await user.click(screen.getByRole('button', { name: 'Cancelar' }));
    const dialog = await screen.findByRole('dialog');
    await user.type(within(dialog).getByLabelText(/Motivo/), 'Equipo retirado');
    await user.click(within(dialog).getByRole('button', { name: 'Cancelar mantenimiento' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Mantenimiento cancelado.');
    expect(canceladoBody?.motivo).toBe('Equipo retirado');
  });

  it('la lista envía búsqueda, situación y mes', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(await screen.findByRole('tab', { name: 'Lista' }));
    await user.type(screen.getByPlaceholderText(/Buscar serial/), 'SN1');
    await waitFor(() => expect(listParams[listParams.length - 1]?.get('search')).toBe('SN1'));
    expect(listParams[listParams.length - 1]?.get('tipo')).toBe('PREVENTIVO');
    await user.selectOptions(screen.getByLabelText('Filtrar por situación'), 'VENCIDO');
    await waitFor(() => expect(listParams[listParams.length - 1]?.get('situacion')).toBe('VENCIDO'));
  });

  it('la pestaña Correctivos lista los registros correctivos', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(await screen.findByRole('tab', { name: 'Correctivos' }));
    expect(await screen.findByText('No enciende; se cambió la fuente.')).toBeInTheDocument();
    expect(listParams[listParams.length - 1]?.get('tipo')).toBe('CORRECTIVO');
  });

  it('registra un correctivo con equipo, descripción y seguimiento', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(await screen.findByRole('tab', { name: 'Correctivos' }));
    await user.click(await screen.findByRole('button', { name: 'Registrar correctivo' }));
    const dialog = await screen.findByRole('dialog');
    await within(dialog).findByRole('option', { name: /AST-2026-000009/ });
    await user.selectOptions(within(dialog).getByLabelText(/^Equipo\*/), '9');
    const paramsActivos = activosParams[activosParams.length - 1];
    expect(paramsActivos?.get('is_active')).toBe('true');
    expect(paramsActivos?.get('estado_no')).toBe('DADO_DE_BAJA');
    await user.type(within(dialog).getByLabelText(/¿Qué pasó/), 'No enciende');
    fireEvent.change(within(dialog).getByLabelText(/Fecha de seguimiento/), {
      target: { value: '2026-12-01' },
    });
    await user.click(within(dialog).getByRole('button', { name: 'Registrar' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Correctivo registrado.');
    expect(correctivoBody?.activo).toBe(9);
    expect(correctivoBody?.observacion).toBe('No enciende');
    expect(correctivoBody?.fecha_seguimiento).toBe('2026-12-01');
    expect(correctivoBody?.tecnico).toBe(7);
  });

  it('el correctivo exige equipo y descripción', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(await screen.findByRole('tab', { name: 'Correctivos' }));
    await user.click(await screen.findByRole('button', { name: 'Registrar correctivo' }));
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Registrar' }));
    expect(await within(dialog).findByText('El equipo es obligatorio')).toBeInTheDocument();
    expect(within(dialog).getByText('Describa qué pasó')).toBeInTheDocument();
    expect(correctivoBody).toBeNull();
  });
});
