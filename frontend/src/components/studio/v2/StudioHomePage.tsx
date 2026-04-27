import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

const cn = (...c: Array<string | undefined | null | false>) => c.filter(Boolean).join(' ');

type Screen = 'home' | 'editor';
type Tool = 'Editar' | 'Áudio' | 'Texto' | 'Efeitos' | 'Camadas' | 'Legendas';

const quickTools = [
  { name: 'AutoCut', icon: '▣' },
  { name: 'Retoque', icon: '✦' },
  { name: 'Espaço', icon: '☁' },
  { name: 'Gerador de IA', icon: '▱' },
  { name: 'Aprimorar', icon: '✧' },
  { name: 'Ferramentas de foto', icon: '▧' },
  { name: 'Marketing', icon: '▤' },
  { name: 'Desktop', icon: '▥' },
  { name: 'Remover fundo', icon: '◌' },
  { name: 'Legendas', icon: 'CC' },
  { name: 'Câmera', icon: '◉' },
  { name: 'Áudio', icon: '♪' },
];

const editorTools: Tool[] = ['Editar', 'Áudio', 'Texto', 'Efeitos', 'Camadas', 'Legendas'];

function Home({ go }: { go: (s: Screen) => void }) {
  return (
    <div className="min-h-screen overflow-hidden bg-[#f7fbff] text-[#101522]">
      <div className="mx-auto flex min-h-screen max-w-[980px] flex-col px-8 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-500">AXI Studio</div>
            <h1 className="mt-2 text-4xl font-black tracking-tight">Criar com IA</h1>
          </div>
          <button className="rounded-full bg-[#101522] px-5 py-2 text-sm font-semibold text-white shadow-lg">Pro</button>
        </div>

        <div className="mb-7 grid grid-cols-[1.2fr_0.8fr] gap-5">
          <button
            onClick={() => go('editor')}
            className="group rounded-[28px] bg-gradient-to-br from-[#dceeff] to-[#b9d7f4] p-7 text-left shadow-[0_24px_70px_rgba(58,99,145,0.18)] transition hover:-translate-y-1 hover:shadow-[0_30px_90px_rgba(58,99,145,0.25)]"
          >
            <div className="mb-10 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0b1020] text-3xl font-black text-white">+</div>
            <div className="text-2xl font-black">Novo vídeo</div>
            <div className="mt-1 text-sm font-medium text-slate-600">Importe mídia ou comece do zero</div>
          </button>

          <button
            onClick={() => go('editor')}
            className="group rounded-[28px] bg-gradient-to-br from-[#e7f4ff] to-[#c8def4] p-7 text-left shadow-[0_24px_70px_rgba(58,99,145,0.16)] transition hover:-translate-y-1 hover:shadow-[0_30px_90px_rgba(58,99,145,0.23)]"
          >
            <div className="mb-10 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0b1020] text-2xl text-white">▧</div>
            <div className="text-2xl font-black">Editar foto</div>
            <div className="mt-1 text-sm font-medium text-slate-600">Retoque, fundo e ajustes</div>
          </button>
        </div>

        <div className="mb-8 flex gap-4 overflow-hidden">
          {[
            'bg-[linear-gradient(135deg,#132033,#415f83)]',
            'bg-[linear-gradient(135deg,#e9eef6,#c6d8f0)]',
            'bg-[linear-gradient(135deg,#0e1628,#41d8ee)]',
            'bg-[linear-gradient(135deg,#f4f8ff,#d9e8f5)]',
          ].map((bg, i) => (
            <div key={i} className={cn('h-24 min-w-24 rounded-3xl shadow-[0_20px_50px_rgba(21,38,66,0.12)]', bg)}>
              {i < 3 ? <div className="ml-2 mt-16 rounded-full bg-black/55 px-2 py-1 text-xs font-bold text-white">0{i + 12}</div> : null}
            </div>
          ))}
        </div>

        <div className="grid flex-1 grid-cols-3 gap-x-8 gap-y-8 pb-24">
          {quickTools.map((tool) => (
            <button key={tool.name} className="group flex flex-col items-center text-center transition hover:-translate-y-1">
              <div className="mb-3 flex h-[72px] w-[72px] items-center justify-center rounded-[24px] bg-white text-2xl font-black text-[#333946] shadow-[0_15px_45px_rgba(48,63,88,0.12)] ring-1 ring-slate-200/70 transition group-hover:ring-cyan-300/70">
                {tool.icon}
              </div>
              <span className="max-w-[120px] text-lg font-bold leading-tight text-[#343842]">{tool.name}</span>
            </button>
          ))}
        </div>

        <div className="fixed bottom-0 left-0 right-0 border-t border-slate-200 bg-white/95 backdrop-blur-xl">
          <div className="mx-auto grid max-w-[980px] grid-cols-5 px-6 py-3 text-center text-sm font-bold text-slate-400">
            {[
              ['✂', 'Editar', true],
              ['▯', 'Modelos', false],
              ['✣', 'IA', false],
              ['▱', 'Projetos', false],
              ['◌', 'Eu', false],
            ].map(([icon, label, active]) => (
              <button key={String(label)} className={cn('flex flex-col items-center gap-1', active ? 'text-black' : 'text-slate-400')}>
                <span className="text-3xl leading-none">{icon}</span>
                <span>{label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Editor({ go }: { go: (s: Screen) => void }) {
  const [tool, setTool] = useState<Tool>('Editar');

  return (
    <div className="h-screen w-screen overflow-hidden bg-[#151515] text-white">
      <div className="grid h-full grid-rows-[88px_minmax(0,1fr)_250px_104px]">
        <div className="flex items-center justify-between px-9">
          <div className="flex items-center gap-8">
            <button onClick={() => go('home')} className="flex h-14 w-14 items-center justify-center rounded-full bg-black/20 text-4xl text-white/85 transition hover:bg-white/10">×</button>
            <button className="text-4xl text-white/80">⌕</button>
          </div>
          <div className="flex items-center gap-4">
            <button className="rounded-2xl bg-[#2a2a2c] px-6 py-3 text-xl font-semibold text-white">AI UHD⌄</button>
            <button className="rounded-2xl bg-[#1fc8df] px-7 py-3 text-xl font-bold text-black">Exportar</button>
          </div>
        </div>

        <div className="relative flex min-h-0 items-center justify-center">
          <div className="absolute left-8 top-1/2 z-20 -translate-y-1/2 rounded-2xl bg-[#242424] px-4 py-3 text-xl font-medium text-white/80 shadow-2xl">▣ Feedback</div>
          <div className="relative flex aspect-[9/16] h-[94%] max-h-[610px] items-center justify-center bg-black shadow-[0_40px_130px_rgba(0,0,0,0.7)]">
            <div className="text-center text-white">
              <div className="mb-3 text-4xl font-black">AXI</div>
              <div className="text-2xl font-bold">Toque para editar</div>
              <div className="absolute bottom-12 left-0 right-0 text-center text-sm text-white/35">ID do AXI: 3958690208</div>
            </div>
          </div>
          <div className="absolute bottom-1 left-8 text-4xl text-white/80">⛶</div>
          <button className="absolute bottom-1 left-1/2 -translate-x-1/2 text-5xl text-white/85">▷</button>
          <div className="absolute bottom-2 right-10 flex gap-8 text-4xl text-white/55"><span>▯</span><span>↶</span><span>↷</span></div>
        </div>

        <div className="relative overflow-hidden bg-[#1d1d1d]">
          <div className="flex h-14 items-center gap-8 px-8 text-xl font-medium text-white/55">
            <span>00:06 / 00:06</span>
            <span>·</span>
            <span>00:04</span>
            <span>·</span>
          </div>
          <div className="absolute left-1/2 top-10 z-20 h-[205px] w-[3px] bg-white shadow-[0_0_20px_rgba(255,255,255,0.5)]" />
          <div className="absolute right-8 top-24 z-20 flex h-16 w-16 items-center justify-center rounded-xl bg-white text-5xl text-black shadow-2xl">+</div>
          <div className="ml-0 mt-4 flex h-[74px] items-center">
            <div className="h-full w-[240px] bg-white/90" />
            <div className="h-full w-[540px] bg-black" />
            <div className="h-full flex-1 bg-[#111]" />
          </div>
          <div className="mt-3 h-14 bg-[#252525] pl-8 pt-4 text-2xl font-bold text-white/30">+ Adicionar áudio</div>
          <div className="mt-2 h-14 bg-[#252525] pl-8 pt-4 text-2xl font-bold text-white/30">+ Adicionar texto</div>
        </div>

        <div className="flex items-center justify-around bg-[#151515] text-center text-white/75">
          {editorTools.map((item) => (
            <button key={item} onClick={() => setTool(item)} className={cn('flex min-w-[100px] flex-col items-center gap-2 text-xl font-semibold transition', tool === item ? 'text-white' : 'text-white/55')}>
              <span className="text-4xl">{item === 'Editar' ? '✂' : item === 'Áudio' ? '♪' : item === 'Texto' ? 'T' : item === 'Efeitos' ? '✩' : item === 'Camadas' ? '▧' : '▤'}</span>
              <span>{item}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export function StudioHomePage() {
  const [screen, setScreen] = useState<Screen>('home');

  return (
    <AnimatePresence mode="wait">
      <motion.div key={screen} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }} transition={{ duration: 0.25 }}>
        {screen === 'home' ? <Home go={setScreen} /> : <Editor go={setScreen} />}
      </motion.div>
    </AnimatePresence>
  );
}
