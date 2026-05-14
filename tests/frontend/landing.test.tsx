import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import { LandingPage } from '../../frontend/src/components/landing/LandingPage';

describe('LandingPage', () => {
  it('renderiza a proposta principal', () => {
    render(
      <MemoryRouter>
        <LandingPage />
      </MemoryRouter>,
    );

    expect(screen.getByText(/AXI transforma atendimento/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Criar conta/i })).toBeInTheDocument();
  });
});
