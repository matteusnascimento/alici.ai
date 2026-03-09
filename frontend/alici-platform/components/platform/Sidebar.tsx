"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, MessageSquare, Bot, Database, Cpu, Wrench, Plug, CreditCard, Settings, Brain, History, User } from "lucide-react";

const menu = [
  { name: "Dashboard", icon: Home, path: "/dashboard" },
  { name: "Chat", icon: MessageSquare, path: "/chat" },
  { name: "Agents", icon: Bot, path: "/agents" },
  { name: "Memória Neural", icon: Brain, path: "/memory" },
  { name: "Histórico", icon: History, path: "/history" },
  { name: "Knowledge", icon: Database, path: "/knowledge" },
  { name: "Models", icon: Cpu, path: "/models" },
  { name: "Tools", icon: Wrench, path: "/tools" },
  { name: "Integrations", icon: Plug, path: "/integrations" },
  { name: "Billing", icon: CreditCard, path: "/billing" },
  { name: "Perfil", icon: User, path: "/profile" },
  { name: "Settings", icon: Settings, path: "/settings" }
] as const;

export default function Sidebar() {
  const pathname = usePathname();

  function isActive(path: string) {
    return pathname === path || pathname.startsWith(`${path}/`);
  }

  return (
    <aside className="flex w-[260px] flex-col gap-4 border-r border-slate-800 bg-slate-950 p-4">
      <div className="text-2xl font-bold text-sky-400">ALICI</div>

      <nav className="mt-4 flex flex-col gap-1">
        {menu.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
                isActive(item.path)
                  ? "bg-sky-500/20 text-sky-300 ring-1 ring-sky-500/40"
                  : "text-slate-200 hover:bg-slate-800"
              }`}
            >
              <Icon size={16} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto text-xs text-slate-500">AI Platform</div>
    </aside>
  );
}
