import { Music4, Sparkles, Type, Wand2 } from 'lucide-react';
import { useRef, useState } from 'react';

interface StudioVideoContextPanelProps {
  activeTool: string;
  onAddTextClip: (text: string) => void;
  onUploadAudio: (file: File) => Promise<void>;
  onRunAiAction: (action: 'captions' | 'voiceover' | 'generate') => Promise<void>;
}

function normalize(tool: string) {
  return tool.toLowerCase();
}

export function StudioVideoContextPanel({ activeTool, onAddTextClip, onUploadAudio, onRunAiAction }: StudioVideoContextPanelProps) {
  const tool = normalize(activeTool);
  const audioInputRef = useRef<HTMLInputElement | null>(null);
  const [textValue, setTextValue] = useState('Titulo principal');
  const [fontValue, setFontValue] = useState('Sora');
  const [animationValue, setAnimationValue] = useState('Fade in');
  const [volume, setVolume] = useState(72);

  if (tool.includes('texto')) {
    return (
      <div className="space-y-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-300">Texto</p>
          <h3 className="mt-1 text-base font-semibold text-white">Adicione copy ao frame</h3>
          <p className="mt-1 text-xs text-slate-300">Insira titulos e overlays com estilo pronto para video vertical.</p>
        </div>
        <label className="block text-xs text-slate-300">
          <span className="mb-1 block">Texto</span>
          <textarea value={textValue} onChange={(event) => setTextValue(event.target.value)} className="min-h-24 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block text-xs text-slate-300">
            <span className="mb-1 block">Fonte</span>
            <select value={fontValue} onChange={(event) => setFontValue(event.target.value)} className="w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white">
              <option>Sora</option>
              <option>Space Grotesk</option>
              <option>Manrope</option>
              <option>DM Sans</option>
            </select>
          </label>
          <label className="block text-xs text-slate-300">
            <span className="mb-1 block">Animacao</span>
            <select value={animationValue} onChange={(event) => setAnimationValue(event.target.value)} className="w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white">
              <option>Fade in</option>
              <option>Slide up</option>
              <option>Pop</option>
              <option>Typewriter</option>
            </select>
          </label>
        </div>
        <button type="button" onClick={() => onAddTextClip(`${textValue} • ${fontValue} • ${animationValue}`)} className="inline-flex items-center gap-2 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink">
          <Type size={16} /> Adicionar texto
        </button>
      </div>
    );
  }

  if (tool.includes('audio')) {
    return (
      <div className="space-y-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-300">Audio</p>
          <h3 className="mt-1 text-base font-semibold text-white">Trilha, voz e volume</h3>
          <p className="mt-1 text-xs text-slate-300">Envie audio, gere voz IA e ajuste o nivel da trilha.</p>
        </div>
        <button type="button" onClick={() => audioInputRef.current?.click()} className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/[0.04] px-4 py-2 text-sm text-white">
          <Music4 size={16} /> Upload de audio
        </button>
        <input
          ref={audioInputRef}
          type="file"
          accept="audio/*"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              void onUploadAudio(file);
              event.currentTarget.value = '';
            }
          }}
        />
        <label className="block text-xs text-slate-300">
          <span className="mb-1 flex items-center justify-between">
            <span>Volume</span>
            <span>{volume}%</span>
          </span>
          <input type="range" min={0} max={100} value={volume} onChange={(event) => setVolume(Number(event.target.value))} className="w-full" />
        </label>
        <button type="button" onClick={() => void onRunAiAction('voiceover')} className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/40 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-100">
          <Sparkles size={16} /> Gerar voz IA
        </button>
      </div>
    );
  }

  if (tool.includes('legendas')) {
    return (
      <div className="space-y-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-300">Legendas</p>
          <h3 className="mt-1 text-base font-semibold text-white">Subtitulos inteligentes</h3>
          <p className="mt-1 text-xs text-slate-300">Gere legendas automaticas e organize o destaque das frases.</p>
        </div>
        <button type="button" onClick={() => void onRunAiAction('captions')} className="inline-flex items-center gap-2 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink">
          <Sparkles size={16} /> Gerar legendas
        </button>
      </div>
    );
  }

  if (tool.includes('efeitos') || tool.includes('filtros')) {
    return (
      <div className="space-y-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-300">Visual</p>
          <h3 className="mt-1 text-base font-semibold text-white">Efeitos e filtros</h3>
          <p className="mt-1 text-xs text-slate-300">Aplique estilo cinematografico, cor e refinamento visual.</p>
        </div>
        <div className="grid gap-2 sm:grid-cols-2">
          {['Clean', 'Cinematic', 'Glow', 'Punch'].map((preset) => (
            <button key={preset} type="button" className="rounded-xl border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:border-cyan-300/45 hover:text-white">
              {preset}
            </button>
          ))}
        </div>
        <button type="button" onClick={() => void onRunAiAction('generate')} className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/40 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-100">
          <Wand2 size={16} /> Sugerir variacoes
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <div>
        <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-300">Edicao</p>
        <h3 className="mt-1 text-base font-semibold text-white">Ferramenta ativa: {activeTool}</h3>
        <p className="mt-1 text-xs text-slate-300">Selecione clips, reorganize a timeline e ajuste o projeto quadro a quadro.</p>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {['Split', 'Trim', 'Speed', 'Replace'].map((action) => (
          <button key={action} type="button" className="rounded-xl border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:border-cyan-300/45 hover:text-white">
            {action}
          </button>
        ))}
      </div>
    </div>
  );
}
