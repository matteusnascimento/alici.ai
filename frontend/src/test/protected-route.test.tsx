import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';

import { ThemeProvider } from '../contexts/ThemeContext';

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({ isAuthenticated: false, ready: true }),
}));

import { ProtectedRoute } from '../router/ProtectedRoute';

describe('ProtectedRoute', () => {
  it('redireciona visitantes para login', () => {
    render(
      <ThemeProvider>
        <MemoryRouter initialEntries={['/app/dashboard']}>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route element={<div>Privado</div>} path="/app/dashboard" />
            </Route>
            <Route element={<div>Login</div>} path="/login" />
          </Routes>
        </MemoryRouter>
      </ThemeProvider>,
    );

    expect(screen.getByText('Login')).toBeInTheDocument();
  });
});
