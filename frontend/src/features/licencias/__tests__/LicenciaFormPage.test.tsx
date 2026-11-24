import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

import { LicenciaFormPage } from '../pages/LicenciaFormPage';
import type { Licencia } from '../types';

const licencia: Licencia = {
  id: 7,
  proveedor: 3,
  proveedor_nombre: 'Google',
  servicio: 'Google Workspace Business Standard',
  periodicidad: 'ANUAL',
  fecha_renovacion: '2027-09-15',
  cantidad: 110,
  valor: '4680000.00',
  renovacion_automatica: true,
  medio_pago: 'Facturación electrónica',
  cuenta_vinculada: 'ti@empresa.com',
  responsable_uso: 'Toda la empresa',
  observacion: 'Confirmar cantidad antes de renovar.',
  is_active: true,
  dias_para_renovacion: 296,
  estado_renovacion: 'VIGENTE',
  estado_renovacion_etiqueta: 'Vigente',
  created_at: '2026-11-01T10:00:00Z',
  updated_at: '2026-11-01T10:00:00Z',
};

let crearBody: Record<string, unknown> | null = null;
let actualizarBody: Record<string, unknown> | null = null;
let posts = 0;

const server = setupServer(
  http.get(/\/api\/v1\/licencias\/proveedores\/$/, () =>
    HttpResponse.json([
      { id: 1, nombre: 'Microsoft' },
      { id: 3, nombre: 'Google' },
    ]),
  ),
  http.get(/\/api\/v1\/licencias\/7\/$/, () => HttpResponse.json(licencia)),
  http.post(/\/api\/v1\/licencias\/$/, async ({ request }) => {
    posts += 1;
    crearBody = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json({ ...licencia, id: 20 }, { status: 201 });
  }),
  http.patch(/\/api\/v1\/licencias\/7\/$/, async ({ request }) => {
    actualizarBody = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json({ ...licencia, ...actualizarBody });
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  crearBody = null;
  actualizarBody = null;
  posts = 0;
});
afterAll(() => server.close());

function renderForm(ruta: string) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[ruta]}>
        <Routes>
          <Route path="/licencias/nueva" element={<LicenciaFormPage />} />
          <Route path="/licencias/:id/editar" element={<LicenciaFormPage />} />
          <Route path="/licencias" element={<div>LISTA DE LICENCIAS</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('LicenciaFormPage', () => {
  it('crea una licencia y navega al listado', async () => {
    const user = userEvent.setup();
    renderForm('/licencias/nueva');

    await user.type(screen.getByLabelText(/^Proveedor/), 'Oracle Cloud');
    await user.type(screen.getByLabelText(/^Servicio/), 'Base de datos autónoma');
    await user.clear(screen.getByLabelText(/^Cantidad de licencias/));
    await user.type(screen.getByLabelText(/^Cantidad de licencias/), '4');
    fireEvent.change(screen.getByLabelText(/^Fecha de renovación/), {
      target: { value: '2027-03-15' },
    });
    await user.type(screen.getByLabelText(/^Valor a pagar/), '1200.50');
    await user.type(screen.getByLabelText(/^Medio de pago/), 'Facturación electrónica');
    await user.type(screen.getByLabelText(/^Responsable o área de uso/), 'Equipo de Sistemas');
    await user.click(screen.getByLabelText(/^Renovación automática/));
    await user.click(screen.getByRole('button', { name: 'Guardar licencia' }));

    expect(await screen.findByText('LISTA DE LICENCIAS')).toBeInTheDocument();
    expect(crearBody).toMatchObject({
      proveedor: 'Oracle Cloud',
      servicio: 'Base de datos autónoma',
      cantidad: 4,
      fecha_renovacion: '2027-03-15',
      valor: '1200.50',
      renovacion_automatica: true,
      medio_pago: 'Facturación electrónica',
      responsable_uso: 'Equipo de Sistemas',
    });
  });

  it('edita una licencia existente', async () => {
    const user = userEvent.setup();
    renderForm('/licencias/7/editar');

    await waitFor(() => {
      expect(screen.getByLabelText(/^Proveedor/)).toHaveValue('Google');
    });
    expect(screen.getByLabelText(/^Servicio/)).toHaveValue(
      'Google Workspace Business Standard',
    );
    expect(screen.getByLabelText(/^Valor a pagar/)).toHaveValue('4680000.00');

    await user.clear(screen.getByLabelText(/^Servicio/));
    await user.type(screen.getByLabelText(/^Servicio/), 'Workspace Empresarial');
    await user.click(screen.getByRole('button', { name: 'Guardar licencia' }));

    expect(await screen.findByText('LISTA DE LICENCIAS')).toBeInTheDocument();
    expect(actualizarBody).toMatchObject({
      servicio: 'Workspace Empresarial',
      cantidad: 110,
      renovacion_automatica: true,
    });
  });

  it('valida los campos obligatorios antes de enviar', async () => {
    const user = userEvent.setup();
    renderForm('/licencias/nueva');

    await user.click(screen.getByRole('button', { name: 'Guardar licencia' }));

    expect(await screen.findByText('El proveedor es obligatorio')).toBeInTheDocument();
    expect(screen.getByText('El servicio es obligatorio')).toBeInTheDocument();
    expect(posts).toBe(0);
  });
});
