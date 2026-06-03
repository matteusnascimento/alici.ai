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
      bio: 'Lidero a operacao de atendimento com IA na empresa.',
      company: 'AXI Labs',
      job_title: 'Head de Operacoes',
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

  it('renderiza somente dados pessoais e verificacoes da conta', async () => {
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
    expect(screen.getByText('Informacoes pessoais')).toBeInTheDocument();
    expect(screen.getByText('Verificacoes')).toBeInTheDocument();
    expect(screen.getAllByText('Email')).toHaveLength(2);
    expect(screen.getAllByText('Telefone')).toHaveLength(2);
    expect(screen.getAllByText('Pendente')).toHaveLength(2);
    expect(screen.getByDisplayValue('ana@example.com')).toBeInTheDocument();
    expect(screen.getByDisplayValue('11988887777')).toBeInTheDocument();
    expect(screen.queryByText(/Perfil \d+%/i)).not.toBeInTheDocument();
    expect(screen.queryByText('Conta e contexto profissional')).not.toBeInTheDocument();
    expect(screen.queryByText('Status da conta')).not.toBeInTheDocument();
    expect(screen.queryByDisplayValue('AXI Labs')).not.toBeInTheDocument();
    expect(screen.queryByDisplayValue('Head de Operacoes')).not.toBeInTheDocument();
  });
});
