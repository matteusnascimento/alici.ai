"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/services/api";
import { setSessionTokens } from "@/services/authSession";

interface RegisterResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data } = await api.post<RegisterResponse>("/auth/register", {
        full_name: fullName,
        email,
        password,
        organization_name: organizationName || undefined
      });
      setSessionTokens(data.access_token, data.refresh_token);
      localStorage.setItem("token", data.access_token);
      router.push("/dashboard");
    } catch (err) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(message ?? "Não foi possível criar a conta. Verifique os dados e tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-sky-400">ALICI</h1>
          <p className="mt-1 text-sm text-slate-400">Crie sua conta</p>
        </div>

        <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
          {error && (
            <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
              {error}
            </p>
          )}

          <div>
            <label htmlFor="full_name" className="mb-1 block text-xs text-slate-400">
              Nome completo
            </label>
            <input
              id="full_name"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
              placeholder="Seu nome"
            />
          </div>

          <div>
            <label htmlFor="email" className="mb-1 block text-xs text-slate-400">
              E-mail
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
              placeholder="seu@email.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-xs text-slate-400">
              Senha
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label htmlFor="organization_name" className="mb-1 block text-xs text-slate-400">
              Nome da organização <span className="text-slate-500">(opcional)</span>
            </label>
            <input
              id="organization_name"
              type="text"
              value={organizationName}
              onChange={(e) => setOrganizationName(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
              placeholder="Minha Empresa"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-sky-500 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:opacity-60"
          >
            {loading ? "Criando conta..." : "Criar conta"}
          </button>
        </form>

        <p className="text-center text-xs text-slate-500">
          Já tem conta?{" "}
          <a href="/login" className="text-sky-400 hover:underline">
            Entrar
          </a>
        </p>
      </div>
    </div>
  );
}
