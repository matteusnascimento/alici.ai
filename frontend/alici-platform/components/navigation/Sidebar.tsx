"use client";

import Link from "next/link";
import type { Route } from "next";
import { usePathname } from "next/navigation";
import {
  Bot,
  Cpu,
  CreditCard,
  Database,
  Home,
  MessageSquare,
  Plug,
  Settings,
  Wrench
} from "lucide-react";

const sections = [
  {
    title: "ALICI Platform",
    links: [
      { href: "/platform", label: "Platform Home" },
      { href: "/dashboard", label: "Dashboard" },
      { href: "/chat", label: "Chat" },
      { href: "/agents", label: "Agents" },
      { href: "/knowledge", label: "Knowledge" },
      { href: "/models", label: "Models" },
      { href: "/tools", label: "Tools" },
      { href: "/integrations", label: "Integrations" },
      { href: "/billing", label: "Billing" },
      { href: "/settings", label: "Settings" }
    ]
  }
] as const satisfies ReadonlyArray<{
  title: string;
  links: ReadonlyArray<{ href: string; label: string }>;
}>;

function getIcon(label: string) {
  switch (label) {
    case "Platform Home":
    case "Dashboard":
      return Home;
    case "Chat":
      return MessageSquare;
    case "Agents":
      return Bot;
    case "Knowledge":
      return Database;
    case "Models":
      return Cpu;
    case "Tools":
      return Wrench;
    case "Integrations":
      return Plug;
    case "Billing":
      return CreditCard;
    case "Settings":
      return Settings;
    default:
      return Home;
  }
}

function isRouteActive(pathname: string, href: string) {
  if (href === "/platform") return pathname === "/platform";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-72 border-r border-slate-800 bg-slate-950/70 px-5 py-6">
      <div className="mb-8 text-lg font-bold tracking-wide text-sky-400">ALICI</div>
      <nav className="space-y-8">
        {sections.map((section) => (
          <div key={section.title}>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
              {section.title}
            </p>
            <div className="flex flex-col gap-2">
              {section.links.map((link) => {
                const Icon = getIcon(link.label);
                const active = isRouteActive(pathname, link.href);

                return (
                  <Link
                    key={link.href}
                    href={link.href as Route}
                    className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
                      active
                        ? "bg-sky-500/20 text-sky-300 ring-1 ring-sky-500/40"
                        : "text-slate-200 hover:bg-slate-800"
                    }`}
                  >
                    <Icon size={16} />
                    <span>{link.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}
