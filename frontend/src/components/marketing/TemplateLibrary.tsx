import { getTemplateLibrary } from '../../services/marketingService';
import type { MarketingTemplateProfile } from '../../types/marketing';
import { SectionCard } from './SectionCard';

interface TemplateLibraryProps {
  onUseTemplate: (profile: MarketingTemplateProfile) => void;
  onNotify: (message: string) => void;
}

export function TemplateLibrary({ onUseTemplate, onNotify }: TemplateLibraryProps) {
  const templates = getTemplateLibrary();

  return (
    <SectionCard
      title="Template Library"
      description="Estruturas reutilizaveis por nicho para acelerar campanhas, criativos, copy e funis."
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {templates.map((template) => (
          <article key={template.id} className="rounded-2xl border border-white/10 bg-ink/40 p-4 transition hover:border-cyan/40">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan">{template.niche}</p>
            <h4 className="mt-2 font-display text-lg text-white">{template.title}</h4>
            <p className="mt-2 text-sm text-slate-300">{template.description}</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-100">
              {template.included_assets.map((asset) => (
                <li key={asset} className="rounded-xl border border-white/5 bg-white/[0.03] px-3 py-2">
                  {asset}
                </li>
              ))}
            </ul>
            <button
              type="button"
              onClick={() => {
                onUseTemplate(template.profile);
                onNotify(`Template aplicado: ${template.title}.`);
              }}
              className="mt-4 w-full rounded-2xl bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-cyan/20"
            >
              Usar template
            </button>
          </article>
        ))}
      </div>
    </SectionCard>
  );
}
