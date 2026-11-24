import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, beforeAll, afterAll } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import App from './App';

let rol = 'ADMINISTRADOR';

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

const mantenimiento = {
  id: 1,
  activo: 1,
  activo_serial: 'SN1',
  activo_codigo: 'AST-2026-000001',
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
};

const server = setupServer(
  http.get(/\/api\/v1\/auth\/me\/$/, () =>
    HttpResponse.json({
      id: 1,
      email: 'usuario@test.com',
      nombre_completo: 'Usuario Test',
      rol,
      mfa_activo: true,
    }),
  ),
  http.get(/\/api\/v1\/activos\/$/, () =>
    HttpResponse.json({ count: 1, next: null, previous: null, results: [activo] }),
  ),
  http.get(/\/api\/v1\/mantenimientos\/resumen\/$/, () =>
    HttpResponse.json({
      anio: 2026,
      hoy: '2026-11-15',
      meses: Array.from({ length: 12 }, (_, i) => ({
        mes: i + 1,
        agendados: i === 10 ? 1 : 0,
        completados: 0,
        vencidos: 0,
        incumplidos: 0,
        porcentaje_cumplimiento: 0,
      })),
    }),
  ),
  http.get(/\/api\/v1\/mantenimientos\/calendario\/$/, () =>
    HttpResponse.json({
      anio: 2026,
      mes: 11,
      hoy: '2026-11-15',
      mantenimientos: [mantenimiento],
    }),
  ),
  http.get(/\/api\/v1\/mantenimientos\/tecnicos\/$/, () => HttpResponse.json([])),
  http.get(/\/api\/v1\/dashboard\/resumen\/$/, () =>
    HttpResponse.json({
      hoy: '2026-11-15',
      anio: 2026,
      activos: {
        total: 1,
        operativos: 1,
        en_mantenimiento: 0,
        dados_de_baja: 0,
        inactivos: 0,
        valor_total: null,
        por_estado: [
          { estado: 'DISPONIBLE', etiqueta: 'Disponible', total: 1 },
          { estado: 'ASIGNADO', etiqueta: 'Asignado', total: 0 },
          { estado: 'EN_MANTENIMIENTO', etiqueta: 'En mantenimiento', total: 0 },
          { estado: 'DADO_DE_BAJA', etiqueta: 'Dado de baja', total: 0 },
        ],
        por_categoria: [],
        por_marca: [],
        ultimas_adquisiciones: [],
      },
      mantenimientos: null,
    }),
  ),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
beforeEach(() => {
  rol = 'ADMINISTRADOR';
  localStorage.setItem('access_token', 'token');
  window.history.pushState({}, '', '/activos');
});
afterEach(() => {
  localStorage.clear();
  server.resetHandlers();
  window.history.pushState({}, '', '/');
});
afterAll(() => server.close());

describe('App smoke /activos', () => {
  it('ADMINISTRADOR ve contenido real de /activos', async () => {
    render(<App />);
    expect(await screen.findByText('SN1')).toBeInTheDocument();
    expect(screen.getByText('AST-2024-000001')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Activos/ })).toBeInTheDocument();
    expect(screen.queryByText('Ha ocurrido un error inesperado.')).not.toBeInTheDocument();
  });

  it('TECNICO ve contenido real de /activos', async () => {
    rol = 'TECNICO';
    render(<App />);
    expect(await screen.findByText('SN1')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Activos/ })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Catálogos/ })).not.toBeInTheDocument();
    expect(screen.queryByText('Ha ocurrido un error inesperado.')).not.toBeInTheDocument();
  });

  it('ADMINISTRADOR ve contenido real de /mantenimientos', async () => {
    window.history.pushState({}, '', '/mantenimientos');
    render(<App />);
    expect(await screen.findByText('AST-2026-000001')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Mantenimientos' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Mantenimientos/ })).toBeInTheDocument();
  });

  it('TECNICO ve contenido real de /mantenimientos', async () => {
    rol = 'TECNICO';
    window.history.pushState({}, '', '/mantenimientos');
    render(<App />);
    expect(await screen.findByText('AST-2026-000001')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Mantenimientos' })).toBeInTheDocument();
  });

  it('USUARIO_RESPONSABLE se redirige fuera de /mantenimientos', async () => {
    rol = 'USUARIO_RESPONSABLE';
    window.history.pushState({}, '', '/mantenimientos');
    render(<App />);
    expect(
      await screen.findByRole('heading', { name: 'Dashboard' }),
    ).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Mantenimientos' })).not.toBeInTheDocument();
  });
});
