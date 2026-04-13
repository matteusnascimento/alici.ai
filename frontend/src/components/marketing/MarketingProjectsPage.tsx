import { Plus, Trash2, Pencil, Megaphone, Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { MarketingProject, MarketingProjectCreate } from '../../types/marketing';
import { createProject, deleteProject, listProjects } from '../../services/marketing.service';

export function MarketingProjectsPage() {
  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState<MarketingProjectCreate>({
    name: '',
    audience: '',
    objective: '',
    offer: '',
    tone: 'premium',
    notes: '',
  });
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    listProjects()
      .then(setProjects)
      .catch(() => setError('Erro ao carregar projetos'))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      const p = await createProject(form);
      setProjects((prev) => [p, ...prev]);
      setForm({ name: '', audience: '', objective: '', offer: '', tone: 'premium', notes: '' });
    } catch {
      setError('Erro ao criar projeto');
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Remover projeto?')) return;
    await deleteProject(id);
    setProjects((prev) => prev.filter((p) => p.id !== id));
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 size={24} className="animate-spin text-cyan" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8 space-y-8">
      {/* Create form */}
      <section className="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 className="mb-4 text-lg font-semibold text-white">Novo Projeto de Marketing</h2>
        <form onSubmit={handleCreate} className="grid gap-3 sm:grid-cols-2">
          <input
            required
            placeholder="Nome do projeto"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
          />
          <input
            required
            placeholder="Público-alvo"
            value={form.audience}
            onChange={(e) => setForm((f) => ({ ...f, audience: e.target.value }))}
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
          />
          <input
            required
            placeholder="Objetivo"
            value={form.objective}
            onChange={(e) => setForm((f) => ({ ...f, objective: e.target.value }))}
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
          />
          <input
            required
            placeholder="Oferta / produto"
            value={form.offer}
            onChange={(e) => setForm((f) => ({ ...f, offer: e.target.value }))}
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
          />
          <select
            value={form.tone}
            onChange={(e) => setForm((f) => ({ ...f, tone: e.target.value }))}
            className="rounded-xl border border-white/10 bg-storm px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"
          >
            {['premium', 'casual', 'urgente', 'educativo', 'inspirador'].map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input
            placeholder="Notas adicionais (opcional)"
            value={form.notes ?? ''}
            onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
          />
          <div className="sm:col-span-2 flex justify-end">
            <button
              type="submit"
              disabled={creating}
              className="flex items-center gap-2 rounded-xl bg-cyan px-5 py-2 text-sm font-semibold text-ink hover:bg-cyan/90 disabled:opacity-50"
            >
              {creating ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
              Criar Projeto
            </button>
          </div>
        </form>
        {error && <p className="mt-2 text-xs text-red-400">{error}</p>}
      </section>

      {/* List */}
      <section className="space-y-3">
        <h2 className="text-sm uppercase tracking-[0.25em] text-slate-400">Seus Projetos ({projects.length})</h2>
        {projects.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/5 py-16 gap-3 text-slate-400">
            <Megaphone size={32} />
            <p className="text-sm">Nenhum projeto ainda. Crie o primeiro acima.</p>
          </div>
        ) : (
          projects.map((p) => (
            <div
              key={p.id}
              className="flex items-start justify-between rounded-2xl border border-white/10 bg-white/5 px-5 py-4 hover:bg-white/8 transition-colors"
            >
              <div className="space-y-1">
                <p className="font-semibold text-white">{p.name}</p>
                <p className="text-xs text-slate-400">{p.objective} · {p.audience}</p>
                <p className="text-xs text-slate-500">Oferta: {p.offer} · Tom: {p.tone}</p>
                {p.notes && <p className="text-xs text-slate-500 italic">{p.notes}</p>}
              </div>
              <div className="flex items-center gap-2 ml-4">
                <button
                  onClick={() => navigate(`/app/marketing/copy?project=${p.id}`)}
                  className="rounded-lg border border-cyan/30 px-3 py-1.5 text-xs text-cyan hover:bg-cyan/10"
                >
                  Gerar Copy
                </button>
                <button
                  onClick={() => navigate(`/app/marketing/campaign?project=${p.id}`)}
                  className="rounded-lg border border-white/15 px-3 py-1.5 text-xs text-slate-300 hover:bg-white/5"
                >
                  <Pencil size={12} />
                </button>
                <button
                  onClick={() => handleDelete(p.id)}
                  className="rounded-lg border border-red-500/30 px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/10"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
