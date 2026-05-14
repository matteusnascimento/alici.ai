import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';

vi.mock('../../frontend/src/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { name: 'Ana', plan: 'free' },
    isAuthenticated: true,
    ready: true,
    logout: vi.fn(),
  }),
}));

import { PlatformShell } from '../../frontend/src/components/platform/PlatformShell';

describe('PlatformShell', () => {
  it('renderiza a área autenticada', () => {
    render(
      <MemoryRouter initialEntries={['/app/dashboard']}>
        <Routes>
          <Route element={<PlatformShell />} path="/app/dashboard" />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText(/Control Room/i)).toBeInTheDocument();
  });
});
