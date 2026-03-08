import Link from "next/link";
import type { Route } from "next";

const sections = [
  {
    title: "Plataforma",
    links: [
      { href: "/dashboard", label: "Dashboard" },
      { href: "/agents", label: "Agents" },
      { href: "/workflows", label: "Workflows" },
      { href: "/billing", label: "Billing" },
      { href: "/integrations", label: "Integrations" }
    ]
  },
  {
    title: "AI Studio",
    links: [
      { href: "/ai-studio/chat", label: "Chat" },
      { href: "/prompts", label: "Prompts" },
      { href: "/settings", label: "Settings" }
    ]
  }
] as const satisfies ReadonlyArray<{
  title: string;
  links: ReadonlyArray<{ href: Route; label: string }>;
}>;

export function Sidebar() {
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
              {section.links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-lg px-3 py-2 text-sm text-slate-200 hover:bg-slate-800"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}
