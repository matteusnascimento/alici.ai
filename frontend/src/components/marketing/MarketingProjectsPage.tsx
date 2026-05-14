import { Bot, Loader2, Megaphone, Pencil, Plus, Rocket, Sparkles, Trash2, Wand2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import type { MarketingProject, MarketingProjectCreate } from '../../types/marketing';
import { createProject, deleteProject, listProjects } from '../../services/marketing.service';

const toneStyles: Record<string, string> = {
  premium: 'Premium e sofisticado',
  casual: 'Leve e proximo',
  urgente: 'Urgencia comercial',
  educativo: 'Didatico e confiavel',
  inspirador: 'Inspiracional e humano',
};

function buildPreview(form: MarketingProjectCreate) {
  const business = form.name.trim() || 'Sua marca';
  const audience = form.audience.trim() || 'seu publico ideal';
  const objective = form.objective.trim() || 'gerar crescimento';
  const offer = form.offer.trim() || 'sua oferta principal';
  const toneLabel = toneStyles[form.tone || 'premium'] || toneStyles.premium;

  return {
    headline: `${business}: campanha para ${objective.toLowerCase()}`,
    primaryCopy: `A ${business} ajuda ${audience} a conquistar resultados com ${offer}. Estruturamos uma campanha orientada a conversao com narrativa ${toneLabel.toLowerCase()} e foco em acao imediata.`,
    cta: `Quero conhecer ${business}`,
    idea: `Sequencia recomendada: Hook direto + prova social + oferta + CTA. Canal inicial: Instagram/Reels com reforco em WhatsApp para fechamento.`,
    postStructure: ['Hook de impacto', 'Problema real do publico', 'Solucao com oferta', 'Prova e credibilidade', 'CTA final'],
  };
}

function autofillFromQuickIdea(idea: string, currentTone: string): MarketingProjectCreate {
  const text = idea.trim();
  const lower = text.toLowerCase();

  const isHotel = lower.includes('hotel') || lower.includes('pousada') || lower.includes('hospedagem');
  const isClinic = lower.includes('clinica') || lower.includes('estetica') || lower.includes('odont');
  const isRestaurant = lower.includes('restaurante') || lower.includes('delivery') || lower.includes('food');

  if (isHotel) {
    return {
      name: 'Campanha Hospedagem IA',
      audience: 'Casais e familias buscando viagem curta',
      objective: 'Aumentar reservas diretas',
      offer: 'Pacote de hospedagem com beneficios exclusivos',
      tone: currentTone || 'premium',
      notes: text,
    };
  }

  if (isClinic) {
    return {
      name: 'Campanha Conversao Clinica',
      audience: 'Adultos interessados em procedimentos com seguranca',
      objective: 'Gerar agendamentos qualificados',
      offer: 'Consulta avaliativa com condicao especial',
      tone: currentTone || 'premium',
      notes: text,
    };
  }

  if (isRestaurant) {
    return {
      name: 'Campanha Delivery Performance',
      audience: 'Moradores da regiao com interesse em entrega rapida',
      objective: 'Aumentar pedidos no horario de pico',
      offer: 'Combo promocional com tempo limitado',
      tone: currentTone || 'urgente',
      notes: text,
    };
  }

  return {
    name: 'Projeto de Marketing IA',
    audience: 'Publico com alta chance de compra',
    objective: 'Gerar demanda e conversao',
    offer: 'Oferta principal da marca',
    tone: currentTone || 'premium',
    notes: text,
  };
}

export function MarketingProjectsPage() {
  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [quickIdea, setQuickIdea] = useState('');
  const [quickLoading, setQuickLoading] = useState(false);
  const [form, setForm] = useState<MarketingProjectCreate>({
    name: '',
    audience: '',
    objective: '',
    offer: '',
    tone: 'premium',
    notes: '',
  });
  const navigate = useNavigate();
  const preview = buildPreview(form);

  useEffect(() => {
    setLoading(true);
    listProjects()
      .then((rows) => {
        setProjects(Array.isArray(rows) ? rows : []);
        setError(null);
      })
      .catch(() => {
        setError('Erro ao carregar projetos');
        setProjects([]);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError(null);
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

  function handleQuickGenerate() {
    if (!quickIdea.trim()) {
      setError('Descreva sua ideia para ativar a geracao rapida.');
      return;
    }

    setQuickLoading(true);
    setError(null);

    // Simula preenchimento inteligente da IA sem depender de endpoint extra.
    const next = autofillFromQuickIdea(quickIdea, form.tone || 'premium');
    setForm(next);

    setTimeout(() => {
      setQuickLoading(false);
    }, 250);
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
    <div className="mx-auto max-w-7xl px-6 py-8 space-y-8">
      <section className="relative overflow-hidden rounded-3xl border border-cyan-300/20 bg-[radial-gradient(circle_at_15%_20%,rgba(6,182,212,0.25),transparent_35%),radial-gradient(circle_at_85%_0%,rgba(14,116,144,0.35),transparent_30%),linear-gradient(160deg,#041022,#0b1d3a)] p-6 md:p-8">
        <div className="absolute -right-8 top-1/2 hidden h-36 w-36 -translate-y-1/2 rounded-full bg-cyan-400/20 blur-3xl md:block" />
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-cyan-200">
              <Sparkles size={14} className="animate-pulse" /> AXI Studio - Marketing AI
            </p>
            <h1 className="mt-3 font-display text-4xl leading-tight text-white md:text-5xl">
              Crie campanhas inteligentes com IA
            </h1>
            <p className="mt-3 max-w-3xl text-sm text-slate-200 md:text-base">
              Transforme um briefing simples em campanhas prontas para publicar. Defina o contexto e acompanhe o preview estrategico em tempo real.
            </p>
          </div>
          <button
            type="button"
            onClick={handleQuickGenerate}
            disabled={quickLoading}
            className="group inline-flex items-center gap-2 rounded-2xl border border-cyan-300/40 bg-cyan-400/15 px-4 py-2.5 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {quickLoading ? <Loader2 size={15} className="animate-spin" /> : <Wand2 size={15} className="transition group-hover:rotate-12" />}
            Geracao rapida
          </button>
        </div>

        <div className="mt-6 rounded-2xl border border-white/15 bg-white/5 p-4 backdrop-blur">
          <label className="mb-2 block text-sm font-medium text-slate-100">Descreva sua ideia em uma frase</label>
          <div className="flex flex-col gap-2 md:flex-row">
            <input
              value={quickIdea}
              onChange={(e) => setQuickIdea(e.target.value)}
              placeholder="Ex: Quero vender hospedagem de pousada para casais no fim de semana"
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/25"
            />
            <button
              type="button"
              onClick={handleQuickGenerate}
              disabled={quickLoading}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan px-4 py-2.5 text-sm font-semibold text-ink transition hover:bg-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {quickLoading ? <Loader2 size={14} className="animate-spin" /> : <Rocket size={14} />}
              Gerar automatico
            </button>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <article className="rounded-3xl border border-white/10 bg-[linear-gradient(170deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))] p-6 shadow-[0_20px_50px_rgba(0,0,0,0.35)]">
          <div className="mb-4 flex items-center gap-2">
            <Bot size={16} className="text-cyan" />
            <h2 className="text-lg font-semibold text-white">Entrada estratégica</h2>
          </div>

          <form onSubmit={handleCreate} className="grid gap-4 sm:grid-cols-2">
            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-100">Nome do projeto</span>
              <input
                required
                placeholder="Ex: Campanha Black Week"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder:text-slate-500 transition focus:border-cyan/60 focus:outline-none focus:ring-2 focus:ring-cyan/25"
              />
            </label>

            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-100">Publico-alvo</span>
              <input
                required
                placeholder="Ex: PMEs de servicos"
                value={form.audience}
                onChange={(e) => setForm((f) => ({ ...f, audience: e.target.value }))}
                className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder:text-slate-500 transition focus:border-cyan/60 focus:outline-none focus:ring-2 focus:ring-cyan/25"
              />
            </label>

            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-100">Objetivo</span>
              <input
                required
                placeholder="Ex: Gerar leads qualificados"
                value={form.objective}
                onChange={(e) => setForm((f) => ({ ...f, objective: e.target.value }))}
                className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder:text-slate-500 transition focus:border-cyan/60 focus:outline-none focus:ring-2 focus:ring-cyan/25"
              />
            </label>

            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-100">Produto / Oferta</span>
              <input
                required
                placeholder="Ex: Plano anual com bonus"
                value={form.offer}
                onChange={(e) => setForm((f) => ({ ...f, offer: e.target.value }))}
                className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder:text-slate-500 transition focus:border-cyan/60 focus:outline-none focus:ring-2 focus:ring-cyan/25"
              />
            </label>

            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-100">Nivel de comunicacao</span>
              <select
                value={form.tone}
                onChange={(e) => setForm((f) => ({ ...f, tone: e.target.value }))}
                className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white transition focus:border-cyan/60 focus:outline-none focus:ring-2 focus:ring-cyan/25"
              >
                {['premium', 'casual', 'urgente', 'educativo', 'inspirador'].map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>

            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-100">Contexto adicional</span>
              <input
                placeholder="Ex: campanha focada em WhatsApp"
                value={form.notes ?? ''}
                onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
                className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder:text-slate-500 transition focus:border-cyan/60 focus:outline-none focus:ring-2 focus:ring-cyan/25"
              />
            </label>

            <div className="sm:col-span-2 flex justify-end">
              <button
                type="submit"
                disabled={creating}
                className="group flex items-center gap-2 rounded-xl bg-cyan px-5 py-2.5 text-sm font-semibold text-ink transition hover:bg-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creating ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} className="transition group-hover:rotate-90" />}
                Gerar campanha com IA
              </button>
            </div>
          </form>

          {error ? <p className="mt-3 text-xs text-rose-300">{error}</p> : null}
        </article>

        <aside className="rounded-3xl border border-cyan-400/20 bg-[linear-gradient(165deg,rgba(12,20,45,0.95),rgba(6,15,35,0.92))] p-6 shadow-[0_18px_45px_rgba(0,0,0,0.35)]">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Preview da IA</h2>
            <span className="inline-flex items-center gap-1 rounded-full border border-cyan-300/30 bg-cyan-500/10 px-2.5 py-1 text-xs text-cyan-100">
              <Sparkles size={12} /> Atualizacao ao digitar
            </span>
          </div>

          <div className="space-y-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-cyan-300/30">
              <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Titulo sugerido</p>
              <p className="mt-2 text-base font-semibold text-white">{preview.headline}</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-cyan-300/30">
              <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Copy principal</p>
              <p className="mt-2 text-sm text-slate-200">{preview.primaryCopy}</p>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-cyan-300/30">
                <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">CTA</p>
                <p className="mt-2 text-sm font-semibold text-white">{preview.cta}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-cyan-300/30">
                <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Ideia de campanha</p>
                <p className="mt-2 text-sm text-slate-200">{preview.idea}</p>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-cyan-300/30">
              <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Estrutura de post</p>
              <ul className="mt-2 space-y-1 text-sm text-slate-200">
                {preview.postStructure.map((item) => (
                  <li key={item}>- {item}</li>
                ))}
              </ul>
            </div>
          </div>
        </aside>
      </section>

      <section className="space-y-3">
        {/* KPI strip — aparece quando há projetos */}
        {projects.length > 0 && (
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-1.5 rounded-2xl border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-200">
              <Megaphone size={13} className="text-cyan-300" />
              {projects.length} {projects.length === 1 ? 'projeto' : 'projetos'}
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-2xl border border-emerald-400/25 bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-200">
              <Sparkles size={13} className="text-emerald-300" />
              Ativos
            </span>
          </div>
        )}

        <h2 className="text-sm uppercase tracking-[0.25em] text-slate-400">Projetos ativos ({projects.length})</h2>
        {projects.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-3xl border border-cyan-300/20 bg-[linear-gradient(160deg,rgba(8,24,48,0.8),rgba(4,18,33,0.85))] py-14 text-center">
            <Megaphone size={34} className="text-cyan-300" />
            <p className="mt-3 text-lg font-semibold text-white">Voce ainda nao criou campanhas</p>
            <p className="mt-1 max-w-xl text-sm text-slate-300">
              Crie seu primeiro projeto com IA e veja sugestoes instantaneas para copy, CTA e estrutura de publicacao.
            </p>
            <button
              type="button"
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              className="mt-4 inline-flex items-center gap-2 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink hover:bg-cyan/90"
            >
              <Rocket size={14} /> Criar campanha
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {projects.map((p) => (
              <div
                key={p.id}
                className="group flex flex-col justify-between rounded-2xl border border-white/10 bg-[linear-gradient(160deg,rgba(7,14,32,0.95),rgba(10,24,48,0.9))] p-5 shadow-[0_8px_24px_rgba(0,0,0,0.3)] transition hover:-translate-y-0.5 hover:border-cyan-300/25 hover:shadow-[0_12px_32px_rgba(0,0,0,0.4)]"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-semibold leading-snug text-white">{p.name}</p>
                    <span className="shrink-0 rounded-full border border-cyan-300/25 bg-cyan-500/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-cyan-200">
                      {p.tone}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300">{p.objective}</p>
                  <p className="text-xs text-slate-400">Público: {p.audience}</p>
                  <p className="text-xs text-slate-400">Oferta: {p.offer}</p>
                  {p.notes ? <p className="text-xs italic text-slate-500">{p.notes}</p> : null}
                </div>
                <div className="mt-4 flex items-center gap-2 border-t border-white/10 pt-3">
                  <button
                    onClick={() => navigate(`/app/marketing/copy?project=${p.id}`)}
                    className="inline-flex items-center gap-1 rounded-lg border border-cyan/30 bg-cyan/5 px-3 py-1.5 text-xs font-semibold text-cyan transition hover:bg-cyan/15"
                  >
                    <Sparkles size={11} /> Gerar Copy
                  </button>
                  <button
                    onClick={() => navigate(`/app/marketing/campaign?project=${p.id}`)}
                    className="rounded-lg border border-white/15 p-1.5 text-slate-300 transition hover:bg-white/10"
                    title="Editar"
                  >
                    <Pencil size={12} />
                  </button>
                  <button
                    onClick={() => handleDelete(p.id)}
                    className="ml-auto rounded-lg border border-rose-500/30 p-1.5 text-rose-300 transition hover:bg-rose-500/10"
                    title="Remover"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
