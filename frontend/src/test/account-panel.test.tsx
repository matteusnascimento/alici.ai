import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

vi.mock('../hooks/useSettings', () => ({
  useSettings: () => ({
    account: {
      profile: {
        name: 'Ana',
        username: 'ana',
        email: 'ana@example.com',
        phone: '1199999',
        plan: 'free',
      },
      settings: {
        background_conversation: true,
        autocomplete: true,
        trending: true,
        sequence: false,
        split_mode: false,
        language: 'pt-BR',
        voice: 'neutral',
      },
    },
    loading: false,
    saving: false,
    error: null,
    saveProfile: vi.fn(async () => undefined),
    saveSettings: vi.fn(async () => undefined),
  }),
}));

vi.mock('../hooks/useBilling', () => ({
  useBilling: () => ({
    plans: [
      {
        id: 'free',
        name: 'Free',
        monthly_price: 0,
        yearly_price: 0,
        features: ['A'],
        limits: [{ key: 'messages', value: 500 }],
        active: true,
      },
    ],
    current: {
      plan_id: 'free',
      plan_name: 'Free',
      status: 'active',
      billing_cycle: 'monthly',
      monthly_price: 0,
      yearly_price: 0,
      auto_renew: true,
      started_at: new Date().toISOString(),
    },
    usage: { items: [{ metric: 'messages', used: 10, limit: 500 }] },
    loading: false,
    upgrading: false,
    error: null,
    upgrade: vi.fn(async () => 'ok'),
    reload: vi.fn(),
  }),
}));

import { AccountPanel } from '../components/platform/AccountPanel';

describe('AccountPanel', () => {
  it('renderiza perfil e billing', () => {
    render(<AccountPanel />);
    expect(screen.getByText(/Perfil/i)).toBeInTheDocument();
    expect(screen.getByText(/Billing AXI/i)).toBeInTheDocument();
  });
});
