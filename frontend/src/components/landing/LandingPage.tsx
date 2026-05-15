import { motion, useInView } from 'framer-motion';
import {
  ArrowRight,
  Bot,
  ChartNoAxesCombined,
  CheckCircle2,
  MessageCircle,
  Rocket,
  Sparkles,
  Zap,
  Shield,
  Users,
  TrendingUp,
  Clock,
  Star,
} from 'lucide-react';
import { useRef } from 'react';
import { Link } from 'react-router-dom';

interface FadeSectionProps {
  children: React.ReactNode;
  className?: string;
  id?: string;
}

const fadeUp = {
  hidden: { opacity: 0, y: 22 },
  show: (i = 0) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.45 } }),
};

function FadeSection({ children, className = '', ...rest }: FadeSectionProps) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5 }}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

const stats = [
  { label: 'Conversas automatizadas', value: '18.420', delta: '+32% em 30 dias', color: 'text-emerald-300' },
  { label: 'Leads qualificados', value: '1.284', delta: 'Fluxo ativo', color: 'text-cyan' },
  { label: 'Horas poupadas/mês', value: '340h', delta: 'Por cliente médio', color: 'text-violet-300' },
  { label: 'Taxa de resposta', value: '100%', delta: '24h por dia', color: 'text-amber-300' },
];

const useCases = [
  {
    title: 'Atendimento automático',
    description: 'Responda clientes instantaneamente no WhatsApp, Instagram e webchat — sem nenhum atendente online.',
    icon: MessageCircle,
    tag: 'Atendimento',
    tagColor: 'border-cyan/30 bg-cyan/10 text-cyan',
  },
  {
    title: 'Geração de vendas',
    description: 'Qualifique leads, responda objeções e conduza o cliente até a compra com fluxos de IA treinados para vender.',
    icon: TrendingUp,
    tag: 'Vendas',
    tagColor: 'border-emerald-400/30 bg-emerald-500/10 text-emerald-300',
  },
  {
    title: 'Campanhas com IA',
    description: 'Crie campanhas completas — copy, estratégia e execução — em minutos sem depender de agência.',
    icon: Rocket,
    tag: 'Marketing',
    tagColor: 'border-violet-400/30 bg-violet-500/10 text-violet-300',
  },
];

const steps = [
  {
    num: '01',
    title: 'Crie seu agente em minutos',
    description: 'Defina identidade, tom de voz e objetivo. A IA aprende como sua empresa fala e vende.',
    icon: Bot,
  },
  {
    num: '02',
    title: 'Conecte seus canais',
    description: 'WhatsApp, Instagram e webchat ativos sem setup complexo. Tudo centralizado no mesmo painel.',
    icon: Zap,
  },
  {
    num: '03',
    title: 'Automatize e escale',
    description: 'Respostas, qualificação e campanhas rodando 24h — sem time dedicado, sem custo operacional extra.',
    icon: ChartNoAxesCombined,
  },
];

const capabilities = [
  { icon: Bot, title: 'Agentes de IA configuráveis', description: 'Crie múltiplos agentes com personalidades e objetivos diferentes para cada área do negócio.' },
  { icon: MessageCircle, title: 'Omnichannel real', description: 'WhatsApp, Instagram e webchat integrados em um inbox unificado com histórico completo.' },
  { icon: Rocket, title: 'Campanhas inteligentes', description: 'Planeje e execute campanhas de marketing com geração de copy e automação por IA.' },
  { icon: Shield, title: 'Controle e segurança', description: 'Defina limites de comportamento, filtros de conteúdo e regras de escalada para humanos.' },
  { icon: Users, title: 'Gestão de leads', description: 'Qualifique e segmente automaticamente com base em intenção e comportamento de conversa.' },
  { icon: Star, title: 'Análise e métricas', description: 'Dashboard com volume de conversas, taxa de resposta, leads gerados e performance por canal.' },
];

const benefits = [
  'Reduza até 80% do trabalho manual de atendimento',
  'Responda clientes 24h por dia, 7 dias por semana',
  'Aumente conversão com respostas rápidas e personalizadas',
  'Centralize canais, campanhas e análises em um painel único',
  'Escale sem contratar mais atendentes',
  'Setup completo em menos de 1 hora',
];

export function LandingPage() {
  return (
    <div className="min-h-screen bg-ink text-white">
      {/* ── NAV ── */}
      <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-ink/80 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan text-ink">
              <Bot size={17} strokeWidth={2.5} />
            </div>
            <span className="font-display text-lg font-bold tracking-tight text-white">Alici</span>
          </div>
          <div className="hidden items-center gap-8 text-sm text-slate-300 md:flex">
            <a href="#como-funciona" className="transition hover:text-white">Como funciona</a>
            <a href="#features" className="transition hover:text-white">Features</a>
            <a href="#beneficios" className="transition hover:text-white">Benefícios</a>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="hidden text-sm text-slate-300 transition hover:text-white sm:block">Entrar</Link>
            <Link
              to="/register"
              className="inline-flex items-center gap-1.5 rounded-full bg-cyan px-5 py-2 text-sm font-semibold text-ink shadow-[0_8px_24px_rgba(34,211,238,0.28)] transition hover:brightness-110"
            >
              Começar grátis <ArrowRight size={14} />
            </Link>
          </div>
        </nav>
      </header>

      <main>
        {/* ── HERO ── */}
        <section className="relative overflow-hidden px-6 pb-24 pt-20 md:px-12 lg:px-20">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-10%,rgba(34,211,238,0.18),transparent)]" />
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_80%_50%,rgba(59,130,246,0.14),transparent_50%)]" />
          <div className="relative mx-auto max-w-6xl">
            <div className="grid items-center gap-14 lg:grid-cols-[1.15fr_1fr]">
              {/* Left */}
              <motion.div variants={fadeUp} initial="hidden" animate="show">
                <motion.div
                  variants={fadeUp}
                  custom={0}
                  initial="hidden"
                  animate="show"
                  className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan/25 bg-cyan/10 px-4 py-1.5 text-sm text-cyan"
                >
                  <Sparkles size={14} strokeWidth={2.5} />
                  Automação com IA para negócios reais
                </motion.div>

                <motion.h1
                  variants={fadeUp}
                  custom={0.5}
                  initial="hidden"
                  animate="show"
                  className="font-display text-[2.6rem] font-extrabold leading-[1.12] tracking-tight md:text-6xl"
                >
                  Sua empresa{' '}
                  <span className="bg-gradient-to-r from-cyan via-sky-300 to-blue-400 bg-clip-text text-transparent">
                    atendendo, vendendo
                  </span>
                  {' '}e crescendo 24h — no piloto automático.
                </motion.h1>

                <motion.p
                  variants={fadeUp}
                  custom={1}
                  initial="hidden"
                  animate="show"
                  className="mt-6 max-w-xl text-lg leading-relaxed text-slate-300"
                >
                  Crie agentes de IA que respondem clientes, qualificam leads e executam campanhas. Tudo centralizado, sem precisar de equipe extra.
                </motion.p>

                <motion.div
                  variants={fadeUp}
                  custom={1.5}
                  initial="hidden"
                  animate="show"
                  className="mt-10 flex flex-col gap-3 sm:flex-row"
                >
                  <Link
                    to="/register"
                    className="inline-flex items-center justify-center gap-2 rounded-full bg-cyan px-8 py-3.5 font-semibold text-ink shadow-[0_12px_36px_rgba(34,211,238,0.34)] transition hover:brightness-110 active:scale-95"
                  >
                    Começar grátis — sem cartão <ArrowRight size={17} />
                  </Link>
                  <Link
                    to="/login"
                    className="inline-flex items-center justify-center rounded-full border border-white/18 px-8 py-3.5 font-semibold text-white transition hover:border-white/35 hover:bg-white/[0.05]"
                  >
                    Já tenho conta
                  </Link>
                </motion.div>

                <motion.div
                  variants={fadeUp}
                  custom={2}
                  initial="hidden"
                  animate="show"
                  className="mt-8 flex flex-wrap items-center gap-4 text-sm text-slate-400"
                >
                  <span className="flex items-center gap-1.5"><CheckCircle2 size={14} className="text-emerald-400" /> Grátis para começar</span>
                  <span className="flex items-center gap-1.5"><CheckCircle2 size={14} className="text-emerald-400" /> Setup em menos de 1h</span>
                  <span className="flex items-center gap-1.5"><CheckCircle2 size={14} className="text-emerald-400" /> Sem contrato de fidelidade</span>
                </motion.div>
              </motion.div>

              {/* Right — Dashboard preview */}
              <motion.div
                initial={{ opacity: 0, y: 28, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ delay: 0.2, duration: 0.55 }}
                className="relative"
              >
                <div className="rounded-[2rem] border border-white/12 bg-[linear-gradient(155deg,rgba(10,20,44,0.98),rgba(7,14,32,0.96))] p-1 shadow-[0_32px_96px_rgba(0,0,0,0.5),0_0_0_1px_rgba(255,255,255,0.05)]">
                  <div className="rounded-[1.75rem] border border-white/[0.07] bg-white/[0.02] p-5">
                    {/* Header bar */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-emerald-400" />
                        <span className="text-xs text-slate-300">Painel operacional</span>
                      </div>
                      <span className="rounded-full border border-emerald-400/25 bg-emerald-500/12 px-2.5 py-0.5 text-[11px] text-emerald-300">
                        3 agentes online
                      </span>
                    </div>

                    {/* Stats */}
                    <div className="mt-4 grid grid-cols-2 gap-3">
                      {stats.map((s) => (
                        <div key={s.label} className="rounded-2xl border border-white/[0.07] bg-black/25 p-4">
                          <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">{s.label}</p>
                          <p className="mt-2 text-2xl font-bold text-white">{s.value}</p>
                          <p className={`mt-0.5 text-[11px] ${s.color}`}>{s.delta}</p>
                        </div>
                      ))}
                    </div>

                    {/* Activity */}
                    <div className="mt-3 rounded-2xl border border-white/[0.07] bg-black/20 p-4">
                      <p className="mb-3 text-[10px] uppercase tracking-[0.18em] text-slate-500">Última atividade</p>
                      {[
                        { name: 'Ana Souza', msg: 'Quero saber mais sobre o plano...', time: '2 min', color: 'bg-cyan' },
                        { name: 'Carlos M.', msg: 'Já recebi o link de pagamento?', time: '5 min', color: 'bg-emerald-400' },
                        { name: 'Julia R.', msg: 'Perfeito! Vou fechar agora.', time: '8 min', color: 'bg-violet-400' },
                      ].map((item) => (
                        <div key={item.name} className="flex items-start gap-3 py-1.5">
                          <div className={`mt-0.5 h-2 w-2 shrink-0 rounded-full ${item.color}`} />
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-xs text-slate-200">{item.name} <span className="text-slate-500">· {item.time}</span></p>
                            <p className="truncate text-[11px] text-slate-400">{item.msg}</p>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Channels */}
                    <div className="mt-3 flex flex-wrap gap-2">
                      {['WhatsApp', 'Instagram', 'Webchat', 'Campanhas IA'].map((ch, i) => (
                        <span
                          key={ch}
                          className={`rounded-full border px-3 py-1 text-[11px] ${i === 3 ? 'border-cyan/30 bg-cyan/10 text-cyan' : 'border-white/10 bg-black/20 text-slate-300'}`}
                        >
                          {ch}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                {/* Glow */}
                <div className="pointer-events-none absolute -bottom-10 left-1/2 h-40 w-3/4 -translate-x-1/2 rounded-full bg-cyan/10 blur-3xl" />
              </motion.div>
            </div>
          </div>
        </section>

        {/* ── STATS BAR ── */}
        <FadeSection>
          <section className="border-y border-white/[0.07] bg-white/[0.02] px-6 py-8 md:px-12">
            <div className="mx-auto grid max-w-6xl grid-cols-2 gap-6 md:grid-cols-4">
              {[
                { value: '18k+', label: 'Conversas/mês', icon: MessageCircle },
                { value: '80%', label: 'Menos trabalho manual', icon: Clock },
                { value: '24h', label: 'Atendimento ininterrupto', icon: Zap },
                { value: '1h', label: 'Setup completo', icon: Rocket },
              ].map((item) => (
                <div key={item.label} className="flex flex-col items-center gap-1 text-center">
                  <item.icon size={18} className="text-cyan opacity-70" />
                  <p className="font-display text-3xl font-bold text-white">{item.value}</p>
                  <p className="text-sm text-slate-400">{item.label}</p>
                </div>
              ))}
            </div>
          </section>
        </FadeSection>

        <div className="mx-auto max-w-6xl px-6 md:px-12 lg:px-20">
          {/* ── USE CASES ── */}
          <FadeSection className="mt-24">
            <div className="mb-10 text-center">
              <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan">O que você pode fazer</p>
              <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-white md:text-4xl">
                Um sistema para atendimento, vendas e marketing.
              </h2>
            </div>
            <div className="grid gap-6 md:grid-cols-3">
              {useCases.map((uc, i) => (
                <motion.article
                  key={uc.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="group relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.05] to-white/[0.02] p-7 transition duration-300 hover:border-white/20 hover:shadow-[0_0_36px_rgba(34,211,238,0.07)]"
                >
                  <div className="mb-5 flex items-center justify-between">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.07]">
                      <uc.icon size={21} className="text-cyan" />
                    </div>
                    <span className={`rounded-full border px-2.5 py-1 text-[11px] font-medium ${uc.tagColor}`}>
                      {uc.tag}
                    </span>
                  </div>
                  <h3 className="font-display text-xl font-bold text-white">{uc.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-slate-400">{uc.description}</p>
                </motion.article>
              ))}
            </div>
          </FadeSection>

          {/* ── COMO FUNCIONA ── */}
          <FadeSection className="mt-28" id="como-funciona">
            <div className="mb-12 text-center">
              <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan">Como funciona</p>
              <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-white md:text-4xl">
                3 passos para sua operação rodar sozinha.
              </h2>
            </div>
            <div className="relative grid gap-6 md:grid-cols-3">
              {/* Connector line */}
              <div className="absolute left-0 right-0 top-11 hidden h-px bg-gradient-to-r from-transparent via-white/15 to-transparent md:block" />
              {steps.map((step, i) => (
                <motion.div
                  key={step.num}
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.15 }}
                  className="relative rounded-3xl border border-white/10 bg-white/[0.03] p-7"
                >
                  <div className="mb-5 flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-cyan/30 bg-cyan/10">
                      <step.icon size={17} className="text-cyan" />
                    </div>
                    <span className="font-mono text-3xl font-bold text-white/10">{step.num}</span>
                  </div>
                  <h3 className="font-display text-xl font-bold text-white">{step.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-slate-400">{step.description}</p>
                </motion.div>
              ))}
            </div>
          </FadeSection>

          {/* ── BENEFÍCIOS ── */}
          <FadeSection className="mt-28" id="beneficios">
            <div className="overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/[0.06] via-white/[0.03] to-transparent">
              <div className="grid gap-10 p-8 lg:grid-cols-[1.1fr_1fr] lg:p-12">
                <div>
                  <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan">Resultados reais</p>
                  <h2 className="mt-4 font-display text-3xl font-extrabold leading-tight text-white md:text-4xl">
                    Impacto direto no atendimento e nas vendas — desde o primeiro dia.
                  </h2>
                  <p className="mt-5 text-slate-400">
                    Negócios que usam Alici param de perder clientes por demora na resposta e passam a operar com escala real sem aumentar o time.
                  </p>
                  <Link
                    to="/register"
                    className="mt-8 inline-flex items-center gap-2 rounded-full bg-cyan px-7 py-3.5 font-semibold text-ink shadow-[0_10px_28px_rgba(34,211,238,0.3)] transition hover:brightness-110"
                  >
                    Quero começar agora <ArrowRight size={17} />
                  </Link>
                </div>
                <ul className="flex flex-col justify-center space-y-4">
                  {benefits.map((item) => (
                    <li key={item} className="flex items-start gap-3">
                      <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-emerald-400/30 bg-emerald-500/15">
                        <CheckCircle2 size={11} className="text-emerald-300" />
                      </div>
                      <span className="text-slate-200">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </FadeSection>

          {/* ── CAPABILITIES ── */}
          <FadeSection className="mt-28" id="features">
            <div className="mb-10 text-center">
              <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan">O que está incluído</p>
              <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-white md:text-4xl">
                Tudo para operar IA com resultado real.
              </h2>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {capabilities.map((cap, i) => (
                <motion.article
                  key={cap.title}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.07 }}
                  className="rounded-2xl border border-white/8 bg-white/[0.03] p-6 transition duration-300 hover:border-cyan/25 hover:bg-white/[0.06]"
                >
                  <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.06]">
                    <cap.icon size={18} className="text-cyan" />
                  </div>
                  <h3 className="font-display text-lg font-bold text-white">{cap.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">{cap.description}</p>
                </motion.article>
              ))}
            </div>
          </FadeSection>

          {/* ── CTA FINAL ── */}
          <FadeSection className="mb-24 mt-24">
            <div className="relative overflow-hidden rounded-[2.5rem] border border-cyan/25 bg-[radial-gradient(ellipse_100%_120%_at_50%_120%,rgba(34,211,238,0.18),transparent_70%),linear-gradient(160deg,rgba(10,20,50,0.95),rgba(7,14,32,0.98))] px-8 py-16 text-center shadow-[0_0_80px_rgba(34,211,238,0.08)]">
              <div className="pointer-events-none absolute inset-0 rounded-[2.5rem] border border-cyan/10" />
              <motion.div
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                <p className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan/25 bg-cyan/10 px-4 py-1.5 text-sm text-cyan">
                  <Sparkles size={13} /> Sem cartão de crédito — comece agora
                </p>
                <h2 className="mt-2 font-display text-3xl font-extrabold text-white md:text-5xl">
                  Comece grátis e coloque{' '}
                  <span className="bg-gradient-to-r from-cyan to-sky-300 bg-clip-text text-transparent">
                    sua operação no piloto automático.
                  </span>
                </h2>
                <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-300">
                  Alici foi feita para tirar você da operação manual e colocar IA para gerar resposta, conversão e escala — de verdade.
                </p>
                <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
                  <Link
                    to="/register"
                    className="inline-flex items-center gap-2 rounded-full bg-cyan px-9 py-4 text-lg font-bold text-ink shadow-[0_14px_44px_rgba(34,211,238,0.38)] transition hover:brightness-110 active:scale-95"
                  >
                    Criar conta grátis <ArrowRight size={20} />
                  </Link>
                  <Link
                    to="/login"
                    className="inline-flex items-center gap-2 rounded-full border border-white/20 px-9 py-4 text-lg font-semibold text-white transition hover:border-white/40 hover:bg-white/[0.07]"
                  >
                    Já tenho conta
                  </Link>
                </div>
                <p className="mt-6 text-sm text-slate-500">Setup em menos de 1 hora · Sem contrato · Cancele quando quiser</p>
              </motion.div>
            </div>
          </FadeSection>
        </div>
      </main>

      {/* ── FOOTER ── */}
      <footer className="border-t border-white/[0.07] bg-ink px-6 py-10 md:px-12">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-6 md:flex-row">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan text-ink">
              <Bot size={14} strokeWidth={2.5} />
            </div>
            <span className="font-display font-bold text-white">Alici</span>
          </div>
          <p className="text-sm text-slate-500">© {new Date().getFullYear()} Alici. Todos os direitos reservados.</p>
          <div className="flex items-center gap-6 text-sm text-slate-500">
            <a href="#" className="transition hover:text-slate-300">Termos</a>
            <a href="#" className="transition hover:text-slate-300">Privacidade</a>
            <a href="#" className="transition hover:text-slate-300">Suporte</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
