import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

vi.mock('../hooks/useAgents', () => ({
  useAgents: () => ({
    agents: [
      {
        id: 1,
        user_id: 1,
        nome: 'Closer',
        funcao: 'Vendas',
        tipo: 'sales',
        linguagem: 'pt-BR',
        prompt: 'Atue em vendas',
        whatsapp: null,
        instagram: null,
        api: null,
        outros: null,
        outros_nome: null,
        ativo: true,
        created_at: new Date().toISOString(),
      },
    ],
    loading: false,
    saving: false,
    error: null,
    addAgent: vi.fn(async () => undefined),
    handleToggle: vi.fn(async () => undefined),
    reload: vi.fn(),
  }),
}));

import { AgentsPanel } from '../components/platform/AgentsPanel';

describe('AgentsPanel', () => {
  it('renderiza criacao e lista de agentes', () => {
    render(<AgentsPanel />);
    expect(screen.getByRole('heading', { name: /Criar agente/i })).toBeInTheDocument();
    expect(screen.getByText(/Seus agentes/i)).toBeInTheDocument();
  });
});
