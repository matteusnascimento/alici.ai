import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AccountProfilePage } from '../components/account/pages/AccountProfilePage';

const getAccountProfileMock = vi.fn();
const updateAccountProfileMock = vi.fn();
const uploadAccountAvatarMock = vi.fn();
const requestEmailVerificationMock = vi.fn();
const confirmEmailVerificationMock = vi.fn();
const requestPhoneVerificationMock = vi.fn();
const confirmPhoneVerificationMock = vi.fn();

vi.mock('../services/account.service', () => ({
  getAccountProfile: (...args: unknown[]) => getAccountProfileMock(...args),
  updateAccountProfile: (...args: unknown[]) => updateAccountProfileMock(...args),
  uploadAccountAvatar: (...args: unknown[]) => uploadAccountAvatarMock(...args),
  requestEmailVerification: (...args: unknown[]) => requestEmailVerificationMock(...args),
  confirmEmailVerification: (...args: unknown[]) => confirmEmailVerificationMock(...args),
  requestPhoneVerification: (...args: unknown[]) => requestPhoneVerificationMock(...args),
  confirmPhoneVerification: (...args: unknown[]) => confirmPhoneVerificationMock(...args),
}));

vi.mock('../hooks/useBilling', () => ({
  useBilling: () => ({ current: { plan_name: 'Pro' } }),
}));

vi.mock('../hooks/useToast', () => ({
  useToast: () => ({ pushToast: vi.fn() }),
}));

describe('AccountProfilePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccountProfileMock.mockResolvedValue({
      id: 1,
      name: 'Ana Souza',
      username: 'ana.souza',
      email: 'ana@example.com',
      phone: '11988887777',
      avatar_url: null,
      bio: 'Lidero a operação de atendimento com IA na empresa.',
      company: 'AXI Labs',
      job_title: 'Head de Operações',
      timezone: 'America/Sao_Paulo',
      language: 'pt-BR',
      email_verified: false,
      phone_verified: false,
      status: 'ativa',
      plan: 'free',
      created_at: new Date('2026-01-10T12:00:00Z').toISOString(),
      updated_at: new Date('2026-04-17T12:00:00Z').toISOString(),
      last_login_at: new Date('2026-04-17T13:00:00Z').toISOString(),
    });
  });

  it('renderiza contexto, status e completude do perfil', async () => {
    render(
      <MemoryRouter>
        <AccountProfilePage />
      </MemoryRouter>,
    );

    expect(screen.getByText(/Carregando perfil/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Ana Souza')).toBeInTheDocument();
    });

    expect(screen.getByText('@ana.souza')).toBeInTheDocument();
    expect(screen.getByText(/Perfil \d+% concluído/i)).toBeInTheDocument();
    expect(screen.getByText('Dados principais')).toBeInTheDocument();
    expect(screen.getByText('Conta e contexto profissional')).toBeInTheDocument();
    expect(screen.getAllByText('Status da conta')).toHaveLength(2);
    expect(screen.getByText('Verificações')).toBeInTheDocument();
    expect(screen.getByText('Verificação de email')).toBeInTheDocument();
    expect(screen.getByText('Verificação de telefone')).toBeInTheDocument();
    expect(screen.getByDisplayValue('AXI Labs')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Head de Operações')).toBeInTheDocument();
    expect(screen.getByText('Não verificado')).toBeInTheDocument();
    expect(screen.getByText('Ainda não confirmado')).toBeInTheDocument();
  });
});