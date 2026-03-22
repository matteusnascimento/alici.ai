import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: { name: 'Ana', plan: 'free' },
    isAuthenticated: true,
    ready: true,
    logout: vi.fn(),
  }),
}));

import { PlatformShell } from '../components/platform/PlatformShell';

describe('PlatformShell', () => {
  it('renderiza a area autenticada', () => {
    render(
      <MemoryRouter initialEntries={['/app']}>
        <Routes>
          <Route element={<PlatformShell />} path="/app" />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText(/Control Room/i)).toBeInTheDocument();
  });
});
