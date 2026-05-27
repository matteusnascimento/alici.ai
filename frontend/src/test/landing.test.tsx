import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import { LandingPage } from '../components/landing/LandingPage';

describe('LandingPage', () => {
  it('renderiza a proposta principal', () => {
    render(
      <MemoryRouter>
        <LandingPage />
      </MemoryRouter>,
    );

    expect(screen.getAllByText(/Crie, Edite e/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Revolucione/i).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('link', { name: /Criar conta gratis|Testar gratis|Comecar agora/i }).length).toBeGreaterThan(0);
  });
});
