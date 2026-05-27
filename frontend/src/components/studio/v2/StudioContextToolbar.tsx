import {
  AlignCenter,
  Blend,
  Crop,
  Eraser,
  FlipHorizontal2,
  ImageOff,
  Layers3,
  PaintRoller,
  Scissors,
  Sparkles,
  SplitSquareHorizontal,
  Timer,
  Type,
  Wand2,
  Volume2,
  type LucideIcon,
} from 'lucide-react';

type SelectionKind = 'image' | 'video' | 'text' | 'none';

interface ToolbarAction {
  id: string;
  label: string;
  icon: LucideIcon;
  premium?: boolean;
}

const imageActions: ToolbarAction[] = [
  { id: 'edit', label: 'Editar', icon: Wand2 },
  { id: 'remove-background', label: 'Remover fundo', icon: ImageOff, premium: true },
  { id: 'eraser', label: 'Borracha', icon: Eraser },
  { id: 'color', label: 'Cor', icon: Blend },
  { id: 'crop', label: 'Cortar', icon: Crop },
  { id: 'flip', label: 'Inverter', icon: FlipHorizontal2 },
  { id: 'transparency', label: 'Transparencia', icon: Sparkles },
  { id: 'animate', label: 'Animar', icon: Timer },
  { id: 'position', label: 'Posicao', icon: Layers3 },
  { id: 'style', label: 'Pincel', icon: PaintRoller },
];

const videoActions: ToolbarAction[] = [
  { id: 'split', label: 'Dividir', icon: SplitSquareHorizontal },
  { id: 'trim', label: 'Cortar', icon: Scissors },
  { id: 'speed', label: 'Velocidade', icon: Timer },
  { id: 'audio', label: 'Audio', icon: Volume2 },
  { id: 'captions', label: 'Legendas', icon: Type },
  { id: 'animate', label: 'Animar', icon: Timer },
  { id: 'position', label: 'Posicao', icon: Layers3 },
  { id: 'ai', label: 'IA', icon: Wand2, premium: true },
];

const textActions: ToolbarAction[] = [
  { id: 'font', label: 'Fonte', icon: Type },
  { id: 'align', label: 'Alinhar', icon: AlignCenter },
  { id: 'color', label: 'Cor', icon: Blend },
  { id: 'animate', label: 'Animar', icon: Timer },
  { id: 'position', label: 'Posicao', icon: Layers3 },
];

function actionsForSelection(kind: SelectionKind) {
  if (kind === 'image') return imageActions;
  if (kind === 'video') return videoActions;
  if (kind === 'text') return textActions;
  return [];
}

export function StudioContextToolbar({
  selectionKind,
  activeAction,
  onAction,
}: {
  selectionKind: SelectionKind;
  activeAction?: string;
  onAction?: (actionId: string) => void;
}) {
  const actions = actionsForSelection(selectionKind);
  if (!actions.length) return null;

  return (
    <div className="mx-auto flex w-fit max-w-full items-center gap-1 overflow-x-auto rounded-2xl border border-slate-200 bg-white px-3 py-2 text-slate-950 shadow-[0_18px_50px_rgba(0,0,0,0.22)]">
      {actions.map((action, index) => {
        const Icon = action.icon;
        const active = activeAction === action.id;
        return (
          <button
            key={action.id}
            type="button"
            onClick={() => onAction?.(action.id)}
            className={[
              'inline-flex shrink-0 items-center gap-2 rounded-xl px-3 py-2 text-sm font-bold transition',
              active ? 'bg-slate-950 text-white' : 'hover:bg-slate-100',
              index > 0 ? 'border-l border-slate-200/70' : '',
            ].join(' ')}
            title={action.label}
          >
            <Icon size={17} />
            <span>{action.label}</span>
            {action.premium ? <span className="text-[10px] text-amber-500">PRO</span> : null}
          </button>
        );
      })}
    </div>
  );
}
