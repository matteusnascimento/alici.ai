import { render, screen } from '@testing-library/react';
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

import { DashboardPanel } from '../components/platform/DashboardPanel';

describe('DashboardPanel', () => {
  it('renderiza metricas do dashboard', () => {
    render(<DashboardPanel />);
    expect(screen.getByText(/Mensagens/i)).toBeInTheDocument();
    expect(screen.getByText(/Receita/i)).toBeInTheDocument();
  });
});
