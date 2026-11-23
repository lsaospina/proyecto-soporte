import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

vi.mock('../features/auth/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

import { useAuth } from '../features/auth/hooks/useAuth';
import { ProtectedRoute } from '../routes/ProtectedRoute';

function setup(authState: { user: any; isAuthenticated: boolean; isLoading: boolean }) {
  (useAuth as any).mockReturnValue(authState);
}

describe('ProtectedRoute', () => {
  it('redirects to /login when not authenticated', () => {
    setup({ user: null, isAuthenticated: false, isLoading: false });
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/protected" element={<div>protected content</div>} />
          </Route>
          <Route path="/login" element={<div>login page</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('login page')).toBeInTheDocument();
  });

  it('renders outlet when authenticated without role restriction', () => {
    setup({ user: { rol: 'TECNICO' }, isAuthenticated: true, isLoading: false });
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/protected" element={<div>protected content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('protected content')).toBeInTheDocument();
  });

  it('redirects to /dashboard when role not allowed', () => {
    setup({ user: { rol: 'USUARIO_RESPONSABLE' }, isAuthenticated: true, isLoading: false });
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<ProtectedRoute roles={['ADMINISTRADOR']} />}>
            <Route path="/protected" element={<div>protected content</div>} />
          </Route>
          <Route path="/dashboard" element={<div>dashboard page</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('dashboard page')).toBeInTheDocument();
  });

  it('renders outlet when role is allowed', () => {
    setup({ user: { rol: 'ADMINISTRADOR' }, isAuthenticated: true, isLoading: false });
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<ProtectedRoute roles={['ADMINISTRADOR']} />}>
            <Route path="/protected" element={<div>protected content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('protected content')).toBeInTheDocument();
  });
});
