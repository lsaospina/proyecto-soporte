import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, afterEach, beforeAll, afterAll } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { ActivosFormPage } from '../pages/ActivosFormPage';

const marcas = [
  { id: 1, nombre: 'Dell', is_active: true },
  { id: 2, nombre: 'HP', is_active: true },
];
const modelos = [
  { id: 10, nombre: 'Latitude', marca: 1, is_active: true },
  { id: 20, nombre: 'EliteBook', marca: 2, is_active: true },
];
const activoDetalle = {
  id: 5,
  serial: 'SN-OLD',
  modelo: 10,
  modelo_nombre: 'Latitude',
  marca_nombre: 'Dell',
  categoria_nombre: 'Portátiles',
  fecha_adquisicion: '2024-01-01',
  valor_adquisicion: null,
  estado: 'DISPONIBLE',
  codigo_qr: 'AST-2024-000005',
  procesador: '',
  ram_gb: null,
  almacenamiento_gb: null,
  direccion_mac: '',
  observaciones: '',
  is_active: true,
};

let posted: Record<string, unknown> | null = null;
let patched: Record<string, unknown> | null = null;

const server = setupServer(
  http.get(/\/api\/v1\/marcas\/$/, () =>
    HttpResponse.json({ count: marcas.length, next: null, previous: null, results: marcas }),
  ),
  http.get(/\/api\/v1\/modelos\/$/, () =>
    HttpResponse.json({ count: modelos.length, next: null, previous: null, results: modelos }),
  ),
  http.get(/\/api\/v1\/activos\/5\/$/, () => HttpResponse.json(activoDetalle)),
  http.post(/\/api\/v1\/activos\/$/, async ({ request }) => {
    posted = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json({ ...activoDetalle, ...posted }, { status: 201 });
  }),
  http.patch(/\/api\/v1\/activos\/5\/$/, async ({ request }) => {
    patched = (await request.json()) as Record<string, unknown>;
    return HttpResponse.json({ ...activoDetalle, ...patched }, { status: 200 });
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  posted = null;
  patched = null;
});
afterAll(() => server.close());

function renderForm(initialEntry = '/activos/nuevo') {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/activos/nuevo" element={<ActivosFormPage />} />
          <Route path="/activos/:id/editar" element={<ActivosFormPage />} />
          <Route path="/activos" element={<div>Lista activos</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

async function completarFormulario(serial: string) {
  const user = userEvent.setup();
  await user.type(await screen.findByLabelText(/Serial/), serial);
  await screen.findByRole('option', { name: 'Dell' });
  await user.selectOptions(screen.getByLabelText(/Marca/), '1');
  await user.selectOptions(screen.getByLabelText(/Modelo/), '10');
  fireEvent.change(screen.getByLabelText(/Fecha de adquisición/), { target: { value: '2024-01-01' } });
  return user;
}

describe('ActivosFormPage', () => {
  it('marca -> modelo dependiente', async () => {
    const user = userEvent.setup();
    renderForm();
    await screen.findByRole('option', { name: 'Dell' });

    await user.selectOptions(screen.getByLabelText(/Marca/), '1');
    const modelo = screen.getByLabelText(/Modelo/);
    await waitFor(() => expect(within(modelo).getByRole('option', { name: 'Latitude' })).toBeInTheDocument());
    expect(within(modelo).queryByRole('option', { name: 'EliteBook' })).not.toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText(/Marca/), '2');
    expect(within(modelo).getByRole('option', { name: 'EliteBook' })).toBeInTheDocument();
    expect(within(modelo).queryByRole('option', { name: 'Latitude' })).not.toBeInTheDocument();
  });

  it('crear OK', async () => {
    renderForm();
    const user = await completarFormulario('SN1');
    await user.click(screen.getByRole('button', { name: /Guardar/ }));
    expect(await screen.findByText('Lista activos')).toBeInTheDocument();
    expect(posted?.serial).toBe('SN1');
    expect(posted?.modelo).toBe(10);
  });

  it('editar OK', async () => {
    renderForm('/activos/5/editar');
    const serial = await screen.findByDisplayValue('SN-OLD');
    expect(screen.getByText('Editar activo')).toBeInTheDocument();
    await screen.findByRole('option', { name: 'Dell' });
    await waitFor(() => expect((screen.getByLabelText(/Marca/) as HTMLSelectElement).value).toBe('1'));

    const user = userEvent.setup();
    await user.clear(serial);
    await user.type(serial, 'SN-EDIT');
    await user.click(screen.getByRole('button', { name: /Guardar/ }));

    expect(await screen.findByText('Lista activos')).toBeInTheDocument();
    expect(patched?.serial).toBe('SN-EDIT');
  });

  it('error 400 por serial duplicado mostrado en el campo', async () => {
    server.use(
      http.post(/\/api\/v1\/activos\/$/, () =>
        HttpResponse.json({ serial: ['Ya existe un activo con ese serial.'] }, { status: 400 }),
      ),
    );
    renderForm();
    const user = await completarFormulario('SN1');
    await user.click(screen.getByRole('button', { name: /Guardar/ }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Ya existe un activo con ese serial.');
  });
});
