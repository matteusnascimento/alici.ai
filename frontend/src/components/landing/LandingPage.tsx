import { motion } from 'framer-motion';
import { ArrowRight, BrainCircuit, ChartNoAxesCombined, ShieldCheck, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  {
    title: 'Operação centralizada',
    description: 'Chat, agentes, campanhas e conta AXI em um único cockpit operacional.',
    icon: BrainCircuit,
  },
  {
    title: 'Decisões orientadas por dados',
    description: 'Métricas de uso, receita e conversão alimentadas direto pela API.',
    icon: ChartNoAxesCombined,
  },
  {
    title: 'Acesso seguro',
    description: 'Autenticação JWT com proteção de rotas, persistência e invalidação de sessão.',
    icon: ShieldCheck,
  },
];

export function LandingPage() {
  return (
    <main className="min-h-screen bg-ink text-white">
      <section className="relative overflow-hidden px-6 py-16 md:px-12 lg:px-20">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(110,231,249,0.16),transparent_35%),radial-gradient(circle_at_bottom_right,rgba(216,181,107,0.16),transparent_30%)]" />
        <div className="absolute inset-0 bg-grid bg-[size:24px_24px] opacity-20" />
        <div className="relative mx-auto max-w-6xl">
          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm text-cyan">
              <Sparkles size={16} /> Plataforma SaaS AI pronta para operação inicial
            </div>
            <h1 className="font-display text-5xl leading-tight md:text-7xl">
              AXI transforma atendimento, agentes e marketing em execução conectada.
            </h1>
            <p className="mt-6 max-w-2xl text-lg text-slate-300 md:text-xl">
              Construa campanhas, opere agentes, acompanhe indicadores e converse com a Alici em um ambiente premium pensado para crescimento.
            </p>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Link className="inline-flex items-center justify-center gap-2 rounded-full bg-sand px-6 py-3 font-semibold text-ink transition hover:bg-white" to="/register">
                Criar conta <ArrowRight size={18} />
              </Link>
              <Link className="inline-flex items-center justify-center rounded-full border border-white/20 px-6 py-3 font-semibold text-white transition hover:border-cyan hover:text-cyan" to="/login">
                Fazer login
              </Link>
            </div>
          </motion.div>
          <div className="mt-16 grid gap-6 md:grid-cols-3">
            {features.map((feature, index) => (
              <motion.article
                key={feature.title}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="rounded-3xl border border-white/10 bg-white/6 p-6 shadow-soft backdrop-blur"
              >
                <feature.icon className="text-gold" size={26} />
                <h2 className="mt-4 font-display text-2xl">{feature.title}</h2>
                <p className="mt-3 text-slate-300">{feature.description}</p>
              </motion.article>
            ))}
          </div>
          <div className="mt-16 grid gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 lg:grid-cols-[1.3fr_1fr]">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-cyan">Benefícios imediatos</p>
              <h2 className="mt-4 font-display text-3xl md:text-4xl">Uma base funcional para operação real e deploy inicial.</h2>
            </div>
            <ul className="space-y-3 text-slate-200">
              <li>Cadastro e login com sessão restaurada.</li>
              <li>Área privada com rotas protegidas.</li>
              <li>Chat persistido, agentes persistidos e marketing operacional.</li>
              <li>Preparado para Render e Neon PostgreSQL.</li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
}
