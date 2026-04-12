import { useEffect, useState } from 'react';

import { getConversationMessages, getConversations, sendMessage as sendChatMessage } from '../services/chat.service';
import type { ChatMessage, Conversation } from '../types/chat';

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadConversations() {
    setLoading(true);
    try {
      const list = await getConversations();
      setConversations(list);
      if (!selectedConversationId && list[0]) {
        setSelectedConversationId(list[0].id);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar conversas');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadConversations();
  }, []);

  useEffect(() => {
    async function loadMessages() {
      if (!selectedConversationId) {
        setMessages([]);
        return;
      }
      try {
        const list = await getConversationMessages(selectedConversationId);
        setMessages(list);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Falha ao carregar mensagens');
      }
    }
    void loadMessages();
  }, [selectedConversationId]);

  async function sendMessage(text: string) {
    setSending(true);
    try {
      const response = await sendChatMessage({
        text,
        conversation_id: selectedConversationId ?? undefined,
      });
      const assistantText = response.assistant_message?.text?.trim() || '';
      if (!assistantText) {
        throw new Error('A IA retornou resposta vazia. Tente novamente em instantes.');
      }
      setConversations((current) => {
        const existing = current.find((item) => item.id === response.conversation.id);
        if (existing) {
          return current;
        }
        return [response.conversation, ...current];
      });
      setSelectedConversationId(response.conversation.id);
      setMessages((current) => [...current, response.user_message, response.assistant_message]);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Falha ao enviar mensagem';
      setError(message);
      throw err;
    } finally {
      setSending(false);
    }
  }

  return {
    conversations,
    messages,
    selectedConversationId,
    setSelectedConversationId,
    loading,
    sending,
    error,
    reload: loadConversations,
    sendMessage,
  };
}
