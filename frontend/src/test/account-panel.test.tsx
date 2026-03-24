import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

const saveProfile = vi.fn(async () => undefined);
const saveSettings = vi.fn(async () => undefined);
const upgrade = vi.fn(async () => 'ok');
const reloadBilling = vi.fn();

const mockAccount = {
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
};

const mockPlans = [
  {
    id: 'free',
    name: 'Free',
    monthly_price: 0,
    yearly_price: 0,
    features: ['A'],
    limits: [{ key: 'messages', value: 500 }],
    active: true,
  },
];

const mockCurrent = {
  plan_id: 'free',
  plan_name: 'Free',
  status: 'active',
  billing_cycle: 'monthly',
  monthly_price: 0,
  yearly_price: 0,
  auto_renew: true,
  started_at: new Date('2026-03-24T00:00:00.000Z').toISOString(),
};

const mockUsage = {
  items: [{ metric: 'messages', used: 10, limit: 500 }],
};

vi.mock('../hooks/useSettings', () => ({
  useSettings: () => ({
    account: mockAccount,
    loading: false,
    saving: false,
    error: null,
    saveProfile,
    saveSettings,
  }),
}));

vi.mock('../hooks/useBilling', () => ({
  useBilling: () => ({
    plans: mockPlans,
    current: mockCurrent,
    usage: mockUsage,
    loading: false,
    upgrading: false,
    error: null,
    upgrade,
    reload: reloadBilling,
  }),
}));

import { AccountPanel } from '../components/platform/AccountPanel';

describe('AccountPanel', () => {
  it('renderiza perfil e billing', () => {
    render(<AccountPanel />);
    expect(screen.getByRole('heading', { name: 'Perfil' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Billing AXI' })).toBeInTheDocument();
  });
});
