import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { vi } from 'vitest';

vi.mock('../services/admin.service', () => ({
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
    expect(screen.getByText('Operacao administrativa')).toBeInTheDocument();
    expect(screen.queryByText('Pousada Mar e Sol')).not.toBeInTheDocument();

    await user.click(screen.getAllByRole('button', { name: /Billing/i })[0]);
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/billing');
    expect(screen.getByText(/eventos Stripe reais/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Usuarios/i }));
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/users');
    expect(screen.getByText('Geovana Moreira')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Novo usuario/i }));
    expect(screen.getByRole('heading', { name: /Novo usuario/i })).toBeInTheDocument();
    expect(screen.getByText(/backend atual ainda nao expoe/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Cancelar/i }));
    await user.click(screen.getByRole('button', { name: /Permissoes/i }));
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/permissions');
    expect(screen.getByText('AXI Assistant')).toBeInTheDocument();
  });
});
