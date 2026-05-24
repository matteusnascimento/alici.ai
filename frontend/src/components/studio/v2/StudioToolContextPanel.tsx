import { useMemo, useState } from 'react';

interface StudioToolContextPanelProps {
  activeTool: string;
}

type ContextConfig = {
  title: string;
  subtitle: string;
  sliders?: Array<{ key: string; label: string; min?: number; max?: number; defaultValue?: number }>;
  toggles?: Array<{ key: string; label: string; defaultValue?: boolean }>;
  actions?: string[];
};

function normalizeTool(value: string) {
  return value.toLowerCase();
}

function resolveContext(activeTool: string): ContextConfig {
  const tool = normalizeTool(activeTool);

  if (tool.includes('crop') || tool.includes('cortar') || tool.includes('recortar')) {
    return {
      title: 'Recortar',
      subtitle: 'Ajuste proporcao, giro e reposicionamento com precisao.',
      sliders: [
        { key: 'crop-scale', label: 'Escala', defaultValue: 50 },
        { key: 'crop-rotation', label: 'Rotacao', min: -45, max: 45, defaultValue: 0 },
      ],
      toggles: [
        { key: 'crop-grid', label: 'Exibir grade', defaultValue: true },
        { key: 'crop-flip', label: 'Espelhar horizontalmente', defaultValue: false },
      ],
      actions: ['Aplicar 1:1', 'Aplicar 9:16', 'Resetar recorte'],
    };
  }

  if (tool.includes('adjust') || tool.includes('ajust') || tool.includes('brilho') || tool.includes('contraste')) {
    return {
      title: 'Ajustar',
      subtitle: 'Refine tons e nitidez para equilibrio visual do projeto.',
      sliders: [
        { key: 'adjust-brightness', label: 'Brilho', defaultValue: 50 },
        { key: 'adjust-contrast', label: 'Contraste', defaultValue: 50 },
        { key: 'adjust-saturation', label: 'Saturacao', defaultValue: 50 },
        { key: 'adjust-exposure', label: 'Exposicao', defaultValue: 50 },
        { key: 'adjust-temperature', label: 'Temperatura', defaultValue: 50 },
        { key: 'adjust-sharpness', label: 'Nitidez', defaultValue: 50 },
      ],
      actions: ['Aplicar ajuste', 'Resetar valores'],
    };
  }

  if (tool.includes('enhance') || tool.includes('aprimorar') || tool.includes('ia')) {
    return {
      title: 'Aprimorar com IA',
      subtitle: 'Aplique melhoria automatica com controle de intensidade.',
      sliders: [{ key: 'enhance-intensity', label: 'Intensidade IA', defaultValue: 60 }],
      toggles: [{ key: 'enhance-preview', label: 'Preview antes/depois', defaultValue: true }],
      actions: ['Aplicar preset IA', 'Resetar aprimoramento'],
    };
  }

  if (tool.includes('filtro') || tool.includes('filter')) {
    return {
      title: 'Filtros',
      subtitle: 'Escolha estilo visual e controle a forca do efeito.',
      sliders: [{ key: 'filter-strength', label: 'Forca do filtro', defaultValue: 45 }],
      actions: ['Aplicar filtro cinematico', 'Aplicar filtro clean', 'Remover filtro'],
    };
  }

  if (tool.includes('retouch') || tool.includes('retoque')) {
    return {
      title: 'Retoque',
      subtitle: 'Corrija detalhes finos mantendo aparencia natural.',
      sliders: [
        { key: 'retouch-skin', label: 'Suavizacao', defaultValue: 35 },
        { key: 'retouch-detail', label: 'Detalhe', defaultValue: 55 },
      ],
      actions: ['Aplicar retoque', 'Resetar retoque'],
    };
  }

  if (tool.includes('texto') || tool.includes('text')) {
    return {
      title: 'Texto',
      subtitle: 'Adicione copy, ajuste fonte, cor e alinhamento.',
      sliders: [{ key: 'text-size', label: 'Tamanho da fonte', min: 8, max: 96, defaultValue: 28 }],
      toggles: [{ key: 'text-shadow', label: 'Sombra do texto', defaultValue: true }],
      actions: ['Adicionar titulo', 'Adicionar subtitulo'],
    };
  }

  if (tool.includes('brand') || tool.includes('logo') || tool.includes('template')) {
    return {
      title: 'Brand Kit',
      subtitle: 'Aplique ativos da marca com consistencia visual.',
      toggles: [
        { key: 'brand-lock', label: 'Fixar paleta da marca', defaultValue: true },
        { key: 'brand-auto-logo', label: 'Aplicar logo automatico', defaultValue: false },
      ],
      actions: ['Inserir logo', 'Aplicar paleta', 'Abrir templates'],
    };
  }

  return {
    title: 'Ferramenta ativa',
    subtitle: 'Selecione uma ferramenta na barra principal para abrir controles contextuais.',
    actions: ['Aplicar acao', 'Salvar alteracoes'],
  };
}

export function StudioToolContextPanel({ activeTool }: StudioToolContextPanelProps) {
  const context = useMemo(() => resolveContext(activeTool), [activeTool]);
  const [sliderValues, setSliderValues] = useState<Record<string, number>>({});
  const [toggleValues, setToggleValues] = useState<Record<string, boolean>>({});

  return (
    <div className="space-y-4 rounded-2xl border border-white/10 bg-black/20 p-4">
      <div>
        <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-300">Contexto da ferramenta</p>
        <h4 className="mt-1 text-base font-semibold text-white">{context.title}</h4>
        <p className="mt-1 text-xs text-slate-300">{context.subtitle}</p>
      </div>

      {context.sliders?.map((slider) => {
        const min = slider.min ?? 0;
        const max = slider.max ?? 100;
        const value = sliderValues[slider.key] ?? slider.defaultValue ?? 50;

        return (
          <label key={slider.key} className="block text-xs text-slate-300">
            <span className="mb-1 flex items-center justify-between">
              <span>{slider.label}</span>
              <span className="text-slate-400">{value}</span>
            </span>
            <input
              type="range"
              min={min}
              max={max}
              value={value}
              onChange={(event) => setSliderValues((current) => ({ ...current, [slider.key]: Number(event.target.value) }))}
              className="w-full"
            />
          </label>
        );
      })}

      {context.toggles?.map((toggle) => {
        const checked = toggleValues[toggle.key] ?? toggle.defaultValue ?? false;
        return (
          <label key={toggle.key} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-slate-200">
            <span>{toggle.label}</span>
            <input
              type="checkbox"
              checked={checked}
              onChange={(event) => setToggleValues((current) => ({ ...current, [toggle.key]: event.target.checked }))}
              className="h-4 w-4 accent-cyan-500"
            />
          </label>
        );
      })}

      {context.actions ? (
        <div className="grid gap-2">
          {context.actions.map((action) => (
            <button key={action} type="button" className="rounded-xl border border-white/20 px-3 py-2 text-xs text-white transition hover:border-cyan-300/45 hover:text-cyan-100">
              {action}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
