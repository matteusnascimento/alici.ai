import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-16">
      <h1 className="text-4xl font-bold tracking-tight">ALICI Platform</h1>
      <p className="max-w-2xl text-slate-300">
        Base profissional para evoluir a plataforma com arquitetura por features,
        design system e camadas claras de dominio, aplicacao e infraestrutura.
      </p>
      <div className="flex gap-4">
        <Link
          href="/dashboard"
          className="rounded-lg bg-sky-500 px-5 py-3 text-sm font-semibold text-white hover:bg-sky-400"
        >
          Ir para Dashboard
        </Link>
      </div>
    </main>
  );
}
