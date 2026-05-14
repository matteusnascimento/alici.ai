import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

import { LoginForm } from '../../frontend/src/components/auth/LoginForm';
import { AuthProvider } from '../../frontend/src/hooks/useAuth';

vi.mock('../../frontend/src/services/auth.service', () => ({
  login: vi.fn(async () => ({ access_token: 'token', token_type: 'bearer', user: { id: 1, name: 'Ana', username: 'ana', email: 'ana@example.com', phone: null, plan: 'starter', created_at: new Date().toISOString() } })),
  register: vi.fn(),
  getMe: vi.fn(async () => {
    throw new Error('no session');
  }),
  logout: vi.fn(),
}));

describe('LoginForm', () => {
  it('envia o formulário de login', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <LoginForm />
        </AuthProvider>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText(/Email/i), 'ana@example.com');
    await userEvent.type(screen.getByLabelText(/Senha/i), '123456');
    await userEvent.click(screen.getByRole('button', { name: /Entrar/i }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Entrando...|Entrar/i })).toBeInTheDocument();
    });
  });
});
