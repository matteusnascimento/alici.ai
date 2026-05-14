import {
  Bot,
  Crop,
  ImagePlus,
  Palette,
  Scissors,
  Shapes,
  SlidersHorizontal,
  Sparkles,
  Sun,
  Type,
  Wand2,
  type LucideIcon,
} from 'lucide-react';

interface StudioToolRailProps {
  tools: string[];
  activeTool: string;
  onSelect: (tool: string) => void;
}

const defaultIcon = SlidersHorizontal;

function iconForTool(tool: string): LucideIcon {
  const value = tool.toLowerCase();

  if (value.includes('aprimorar') || value.includes('enhance') || value.includes('ia edit')) return Sparkles;
  if (value.includes('crop') || value.includes('cortar') || value.includes('recortar')) return Crop;
  if (value.includes('ajust') || value.includes('brilho') || value.includes('contraste')) return SlidersHorizontal;
  if (value.includes('iluminacao') || value.includes('lighting') || value.includes('exposicao')) return Sun;
  if (value.includes('remover fundo') || value.includes('remove')) return Scissors;
  if (value.includes('filtro')) return Palette;
  if (value.includes('retoque') || value.includes('retouch')) return Wand2;
  if (value.includes('elemento')) return Shapes;
  if (value.includes('texto') || value.includes('text')) return Type;
  if (value.includes('brand') || value.includes('logo') || value.includes('template')) return ImagePlus;
  if (value.includes('ai')) return Bot;
  return defaultIcon;
}

export function StudioToolRail({ tools, activeTool, onSelect }: StudioToolRailProps) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-[linear-gradient(180deg,rgba(7,13,30,0.96),rgba(5,10,22,0.96))] p-2">
      {tools.map((tool) => (
        (() => {
          const Icon = iconForTool(tool);
          const active = activeTool === tool;

          return (
            <button
              key={tool}
              type="button"
              onClick={() => onSelect(tool)}
              className={`group flex min-w-[92px] flex-col items-center justify-center rounded-2xl border px-3 py-2.5 text-center transition ${
                active
                  ? 'border-cyan-300/45 bg-cyan-300/16 text-cyan-50'
                  : 'border-transparent text-slate-300 hover:border-white/12 hover:bg-white/[0.05] hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span className="mt-1 text-[11px] font-medium leading-4">{tool}</span>
            </button>
          );
        })()
      ))}
    </div>
  );
}
