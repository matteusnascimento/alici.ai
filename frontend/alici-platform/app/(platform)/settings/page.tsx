"use client";

import { useEffect, useState } from "react";
import { Settings } from "lucide-react";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { Card, CardContent } from "@/components/ui/Card";
import { api } from "@/services/api";

interface UserSettings {
  language: string | null;
  theme: string | null;
  notifications_enabled: boolean | null;
  api_key_alias: string | null;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const res = await api.get<UserSettings>("/user/settings");
        if (active) setSettings(res.data);
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
    if (!settings) return;
    setSaving(true);
    setSaved(false);
    try {
      await api.put("/user/settings", settings);
      setSaved(true);
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  return (
    <DashboardLayout>
      <section className="space-y-6">
        <header>
          <div className="flex items-center gap-3">
            <Settings size={24} className="text-slate-400" />
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-400">Conta</p>
              <h1 className="text-2xl font-semibold">Configurações</h1>
            </div>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Personalize sua experiência na plataforma ALICI.
          </p>
        </header>

        {loading ? (
          <p className="text-sm text-slate-400">Carregando configurações...</p>
        ) : !settings ? (
          <p className="text-sm text-red-400">Não foi possível carregar as configurações.</p>
        ) : (
          <Card>
            <CardContent>
              <form onSubmit={(e) => void handleSave(e)} className="space-y-5">
                <div>
                  <label htmlFor="language" className="mb-1 block text-xs text-slate-400">
                    Idioma
                  </label>
                  <select
                    id="language"
                    value={settings.language ?? "pt-BR"}
                    onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                    className="w-full max-w-xs rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                  >
                    <option value="pt-BR">Português (Brasil)</option>
                    <option value="en-US">English (US)</option>
                    <option value="es-ES">Español</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="theme" className="mb-1 block text-xs text-slate-400">
                    Tema
                  </label>
                  <select
                    id="theme"
                    value={settings.theme ?? "dark"}
                    onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                    className="w-full max-w-xs rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                  >
                    <option value="dark">Escuro</option>
                    <option value="light">Claro</option>
                  </select>
                </div>

                <div className="flex items-center gap-3">
                  <input
                    id="notifications"
                    type="checkbox"
                    checked={settings.notifications_enabled ?? true}
                    onChange={(e) =>
                      setSettings({ ...settings, notifications_enabled: e.target.checked })
                    }
                    className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-sky-500"
                  />
                  <label htmlFor="notifications" className="text-sm text-slate-200">
                    Notificações ativadas
                  </label>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    type="submit"
                    disabled={saving}
                    className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:opacity-60"
                  >
                    {saving ? "Salvando..." : "Salvar configurações"}
                  </button>
                  {saved && (
                    <span className="text-xs text-emerald-400">Salvo com sucesso!</span>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        )}
      </section>
    </DashboardLayout>
  );
}

