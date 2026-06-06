import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

const chatHookState = {
  conversations: [],
  messages: [],
  selectedConversationId: null,
  setSelectedConversationId: vi.fn(),
  loading: false,
  sending: false,
  error: null as string | null,
  sendMessage: vi.fn(async () => undefined),
};

vi.mock('../hooks/useChat', () => ({
  useChat: () => ({
    ...chatHookState,
  }),
}));

vi.mock('../services/chats.service', () => ({
  getChatChannels: () => Promise.resolve([]),
}));

vi.mock('../services/revenue.service', () => ({
  getRevenueIntelligence: () => Promise.resolve(null),
}));

import { AxiAssistantPage } from '../components/platform/AxiAssistantPage';

describe('AxiAssistantPage', () => {
  beforeEach(() => {
    chatHookState.error = null;
    chatHookState.sendMessage.mockClear();
  });

  it('mostra erro amigavel de IA quando backend falha', async () => {
    chatHookState.error = 'A integracao de IA nao esta configurada.';
    render(<AxiAssistantPage />);

    expect(await screen.findByText(/A integracao de IA nao esta configurada/i)).toBeInTheDocument();
  });

  it('envia mensagem usando o hook', async () => {
    render(<AxiAssistantPage />);

    await userEvent.type(screen.getByPlaceholderText(/Pergunte sobre dados/i), 'Quero uma campanha');
    await userEvent.click(screen.getByRole('button', { name: /Enviar/i }));

    await waitFor(() => {
      expect(chatHookState.sendMessage).toHaveBeenCalledWith('Quero uma campanha');
    });
  });
});
