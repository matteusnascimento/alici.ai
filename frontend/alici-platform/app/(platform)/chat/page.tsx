import Link from "next/link";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function ChatRoute() {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Chat</h1>
        <p className="text-sm text-slate-300">Entrada principal de conversas.</p>
        <Link href="/ai-studio/chat" className="inline-block rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white hover:bg-sky-400">
          Open AI Studio Chat
        </Link>
      </main>
    </DashboardLayout>
  );
}
