import { render, screen, within } from '@testing-library/react';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

import { DashboardPage } from '../pages/DashboardPage';
import type { DashboardResumen } from '../types';

const authState = vi.hoisted(() => ({ rol: 'ADMINISTRADOR' }));

vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => ({ user: { id: 1, rol: authState.rol, nombre_completo: 'Admin Uno' } }),
}));

const activo = {
  id: 1,
  serial: 'SN-00001',
  codigo_qr: 'AST-2026-000001',
  marca: 'Dell',
  modelo: 'Latitude 5420',
  categoria: 'Computo',
  estado: 'ASIGNADO' as const,
  fecha_adquisicion: '2024-11-23',
};

const proximo = {
  id: 10,
  activo_serial: 'SN-00002',
  activo_codigo: 'AST-2026-000002',
  marca: 'Cisco',
  modelo: 'Switch 2960',
  tipo: 'PREVENTIVO' as const,
  fecha_programada: '2026-11-18',
  tecnico: 'Técnico Uno',
  observacion: '',
  dias_restantes: 3,
};

const vencido = {
  id: 11,
  activo_serial: 'SN-00007',
  activo_codigo: 'AST-2026-000007',
  marca: 'Lenovo',
  modelo: 'ThinkPad T14',
  tipo: 'PREVENTIVO' as const,
  fecha_programada: '2026-10-01',
  tecnico: null,
  observacion: '',
  dias_atraso: 45,
};

const correctivo = {
  id: 12,
  activo_serial: 'SN-00003',
  activo_codigo: 'AST-2026-000003',
  marca: 'HP',
  modelo: 'EliteBook 840',
  tipo: 'CORRECTIVO' as const,
  fecha_programada: '2026-11-10',
  tecnico: 'Técnico Dos',
  observacion: 'Se reemplazó el cable de pantalla.',
};

const resumenAdmin: DashboardResumen = {
  hoy: '2026-11-15',
  anio: 2026,
  activos: {
    total: 39,
    operativos: 19,
    en_mantenimiento: 10,
    dados_de_baja: 10,
    inactivos: 1,
    valor_total: '2850000.00',
    por_estado: [
      { estado: 'DISPONIBLE', etiqueta: 'Disponible', total: 9 },
      { estado: 'ASIGNADO', etiqueta: 'Asignado', total: 10 },
      { estado: 'EN_MANTENIMIENTO', etiqueta: 'En mantenimiento', total: 10 },
      { estado: 'DADO_DE_BAJA', etiqueta: 'Dado de baja', total: 10 },
    ],
    por_categoria: [
      { nombre: 'Computo', total: 12 },
      { nombre: 'Redes', total: 7 },
    ],
    por_marca: [
      { nombre: 'Dell', total: 6 },
      { nombre: 'HP', total: 6 },
    ],
    ultimas_adquisiciones: [activo],
  },
  mantenimientos: {
    preventivos_anio: {
      total: 32,
      agendados: 32,
      cancelados: 0,
      completados: 19,
      vencidos: 5,
      incumplidos: 3,
      pendientes: 5,
      porcentaje_cumplimiento: 59,
    },
    mensual: Array.from({ length: 12 }, (_, i) => ({
      mes: i + 1,
      agendados: i + 1 <= 11 ? 3 : 0,
      completados: i + 1 <= 11 ? 2 : 0,
      vencidos: i + 1 === 10 ? 1 : 0,
      incumplidos: i + 1 === 1 ? 1 : 0,
      porcentaje_cumplimiento: i + 1 <= 11 ? 67 : 0,
    })),
    proximos: [proximo],
    vencidos: [vencido],
    correctivos: {
      registrados_30_dias: 4,
      costo_30_dias: '450000.00',
      recientes: [correctivo],
    },
    activos_sin_preventivo: { total: 2, activos: [activo] },
    costo_anio: '2850000.00',
  },
};

const resumenResponsable: DashboardResumen = {
  ...resumenAdmin,
  activos: { ...resumenAdmin.activos, valor_total: null },
  mantenimientos: null,
};

let respuesta: DashboardResumen = resumenAdmin;

const server = setupServer(
  http.get(/\/api\/v1\/dashboard\/resumen\/$/, () => HttpResponse.json(respuesta)),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  respuesta = resumenAdmin;
  authState.rol = 'ADMINISTRADOR';
});
afterAll(() => server.close());

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('DashboardPage', () => {
  it('muestra los indicadores y paneles del inventario y mantenimiento', async () => {
    renderPage();

    expect(await screen.findByText('Activos vigentes')).toBeInTheDocument();
    expect(screen.getByText('39')).toBeInTheDocument();
    expect(screen.getByText('59%')).toBeInTheDocument();
    expect(screen.getByText('19 de 32 agendados en 2026')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Cumplimiento preventivo 2026' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Estado del inventario' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Próximos 14 días' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Atención inmediata' })).toBeInTheDocument();
    expect(screen.getByText('En 3 días')).toBeInTheDocument();
    expect(screen.getByText('45 días')).toBeInTheDocument();
    expect(screen.getByText(/Se reemplazó el cable de pantalla/)).toBeInTheDocument();
  });

  it('resume las alertas operativas', async () => {
    renderPage();
    expect(await screen.findByRole('alert')).toHaveTextContent(
      '5 mantenimientos preventivos vencidos',
    );
    expect(screen.getByText('3 servicios incumplidos')).toBeInTheDocument();
    expect(screen.getByText('1 servicio en los próximos 7 días')).toBeInTheDocument();
    expect(screen.getByText('2 activos sin preventivo en 2026')).toBeInTheDocument();
  });

  it('no incluye el botón de registrar activo', async () => {
    renderPage();
    await screen.findByText('Activos vigentes');
    expect(screen.queryByText(/registrar activo/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /registrar activo/i })).not.toBeInTheDocument();
  });

  it('ofrece accesos al inventario y a mantenimientos', async () => {
    renderPage();
    expect(await screen.findByRole('link', { name: 'Ver inventario' })).toHaveAttribute(
      'href',
      '/activos',
    );
    expect(screen.getByRole('link', { name: 'Mantenimientos' })).toHaveAttribute(
      'href',
      '/mantenimientos',
    );
  });

  it('el usuario responsable solo ve el inventario', async () => {
    authState.rol = 'USUARIO_RESPONSABLE';
    respuesta = resumenResponsable;
    renderPage();

    expect(await screen.findByText('Activos vigentes')).toBeInTheDocument();
    expect(screen.getByText('Dados de baja')).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: /Cumplimiento preventivo/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Atención inmediata' })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Mantenimientos' })).not.toBeInTheDocument();
    expect(screen.queryByText(/Valor del inventario/i)).not.toBeInTheDocument();
  });

  it('muestra el estado de error con reintento', async () => {
    server.use(
      http.get(/\/api\/v1\/dashboard\/resumen\/$/, () =>
        HttpResponse.json({ detail: 'Error interno' }, { status: 500 }),
      ),
    );
    renderPage();
    const alerta = await screen.findByRole('alert');
    expect(alerta).toHaveTextContent('No se pudo cargar el tablero.');
    expect(within(alerta).getByRole('button', { name: 'Reintentar' })).toBeInTheDocument();
  });
});
