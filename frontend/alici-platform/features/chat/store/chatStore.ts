import { create } from "zustand";
import type { ChatMessage, Conversation } from "@/types/api";

interface ChatState {
  conversations: Conversation[];
  messages: ChatMessage[];
  selectedConversationId: string | null;
  setConversations: (conversations: Conversation[]) => void;
  setMessages: (messages: ChatMessage[]) => void;
  setSelectedConversationId: (id: string | null) => void;
  appendMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, patch: Partial<ChatMessage>) => void;
  removeMessages: (ids: string[]) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  messages: [],
  selectedConversationId: null,
  setConversations: (conversations) => set({ conversations }),
  setMessages: (messages) => set({ messages }),
  setSelectedConversationId: (selectedConversationId) => set({ selectedConversationId }),
  appendMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  updateMessage: (id, patch) =>
    set((state) => ({
      messages: state.messages.map((msg) => (msg.id === id ? { ...msg, ...patch } : msg))
    })),
  removeMessages: (ids) =>
    set((state) => ({
      messages: state.messages.filter((msg) => !ids.includes(msg.id))
    }))
}));
