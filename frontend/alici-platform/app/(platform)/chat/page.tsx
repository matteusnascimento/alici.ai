"use client";

import { ChatWorkspace } from "@/components/chat/ChatWorkspace";
import { MessageSquare } from "lucide-react";

export default function ChatRoute() {
  return (
    <section className="flex min-h-[calc(100vh-140px)] flex-col gap-4">
      <header className="flex items-center gap-3">
        <MessageSquare size={22} className="text-sky-400" />
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">AI Studio</p>
          <h1 className="text-2xl font-semibold">Chat</h1>
        </div>
      </header>

      <ChatWorkspace />
    </section>
  );
}
