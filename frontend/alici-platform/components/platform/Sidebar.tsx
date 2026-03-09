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
    <aside className="flex w-[260px] flex-col gap-4 border-r bg-white p-4">
      <div className="text-2xl font-bold">ALICI</div>

      <nav className="mt-4 flex flex-col gap-2">
        {menu.map((item) => {
          const Icon = item.icon;

          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center gap-2 rounded px-3 py-2 ${
                isActive(item.path)
                  ? "bg-gray-900 text-white"
                  : "text-gray-800 hover:bg-gray-100"
              }`}
            >
              <Icon size={18} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto text-xs text-gray-400">AI Platform</div>
    </aside>
  );
}
