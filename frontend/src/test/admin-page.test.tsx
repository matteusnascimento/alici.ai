import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { vi } from 'vitest';

vi.mock('../services/admin.service', () => ({
  createAdminCompany: vi.fn(),
  getAdminOverview: () =>
    Promise.resolve({
      empresas: [
        {
          name: 'Pousada Mar e Sol',
          email: 'mar@pousadamaresol.com.br',
          plan: 'enterprise',
          status: 'Ativa',
          users_count: 3,
          created_at: '2026-05-01',
        },
      ],
      usuarios: [
        { id: 1, name: 'Geovana Moreira', email: 'geovana@pousadamaresol.com.br', role: 'owner', plan: 'enterprise' },
      ],
      permissoes: ['owner'],
      billing: [{ label: 'Eventos Stripe', value: 2 }],
      seguranca: [{ label: 'Rate limit', value: 1 }],
      auditoria: [{ label: 'Usuarios cadastrados', value: 1 }],
    }),
}));

import { AdminPage } from '../components/admin/AdminPage';

function LocationProbe() {
  const location = useLocation();
  return <span data-testid="location">{location.pathname}{location.search}</span>;
}

describe('AdminPage', () => {
  it('navega pelos botoes principais usando a URL da Administracao', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/app/admin']}>
        <AdminPage />
        <LocationProbe />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Administracao/i })).toBeInTheDocument();
    expect(screen.getByText('Pousada Mar e Sol')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Ver detalhes/i }));
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/billing');

    await user.click(screen.getByRole('button', { name: /Nova empresa/i }));
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/companies?action=new');
    expect(screen.getByRole('heading', { name: /Criar empresa no AXI/i })).toBeInTheDocument();

    await user.click(screen.getAllByRole('button', { name: /^Gerenciar ->$/i })[0]);
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/users');
  });
});
