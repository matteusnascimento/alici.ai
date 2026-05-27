import { ArrowRight, Link2, MessageCircle, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export function AccountAppsPage() {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan/25 bg-cyan/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.22em] text-cyan">
            <ShieldCheck size={14} /> Conexoes oficiais
          </div>
          <h2 className="mt-4 font-display text-2xl text-white">Apps e canais</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Para evitar duplicidade e configuracoes conflitantes, todas as conexoes de WhatsApp, Instagram,
            Messenger e TikTok ficam na central unica de integracoes.
          </p>
        </div>
        <Link
          to="/app/integrations"
          className="inline-flex items-center justify-center gap-2 rounded-2xl bg-cyan px-5 py-3 text-sm font-black text-ink shadow-[0_16px_34px_rgb(var(--accent-rgb)/0.25)] transition hover:bg-white"
        >
          <Link2 size={17} /> Abrir integracoes <ArrowRight size={16} />
        </Link>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-3">
        {['WhatsApp Business', 'Instagram Messaging', 'Facebook Messenger'].map((item) => (
          <div key={item} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <MessageCircle className="text-cyan" size={20} />
            <p className="mt-3 text-sm font-semibold text-white">{item}</p>
            <p className="mt-1 text-xs leading-5 text-slate-500">Conectado por OAuth oficial na central unica.</p>
          </div>
        ))}
      </div>
    </section>
  );
}
