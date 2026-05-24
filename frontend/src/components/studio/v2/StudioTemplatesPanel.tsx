import type { StudioTemplate } from '../../../types/studioV2';

interface StudioTemplatesPanelProps {
  templates: StudioTemplate[];
  onApply: (templateId: number) => void;
}

export function StudioTemplatesPanel({ templates, onApply }: StudioTemplatesPanelProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
      <p className="mb-2 text-xs uppercase tracking-[0.16em] text-slate-400">Templates</p>
      <div className="space-y-2">
        {templates.slice(0, 4).map((template) => (
          <button
            key={template.id}
            type="button"
            onClick={() => onApply(template.id)}
            className="block w-full rounded-lg border border-cyan-400/20 bg-cyan-400/10 px-2 py-2 text-left text-xs text-cyan-100 hover:bg-cyan-400/20"
          >
            <p className="font-semibold">{template.name}</p>
            <p className="text-cyan-200/80">{template.category}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
