"use client";

import { useEffect, useState } from "react";
import { getConversations, getConversationMessages } from "@/services/chatService";
import { useChatStore } from "@/features/chat/store/chatStore";

/**
 * Hook: useChat
 * Description: Load conversation list and messages for the selected conversation.
 * Follows the standard loading / error / data pattern.
 *
 * Parameters:
 *   selectedConversationId: active conversation to load messages for.
 */
export function useChat(selectedConversationId?: string | null) {
  const { conversations, messages, setConversations, setMessages } = useChatStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load conversation list on mount.
  useEffect(() => {
    let active = true;

    async function loadConversations() {
      setLoading(true);
      setError(null);
      try {
        const list = await getConversations();
        if (active) setConversations(list);
      } catch {
        if (active) setError("Failed to load conversations");
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadConversations();
    return () => {
      active = false;
    };
  }, [setConversations]);

  // Load messages whenever the selected conversation changes.
  useEffect(() => {
    if (!selectedConversationId) {
      setMessages([]);
      return;
    }

    const conversationId = selectedConversationId;
    let active = true;

    async function loadMessages() {
      setLoading(true);
      setError(null);
      try {
        const list = await getConversationMessages(conversationId);
        if (active) setMessages(list);
      } catch {
        if (active) setError("Failed to load messages");
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadMessages();
    return () => {
      active = false;
    };
  }, [selectedConversationId, setMessages]);

  return {
    loading,
    error,
    data: { conversations, messages },
    conversations,
    messages
  };
}
