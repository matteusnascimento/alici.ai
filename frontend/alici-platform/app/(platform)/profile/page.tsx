"use client";

import { useEffect, useState } from "react";
import { User, Mail, Building, Calendar } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { api } from "@/services/api";

interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  plan: string | null;
  organization_id: string | null;
  created_at: string | null;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [fullName, setFullName] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const res = await api.get<UserProfile>("/user");
        if (active) {
          setProfile(res.data);
          setFullName(res.data.full_name ?? "");
        }
      } catch {
        // ignore
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      await api.put("/user", { full_name: fullName });
      setProfile((prev) => (prev ? { ...prev, full_name: fullName } : prev));
      setSaved(true);
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  return (
      <section className="space-y-6">
        <header>
          <div className="flex items-center gap-3">
            <User size={24} className="text-sky-400" />
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-400">Conta</p>
              <h1 className="text-2xl font-semibold">Perfil</h1>
            </div>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Gerencie suas informações de perfil e configurações de conta.
          </p>
        </header>

        {loading ? (
          <p className="text-sm text-slate-400">Carregando perfil...</p>
        ) : !profile ? (
          <p className="text-sm text-red-400">Não foi possível carregar o perfil.</p>
        ) : (
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardContent>
                <h2 className="mb-4 text-sm font-semibold text-slate-200">Informações da Conta</h2>
                <ul className="space-y-4">
                  <li className="flex items-start gap-3">
                    <Mail size={16} className="mt-0.5 shrink-0 text-slate-400" />
                    <div>
                      <p className="text-xs text-slate-400">E-mail</p>
                      <p className="text-sm text-slate-100">{profile.email}</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <Building size={16} className="mt-0.5 shrink-0 text-slate-400" />
                    <div>
                      <p className="text-xs text-slate-400">Plano</p>
                      <p className="text-sm text-slate-100 capitalize">{profile.plan ?? "—"}</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <Calendar size={16} className="mt-0.5 shrink-0 text-slate-400" />
                    <div>
                      <p className="text-xs text-slate-400">Membro desde</p>
                      <p className="text-sm text-slate-100">
                        {profile.created_at
                          ? new Date(profile.created_at).toLocaleDateString("pt-BR")
                          : "—"}
                      </p>
                    </div>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <h2 className="mb-4 text-sm font-semibold text-slate-200">Editar Perfil</h2>
                <form onSubmit={(e) => void handleSave(e)} className="space-y-4">
                  <div>
                    <label
                      htmlFor="full_name"
                      className="mb-1 block text-xs text-slate-400"
                    >
                      Nome completo
                    </label>
                    <input
                      id="full_name"
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                    />
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      type="submit"
                      disabled={saving}
                      className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:opacity-60"
                    >
                      {saving ? "Salvando..." : "Salvar"}
                    </button>
                    {saved && (
                      <span className="text-xs text-emerald-400">Salvo com sucesso!</span>
                    )}
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </section>
  );
}
