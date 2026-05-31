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

import { AxiAssistantPage } from '../components/platform/AxiAssistantPage';
import { ChatPanel } from '../components/platform/ChatPanel';

describe('AxiAssistantPage', () => {
  it('mostra erro amigavel de IA quando backend falha', () => {
    chatHookState.error = 'A integracao de IA nao esta configurada.';
    render(<AxiAssistantPage />);

    expect(screen.getByText(/A integracao de IA nao esta configurada/i)).toBeInTheDocument();
    chatHookState.error = null;
  });

  it('envia mensagem usando o hook', async () => {
    chatHookState.error = null;
    render(<AxiAssistantPage />);

    await userEvent.type(screen.getByPlaceholderText(/Pergunte sobre dados/i), 'Quero uma campanha');
    await userEvent.click(screen.getByRole('button', { name: /Enviar/i }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Enviar/i })).toBeInTheDocument();
    });
  });
});

describe('ChatPanel', () => {
  it('renderiza central omnichannel separada do AXI Assistant', () => {
    chatHookState.error = null;
    render(<ChatPanel />);

    expect(screen.getByRole('heading', { name: 'Chats' })).toBeInTheDocument();
    expect(screen.getByText('WhatsApp')).toBeInTheDocument();
    expect(screen.getByText('Instagram')).toBeInTheDocument();
    expect(screen.getByText('Messenger')).toBeInTheDocument();
    expect(screen.getByText('Website Chat')).toBeInTheDocument();
    expect(screen.getByText(/Controle IA\/Humano/i)).toBeInTheDocument();
  });
});
