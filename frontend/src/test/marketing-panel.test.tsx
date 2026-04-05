import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import { StudioHomePage } from '../components/studio/tools/StudioHomePage';

describe('MarketingPanel', () => {
  it('renderiza cards principais do AXI Studio', () => {
    render(
      <MemoryRouter>
        <StudioHomePage />
      </MemoryRouter>,
    );
    expect(screen.getByText(/Create \/ Generate/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Anuncios Inteligentes/i })).toBeInTheDocument();
  });
});
