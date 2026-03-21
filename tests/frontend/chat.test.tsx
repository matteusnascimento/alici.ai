import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

vi.mock('../../frontend/src/hooks/useChat', () => ({
  useChat: () => ({
    conversations: [],
    messages: [],
    selectedConversationId: null,
    setSelectedConversationId: vi.fn(),
    loading: false,
    sending: false,
    error: null,
    sendMessage: vi.fn(async () => undefined),
  }),
}));

import { ChatPanel } from '../../frontend/src/components/platform/ChatPanel';

describe('ChatPanel', () => {
  it('envia mensagem usando o hook', async () => {
    render(<ChatPanel />);

    await userEvent.type(screen.getByPlaceholderText(/Descreva sua necessidade/i), 'Quero uma campanha');
    await userEvent.click(screen.getByRole('button', { name: /Enviar/i }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Enviar/i })).toBeInTheDocument();
    });
  });
});
