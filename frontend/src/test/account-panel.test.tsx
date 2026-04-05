import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import { AccountShell } from '../components/account/AccountShell';

describe('AccountPanel', () => {
  it('renderiza navegação de conta e subpágina', () => {
    render(
      <MemoryRouter initialEntries={['/app/account']}>
        <Routes>
          <Route path="/app/account" element={<AccountShell />}>
            <Route index element={<div>Conteudo</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText(/AXI Account Center/i)).toBeInTheDocument();
    expect(screen.getByText(/Overview/i)).toBeInTheDocument();
    expect(screen.getByText('Conteudo')).toBeInTheDocument();
  });
});
