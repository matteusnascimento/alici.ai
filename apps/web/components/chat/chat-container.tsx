"use client"

import { useState } from "react"

import ChatInput from "@/components/chat/chat-input"
import ChatMessage from "@/components/chat/chat-message"
import { sendMessage } from "@/lib/api"

export default function ChatContainer() {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([
    { role: "assistant", content: "Welcome to Alici chat" },
  ])

  async function onSend(value: string) {
    setMessages((prev) => [...prev, { role: "user", content: value }])
    const result = await sendMessage(value)
    setMessages((prev) => [...prev, { role: "assistant", content: result.response }])
  }

  return (
    <section className="flex h-[70vh] flex-col gap-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex-1 space-y-3 overflow-y-auto">
        {messages.map((item, idx) => (
          <ChatMessage key={`${item.role}-${idx}`} role={item.role} content={item.content} />
        ))}
      </div>
      <ChatInput onSend={onSend} />
    </section>
  )
}
