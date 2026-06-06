import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';

import { LoginForm } from '../components/auth/LoginForm';
import { AuthProvider } from '../hooks/useAuth';

vi.mock('../services/auth.service', () => ({
  login: vi.fn(async () => ({ access_token: 'token', token_type: 'bearer', user: { id: 1, name: 'Ana', username: 'ana', email: 'ana@example.com', phone: null, plan: 'free', created_at: new Date().toISOString() } })),
  register: vi.fn(),
  getMe: vi.fn(async () => {
    throw new Error('no session');
  }),
  startGoogleLogin: vi.fn(),
  logout: vi.fn(),
}));

describe('LoginForm', () => {
  it('envia o formulario de login', async () => {
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

  it('redireciona para rota anterior apos login', async () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: '/login', state: { from: { pathname: '/app/chat' } } }] }>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route path="/app/chat" element={<div>Chat</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getByLabelText(/Email/i), 'ana@example.com');
    await userEvent.type(screen.getByLabelText(/Senha/i), '123456');
    await userEvent.click(screen.getByRole('button', { name: /Entrar/i }));

    await waitFor(() => {
      expect(screen.getByText('Chat')).toBeInTheDocument();
    });
  });
});
