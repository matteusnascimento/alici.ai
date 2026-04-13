import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

vi.mock('../hooks/useDashboard', () => ({
  useDashboard: () => ({
    stats: {
      total_messages: 12,
      total_agents: 3,
      revenue: 1200,
      conversions: 8,
      clicks: 90,
      quotes: 4,
      usage_bars: [
        { label: 'Seg', value: 2 },
        { label: 'Ter', value: 3 },
      ],
    },
    loading: false,
    error: null,
    reload: vi.fn(),
  }),
}));

vi.mock('../services/dashboard.service', async (importOriginal) => {
  const orig = await importOriginal<typeof import('../services/dashboard.service')>();
  return {
    ...orig,
    getDashboardOverview: () => Promise.resolve({ total_messages: 0, total_agents: 0, active_agents: 0, current_plan: 'free' }),
    getDashboardUsage: () => Promise.resolve({ messages_used: 0, messages_limit: 100, agents_used: 0, agents_limit: 3 }),
  };
});

vi.mock('../services/marketing.service', () => ({
  listProjects: () => Promise.resolve([]),
}));

vi.mock('../services/integrations.service', () => ({
  listChannelIntegrations: () => Promise.resolve([]),
}));

import { DashboardPanel } from '../components/platform/DashboardPanel';

describe('DashboardPanel', () => {
  it('renderiza metricas do dashboard', async () => {
    render(
      <MemoryRouter>
        <DashboardPanel />
      </MemoryRouter>,
    );
    expect(screen.getByText(/Mensagens/i)).toBeInTheDocument();
    expect(screen.getByText(/Receita/i)).toBeInTheDocument();
    expect(await screen.findByText(/Plano atual/i)).toBeInTheDocument();
  });
});
