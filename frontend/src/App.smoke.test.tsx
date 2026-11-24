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
});
