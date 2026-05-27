import { motion, useInView } from 'framer-motion';
import {
  ArrowRight,
  Bot,
  CheckCircle2,
  ChevronRight,
  LayoutDashboard,
  LineChart,
  Megaphone,
  MessageCircle,
  PlayCircle,
  ShieldCheck,
  Sparkles,
  Star,
  Users,
  Wand2,
  Zap,
  type LucideIcon,
} from 'lucide-react';
import { useRef } from 'react';
import { Link } from 'react-router-dom';

interface FadeSectionProps {
  children: React.ReactNode;
  className?: string;
  id?: string;
}

interface FeatureItem {
  icon: LucideIcon;
  title: string;
  description: string;
}

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.45 },
  }),
};

function FadeSection({ children, className = '', ...rest }: FadeSectionProps) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <motion.section
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5 }}
      className={className}
      {...rest}
    >
      {children}
    </motion.section>
  );
}

const platformStats = [
  { label: 'Atendimento 24/7', value: '100%', detail: 'sem fila manual' },
  { label: 'Canais conectados', value: '4+', detail: 'WhatsApp, Instagram e mais' },
  { label: 'Tempo economizado', value: '80%', detail: 'menos rotina operacional' },
  { label: 'Setup inicial', value: '1h', detail: 'para comecar a vender' },
];

const pillars: FeatureItem[] = [
  {
    icon: MessageCircle,
    title: 'Atendimento omnichannel',
    description: 'Unifique WhatsApp, Instagram, Messenger, TikTok e webchat em uma conversa inteligente.',
  },
  {
    icon: Bot,
    title: 'Agentes que vendem',
    description: 'A IA responde, qualifica leads, entende contexto e entrega oportunidades para o time certo.',
  },
  {
    icon: Wand2,
    title: 'AXI Studio',
    description: 'Crie anuncios, videos, posts e campanhas com IA para acelerar marketing e vendas.',
  },
  {
    icon: LineChart,
    title: 'CRM e forecast',
    description: 'Transforme conversas em contatos, negocios, pipelines, receita prevista e indicadores reais.',
  },
  {
    icon: ShieldCheck,
    title: 'Controle e seguranca',
    description: 'Limites de uso, logs, billing, credito atomico, webhooks e integracoes oficiais por login.',
  },
  {
    icon: Megaphone,
    title: 'Campanhas prontas',
    description: 'Gere copy, CTA, segmentacao, respostas rapidas e criativos para canais sociais.',
  },
];

const workflow = [
  {
    step: '01',
    title: 'Conecte seus canais',
    description: 'O cliente autoriza as redes sociais com login oficial. A AXI recebe mensagens reais e organiza tudo no inbox.',
  },
  {
    step: '02',
    title: 'Treine sua operacao',
    description: 'Configure tom de voz, produtos, agenda, contratos, CRM, respostas rapidas e regras de escalada.',
  },
  {
    step: '03',
    title: 'Venda com IA',
    description: 'A plataforma atende, qualifica, cria campanhas, acompanha receita e mostra o que precisa de acao humana.',
  },
];

const testimonials = [
  {
    quote: 'A AXI tira o caos do WhatsApp e transforma conversa em pipeline real.',
    name: 'Operacao comercial',
    role: 'Atendimento e vendas',
  },
  {
    quote: 'O Studio ajuda a criar campanha sem depender de agencia para cada ideia nova.',
    name: 'Time de marketing',
    role: 'Criativos e anuncios',
  },
  {
    quote: 'A visao de receita, forecast e contatos deixa a gestao muito mais clara.',
    name: 'Gestao',
    role: 'Indicadores e crescimento',
  },
];

function ProductPreview() {
  return (
    <div className="relative">
      <div className="absolute -inset-6 rounded-[2.5rem] bg-[radial-gradient(circle_at_top_left,rgba(0,240,255,0.2),transparent_42%),radial-gradient(circle_at_bottom_right,rgba(160,32,240,0.2),transparent_46%)] blur-2xl" />
      <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-[#07111f] shadow-[0_34px_120px_rgba(0,0,0,0.5)]">
        <div className="flex items-center justify-between border-b border-white/10 bg-white/[0.04] px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-rose-400" />
            <span className="h-3 w-3 rounded-full bg-amber-300" />
            <span className="h-3 w-3 rounded-full bg-emerald-400" />
          </div>
          <span className="rounded-full border border-cyan/25 bg-cyan/10 px-3 py-1 text-xs font-semibold text-cyan">
            AXI ao vivo
          </span>
        </div>

        <div className="grid min-h-[420px] md:grid-cols-[190px_1fr]">
          <aside className="hidden border-r border-white/10 bg-black/20 p-4 md:block">
            <div className="mb-5 flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan text-ink">
                <Sparkles size={17} />
              </div>
              <div>
                <p className="text-sm font-black text-white">AXI Platform</p>
                <p className="text-xs text-slate-500">workspace</p>
              </div>
            </div>
            {['Dashboard', 'Chat', 'CRM', 'AXI Studio', 'Analises'].map((item, index) => (
              <div
                key={item}
                className={[
                  'mb-2 rounded-xl px-3 py-2 text-sm font-semibold',
                  index === 1 ? 'bg-cyan/15 text-cyan ring-1 ring-cyan/25' : 'text-slate-400',
                ].join(' ')}
              >
                {item}
              </div>
            ))}
          </aside>

          <div className="p-4 sm:p-5">
            <div className="mb-4 grid gap-3 sm:grid-cols-4">
              {platformStats.map((stat) => (
                <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">{stat.label}</p>
                  <p className="mt-2 text-2xl font-black text-white">{stat.value}</p>
                  <p className="text-[11px] text-cyan/80">{stat.detail}</p>
                </div>
              ))}
            </div>

            <div className="grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
              <div className="rounded-3xl border border-white/10 bg-black/25 p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.22em] text-cyan">Inbox inteligente</p>
                    <h3 className="mt-1 text-xl font-black text-white">Conversas viram vendas</h3>
                  </div>
                  <MessageCircle className="text-cyan" size={22} />
                </div>
                {[
                  ['WhatsApp', 'Cliente pediu preco do plano anual', 'IA respondeu em 4s'],
                  ['Instagram', 'Lead quer agendar demonstracao', 'Enviado para CRM'],
                  ['Webchat', 'Pergunta sobre suporte e garantia', 'Resolvido pela IA'],
                ].map(([channel, text, status]) => (
                  <div key={text} className="mb-3 rounded-2xl border border-white/10 bg-white/[0.04] p-3">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-bold text-white">{channel}</p>
                      <span className="rounded-full bg-emerald-400/10 px-2 py-1 text-[10px] font-bold text-emerald-300">
                        {status}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-400">{text}</p>
                  </div>
                ))}
              </div>

              <div className="space-y-4">
                <div className="rounded-3xl border border-white/10 bg-[linear-gradient(135deg,rgba(0,240,255,0.12),rgba(160,32,240,0.12))] p-4">
                  <p className="text-xs uppercase tracking-[0.22em] text-cyan">AXI Studio</p>
                  <h3 className="mt-1 text-xl font-black text-white">Criativos com IA</h3>
                  <div className="mt-4 grid grid-cols-3 gap-2">
                    {['Video', 'Post', 'Anuncio'].map((item) => (
                      <div key={item} className="rounded-2xl border border-white/10 bg-black/25 p-3 text-center">
                        <PlayCircle className="mx-auto text-cyan" size={20} />
                        <p className="mt-2 text-xs font-bold text-white">{item}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-4">
                  <p className="text-xs uppercase tracking-[0.22em] text-violet-200">Forecast</p>
                  <div className="mt-4 h-24 rounded-2xl bg-[linear-gradient(180deg,rgba(0,240,255,0.2),rgba(0,240,255,0.02))]">
                    <div className="flex h-full items-end gap-2 px-4 pb-4">
                      {[30, 55, 42, 76, 61, 88].map((height, index) => (
                        <span key={index} style={{ height: `${height}%` }} className="flex-1 rounded-t-lg bg-cyan/70" />
                      ))}
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-400">Receita, pipeline e oportunidades acompanhadas em tempo real.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function LandingPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-[#030711] text-white">
      <header className="sticky top-0 z-50 border-b border-white/[0.07] bg-[#030711]/82 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#00F0FF,#A020F0)] text-ink shadow-[0_0_30px_rgba(0,240,255,0.24)]">
              <Sparkles size={19} strokeWidth={2.7} />
            </div>
            <div>
              <p className="font-display text-xl font-black leading-none text-white">AXI</p>
              <p className="text-[10px] uppercase tracking-[0.24em] text-cyan">AI SaaS Platform</p>
            </div>
          </Link>

          <div className="hidden items-center gap-8 text-sm font-semibold text-slate-300 md:flex">
            <a href="#produto" className="transition hover:text-white">Produto</a>
            <a href="#como-funciona" className="transition hover:text-white">Como funciona</a>
            <a href="#recursos" className="transition hover:text-white">Recursos</a>
            <a href="#planos" className="transition hover:text-white">Planos</a>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/login" className="hidden rounded-full px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white sm:inline-flex">
              Entrar
            </Link>
            <Link
              to="/register"
              className="inline-flex items-center gap-2 rounded-full bg-cyan px-5 py-2.5 text-sm font-black text-ink shadow-[0_12px_36px_rgba(0,240,255,0.25)] transition hover:brightness-110"
            >
              Comecar agora <ArrowRight size={16} />
            </Link>
          </div>
        </nav>
      </header>

      <main>
        <section className="relative px-5 pb-20 pt-16 lg:px-8 lg:pb-28 lg:pt-24">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(0,240,255,0.16),transparent_34%),radial-gradient(circle_at_top_right,rgba(160,32,240,0.17),transparent_34%)]" />
          <div className="relative mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-[0.92fr_1.08fr]">
            <motion.div variants={fadeUp} initial="hidden" animate="show">
              <motion.div
                variants={fadeUp}
                custom={0}
                initial="hidden"
                animate="show"
                className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan/25 bg-cyan/10 px-4 py-2 text-sm font-bold text-cyan"
              >
                <Zap size={15} /> IA, atendimento, CRM e criativos em uma plataforma
              </motion.div>

              <motion.h1
                variants={fadeUp}
                custom={1}
                initial="hidden"
                animate="show"
                className="font-display text-5xl font-black leading-[1.04] tracking-tight text-white md:text-7xl"
              >
                Crie, Edite e{' '}
                <span className="bg-[linear-gradient(90deg,#00F0FF,#A020F0,#ffffff)] bg-clip-text text-transparent">
                  Revolucione
                </span>{' '}
                com IA.
              </motion.h1>

              <motion.p
                variants={fadeUp}
                custom={2}
                initial="hidden"
                animate="show"
                className="mt-6 max-w-2xl text-lg leading-8 text-slate-300 md:text-xl"
              >
                A AXI une agentes inteligentes, CRM, canais sociais e AXI Studio para sua empresa atender melhor,
                vender mais e criar campanhas profissionais sem aumentar o time.
              </motion.p>

              <motion.div
                variants={fadeUp}
                custom={3}
                initial="hidden"
                animate="show"
                className="mt-9 flex flex-col gap-3 sm:flex-row"
              >
                <Link
                  to="/register"
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-cyan px-8 py-4 text-base font-black text-ink shadow-[0_18px_48px_rgba(0,240,255,0.28)] transition hover:brightness-110"
                >
                  Testar gratis <ArrowRight size={18} />
                </Link>
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-white/18 bg-white/[0.04] px-8 py-4 text-base font-bold text-white transition hover:border-white/35 hover:bg-white/[0.08]"
                >
                  Ver plataforma <ChevronRight size={18} />
                </Link>
              </motion.div>

              <motion.div
                variants={fadeUp}
                custom={4}
                initial="hidden"
                animate="show"
                className="mt-8 flex flex-wrap gap-4 text-sm font-semibold text-slate-400"
              >
                {['Sem cartao para comecar', 'Login social', 'Canais oficiais', 'Pronto para vender'].map((item) => (
                  <span key={item} className="inline-flex items-center gap-2">
                    <CheckCircle2 size={15} className="text-emerald-300" /> {item}
                  </span>
                ))}
              </motion.div>
            </motion.div>

            <motion.div initial={{ opacity: 0, scale: 0.97, y: 22 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ delay: 0.18, duration: 0.55 }}>
              <ProductPreview />
            </motion.div>
          </div>
        </section>

        <FadeSection className="border-y border-white/[0.07] bg-white/[0.025] px-5 py-8 lg:px-8">
          <div className="mx-auto grid max-w-7xl gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {platformStats.map((stat) => (
              <div key={stat.label} className="rounded-3xl border border-white/10 bg-black/20 p-5">
                <p className="text-sm font-semibold text-slate-400">{stat.label}</p>
                <p className="mt-2 text-4xl font-black text-white">{stat.value}</p>
                <p className="mt-1 text-sm font-semibold text-cyan">{stat.detail}</p>
              </div>
            ))}
          </div>
        </FadeSection>

        <FadeSection id="produto" className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <div className="mb-12 max-w-3xl">
            <p className="text-sm font-black uppercase tracking-[0.28em] text-cyan">Produto</p>
            <h2 className="mt-3 font-display text-4xl font-black tracking-tight md:text-5xl">
              Uma operacao digital completa, nao apenas mais um chatbot.
            </h2>
            <p className="mt-5 text-lg leading-8 text-slate-400">
              A AXI combina atendimento, vendas, criacao de conteudo e analytics para que cada conversa vire dado,
              cada dado vire acao e cada acao gere crescimento.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {pillars.map((item, index) => {
              const Icon = item.icon;
              return (
                <motion.article
                  key={item.title}
                  initial={{ opacity: 0, y: 18 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.05 }}
                  className="group rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.055),rgba(255,255,255,0.025))] p-6 transition hover:-translate-y-1 hover:border-cyan/35"
                >
                  <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan/10 text-cyan ring-1 ring-cyan/20">
                    <Icon size={22} />
                  </div>
                  <h3 className="font-display text-xl font-black text-white">{item.title}</h3>
                  <p className="mt-3 text-sm leading-7 text-slate-400">{item.description}</p>
                </motion.article>
              );
            })}
          </div>
        </FadeSection>

        <FadeSection id="como-funciona" className="mx-auto max-w-7xl px-5 pb-24 lg:px-8">
          <div className="rounded-[2.5rem] border border-white/10 bg-[linear-gradient(135deg,rgba(0,240,255,0.08),rgba(160,32,240,0.08))] p-6 md:p-10">
            <div className="grid gap-10 lg:grid-cols-[0.72fr_1fr]">
              <div>
                <p className="text-sm font-black uppercase tracking-[0.28em] text-cyan">Como funciona</p>
                <h2 className="mt-3 font-display text-4xl font-black">Do primeiro login ao crescimento diario.</h2>
                <p className="mt-5 text-lg leading-8 text-slate-300">
                  A AXI foi desenhada para ser simples no comeco e poderosa quando sua operacao cresce.
                </p>
              </div>
              <div className="grid gap-4">
                {workflow.map((item) => (
                  <div key={item.step} className="rounded-3xl border border-white/10 bg-black/25 p-5">
                    <div className="flex gap-4">
                      <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-cyan text-base font-black text-ink">
                        {item.step}
                      </span>
                      <div>
                        <h3 className="font-display text-xl font-black text-white">{item.title}</h3>
                        <p className="mt-2 text-sm leading-7 text-slate-400">{item.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </FadeSection>

        <FadeSection id="recursos" className="mx-auto max-w-7xl px-5 pb-24 lg:px-8">
          <div className="grid gap-5 lg:grid-cols-[1fr_1fr]">
            <div className="rounded-[2rem] border border-white/10 bg-white/[0.035] p-7">
              <LayoutDashboard className="text-cyan" size={28} />
              <h2 className="mt-5 font-display text-3xl font-black">Painel claro para decisao rapida</h2>
              <p className="mt-4 text-slate-400">
                Veja contatos, negocios, contratos, ligacoes, receita, forecast e campanhas em modulos com proposito real.
              </p>
              <div className="mt-6 grid grid-cols-2 gap-3">
                {['CRM', 'Receita', 'Forecast', 'Studio'].map((item) => (
                  <span key={item} className="rounded-2xl border border-white/10 bg-black/25 px-4 py-3 text-sm font-bold text-white">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <div className="rounded-[2rem] border border-cyan/20 bg-[linear-gradient(160deg,rgba(0,240,255,0.13),rgba(160,32,240,0.08))] p-7">
              <Sparkles className="text-cyan" size={28} />
              <h2 className="mt-5 font-display text-3xl font-black">AXI Studio para criar e publicar</h2>
              <p className="mt-4 text-slate-300">
                Edite fotos, videos e criativos de campanha com fluxo inspirado em Canva e CapCut, mantendo sua marca.
              </p>
              <div className="mt-6 flex flex-wrap gap-2">
                {['Templates', 'Video', 'Foto', 'IA', 'Assets', 'Export'].map((item) => (
                  <span key={item} className="rounded-full border border-white/12 bg-black/25 px-4 py-2 text-sm font-bold text-white">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </FadeSection>

        <FadeSection className="mx-auto max-w-7xl px-5 pb-24 lg:px-8">
          <div className="mb-10 text-center">
            <p className="text-sm font-black uppercase tracking-[0.28em] text-cyan">Clientes ideais</p>
            <h2 className="mt-3 font-display text-4xl font-black">Feita para empresas que vivem de conversa e conversao.</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {testimonials.map((item) => (
              <article key={item.name} className="rounded-[2rem] border border-white/10 bg-white/[0.035] p-6">
                <div className="mb-4 flex gap-1 text-amber-300">
                  {Array.from({ length: 5 }).map((_, index) => <Star key={index} size={15} fill="currentColor" />)}
                </div>
                <p className="text-lg font-semibold leading-8 text-white">"{item.quote}"</p>
                <p className="mt-5 text-sm font-black text-cyan">{item.name}</p>
                <p className="text-sm text-slate-500">{item.role}</p>
              </article>
            ))}
          </div>
        </FadeSection>

        <FadeSection id="planos" className="mx-auto max-w-7xl px-5 pb-28 lg:px-8">
          <div className="overflow-hidden rounded-[2.5rem] border border-cyan/25 bg-[radial-gradient(circle_at_top_left,rgba(0,240,255,0.18),transparent_42%),linear-gradient(135deg,rgba(7,17,31,0.96),rgba(8,9,25,0.98))] p-8 text-center md:p-14">
            <p className="mx-auto mb-4 inline-flex items-center gap-2 rounded-full border border-cyan/25 bg-cyan/10 px-4 py-2 text-sm font-bold text-cyan">
              <Users size={15} /> Comece enxuto, escale quando vender mais
            </p>
            <h2 className="font-display text-4xl font-black md:text-6xl">
              Pronto para colocar a AXI trabalhando pela sua empresa?
            </h2>
            <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-300">
              Crie sua conta, conecte seus canais oficiais e comece a transformar atendimento em vendas com IA.
            </p>
            <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
              <Link to="/register" className="inline-flex items-center justify-center gap-2 rounded-full bg-cyan px-9 py-4 text-lg font-black text-ink shadow-[0_18px_48px_rgba(0,240,255,0.28)] transition hover:brightness-110">
                Criar conta gratis <ArrowRight size={20} />
              </Link>
              <Link to="/login" className="inline-flex items-center justify-center rounded-full border border-white/20 bg-white/[0.04] px-9 py-4 text-lg font-bold text-white transition hover:bg-white/[0.08]">
                Entrar na plataforma
              </Link>
            </div>
          </div>
        </FadeSection>
      </main>

      <footer className="border-t border-white/[0.07] px-5 py-10 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 text-sm text-slate-500 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-display text-lg font-black text-white">AXI</p>
            <p>Crie, Edite e Revolucione com IA.</p>
          </div>
          <p>© {new Date().getFullYear()} AXI. Todos os direitos reservados.</p>
          <div className="flex gap-5">
            <a href="#produto" className="hover:text-white">Produto</a>
            <a href="#planos" className="hover:text-white">Planos</a>
            <a href="#recursos" className="hover:text-white">Recursos</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
