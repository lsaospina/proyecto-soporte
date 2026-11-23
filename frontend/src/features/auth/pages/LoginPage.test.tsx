import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../api/auth.api', () => ({
  login: vi.fn(),
}));
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({ setAccessToken: vi.fn(), refreshUser: vi.fn() }),
}));

import { login } from '../api/auth.api';
import { LoginPage } from './LoginPage';

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders credentials form', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );
    expect(screen.getByPlaceholderText('usuario@empresa.com')).toBeInTheDocument();
    expect(document.getElementById('corporatePassword')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('switches to password change step on password_change_required', async () => {
    (login as any).mockResolvedValue({ status: 'password_change_required', password_token: 'tok-123' });
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );
    fireEvent.change(screen.getByPlaceholderText('usuario@empresa.com'), { target: { value: 'a@b.com' } });
    fireEvent.change(document.getElementById('corporatePassword') as HTMLInputElement, { target: { value: 'secret' } });
    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    await waitFor(() => {
      expect(screen.getByText(/cambio de contraseña obligatorio/i)).toBeInTheDocument();
    });
  });
});
