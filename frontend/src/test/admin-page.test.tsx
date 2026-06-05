import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { vi } from 'vitest';

vi.mock('../services/admin.service', () => ({
  ADMIN_PERMISSION_MODULES: [
    { key: 'revenue', label: 'Revenue' },
    { key: 'chats', label: 'Chats' },
    { key: 'assistant', label: 'AXI Assistant' },
    { key: 'marketing', label: 'Marketing' },
    { key: 'studio', label: 'Studio' },
    { key: 'integrations', label: 'Integrations' },
    { key: 'admin', label: 'Administracao' },
  ],
  createEmptyPermissions: () => ({
    revenue: 'none',
    chats: 'none',
    assistant: 'none',
    marketing: 'none',
    studio: 'none',
    integrations: 'none',
    admin: 'none',
  }),
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
      usuarios: [],
      permissoes: ['owner'],
      billing: [{ label: 'Eventos Stripe', value: 2 }],
      seguranca: [{ label: 'Sessoes ativas', value: 1 }],
      auditoria: [{ label: 'Eventos registrados', value: 1 }],
    }),
  listAdminUsers: () =>
    Promise.resolve([
      {
        id: 1,
        name: 'Geovana Moreira',
        email: 'geovana@pousadamaresol.com.br',
        role: 'owner',
        plan: 'enterprise',
        job_title: 'Gerente',
        phone: null,
        company: 'Pousada Mar e Sol',
        status: 'active',
        last_login_at: '2026-05-01T00:00:00Z',
        created_at: '2026-05-01T00:00:00Z',
        disabled_at: null,
        email_verified: true,
        permissions: { revenue: 'admin', chats: 'write', assistant: 'read' },
      },
    ]),
  getAdminSecurity: () =>
    Promise.resolve({
      last_logins: [],
      active_sessions: [],
      open_sessions: [],
      login_attempts: [],
      revoked_tokens: [],
    }),
  getAdminAudit: () =>
    Promise.resolve({
      events: [{ id: 1, data: '2026-05-01T00:00:00Z', usuario: 'Geovana Moreira', acao: 'usuario_convidado', origem: 'admin', detalhes: null }],
    }),
  getAdminUserPermissions: () =>
    Promise.resolve({
      user_id: 1,
      permissions: { revenue: 'admin', chats: 'write', assistant: 'read', marketing: 'none', studio: 'none', integrations: 'none', admin: 'none' },
    }),
  saveAdminUserPermissions: () =>
    Promise.resolve({
      user_id: 1,
      permissions: { revenue: 'admin', chats: 'write', assistant: 'read', marketing: 'read', studio: 'none', integrations: 'none', admin: 'none' },
    }),
  disableAdminUser: vi.fn(),
  enableAdminUser: vi.fn(),
  resetAdminUserPassword: vi.fn(),
  updateAdminUser: vi.fn(),
  inviteAdminUser: vi.fn(),
  getAdminBilling: () =>
    Promise.resolve({
    current: {
      plan_id: 'free',
      plan_name: 'Free',
      status: 'active',
      billing_cycle: 'monthly',
      monthly_price: 0,
      yearly_price: 0,
      auto_renew: true,
      cancel_at_period_end: false,
      started_at: '2026-05-01T00:00:00Z',
      next_renewal_at: null,
      provider: 'stripe',
      stripe_customer_id: null,
    },
      usage: [{ metric: 'messages', used: 12, limit: 500 }],
      limits: [{ key: 'messages', value: 500 }],
      events: [
        {
          id: 1,
          event_type: 'invoice_paid',
          amount: 197,
          currency: 'BRL',
          description: 'Fatura Pro',
          stripe_event_id: 'evt_test',
          status: 'paid',
          created_at: '2026-05-01T00:00:00Z',
        },
      ],
      stripe_configured: true,
      message: null,
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
    expect(await screen.findByText('Plano Atual')).toBeInTheDocument();
    expect(screen.getByText('Resumo Stripe')).toBeInTheDocument();
    expect(screen.queryByText('Upgrade')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Usuarios/i }));
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/users');
    expect(screen.getByText('Geovana Moreira')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Novo usuario/i }));
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/users/new');
    expect(screen.getByRole('heading', { name: /Convidar usuario/i })).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Cancelar/i }));
    await user.click(screen.getByRole('button', { name: /Permissoes/i }));
    expect(screen.getByTestId('location')).toHaveTextContent('/app/admin/permissions');
    expect(screen.getByText('AXI Assistant')).toBeInTheDocument();
  });
});
