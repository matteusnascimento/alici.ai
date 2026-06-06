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

    expect(screen.getByText(/Automa..o com IA para neg.cios reais/i)).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /Come.ar gr.tis/i }).length).toBeGreaterThan(0);
  });
});
