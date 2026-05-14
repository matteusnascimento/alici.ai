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

import { ChatPanel } from '../components/platform/ChatPanel';

describe('ChatPanel', () => {
  it('mostra erro amigavel de IA quando backend falha', () => {
    chatHookState.error = 'A integracao de IA nao esta configurada.';
    render(<ChatPanel />);

    expect(screen.getByText(/A integracao de IA nao esta configurada/i)).toBeInTheDocument();
    chatHookState.error = null;
  });

  it('envia mensagem usando o hook', async () => {
    chatHookState.error = null;
    render(<ChatPanel />);

    await userEvent.type(screen.getByPlaceholderText(/Descreva sua necessidade/i), 'Quero uma campanha');
    await userEvent.click(screen.getByRole('button', { name: /Enviar/i }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Enviar/i })).toBeInTheDocument();
    });
  });
});
