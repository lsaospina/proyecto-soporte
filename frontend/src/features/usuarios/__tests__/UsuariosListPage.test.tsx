import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UsuariosListPage } from '../pages/UsuariosListPage';

vi.mock('../api/usuarios.api', () => ({
  listUsuarios: vi.fn().mockResolvedValue({
    count: 1,
    next: null,
    previous: null,
    results: [
      {
        id: 1,
        email: 'admin@test.com',
        nombre_completo: 'Admin Test',
        rol: 'ADMINISTRADOR',
        is_active: true,
        mfa_activo: true,
        debe_cambiar_password: false,
        esta_bloqueado: false,
      },
    ],
  }),
  resetPassword: vi.fn(),
  resetMfa: vi.fn(),
  activarUsuario: vi.fn(),
  desactivarUsuario: vi.fn(),
}));

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <UsuariosListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('UsuariosListPage', () => {
  it('renders users list with data', async () => {
    renderPage();
    expect(await screen.findByText('Admin Test')).toBeInTheDocument();
    expect(screen.getByText('admin@test.com')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /nuevo usuario/i })).toBeInTheDocument();
  });
});
