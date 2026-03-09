import Link from "next/link";
import type { Route } from "next";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-16">
      <h1 className="text-4xl font-bold tracking-tight">ALICI Platform</h1>
      <p className="max-w-2xl text-slate-300">
        Plataforma de IA com modulos operacionais, dashboard central e ferramentas
        de negocio em uma arquitetura SaaS.
      </p>
      <div className="flex gap-4">
        <Link
          href={"/dashboard" as Route}
          className="rounded-lg bg-sky-500 px-5 py-3 text-sm font-semibold text-white hover:bg-sky-400"
        >
          Comece Agora
        </Link>
      </div>
    </main>
  );
}
