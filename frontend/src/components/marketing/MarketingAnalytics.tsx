import { useEffect, useState } from 'react';

import { getMarketingAnalytics } from '../../services/marketingService';
import type { MarketingAnalytics as AnalyticsData } from '../../types/marketing';
import { SectionCard } from './SectionCard';

interface MarketingAnalyticsProps {
  onNotify: (message: string) => void;
}

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-2 w-full rounded-full bg-white/10">
      <div className="h-2 rounded-full bg-cyan transition-all duration-500" style={{ width: `${value}%` }} />
    </div>
  );
}

export function MarketingAnalytics({ onNotify }: MarketingAnalyticsProps) {
  const [data, setData] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    let mounted = true;
    getMarketingAnalytics().then((response) => {
      if (!mounted) return;
      setData(response);
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (!data) {
    return (
      <SectionCard title="Analytics" description="Carregando dados operacionais de crescimento...">
        <div className="h-40 animate-pulse rounded-2xl border border-white/10 bg-white/[0.04]" />
      </SectionCard>
    );
  }

  return (
    <div className="space-y-6">
      <SectionCard
        title="Growth Analytics"
        description="Painel premium com metricas de campanhas, conteudo, funis e oportunidades de conversao."
        rightSlot={
          <button
            type="button"
            onClick={() => onNotify('Dados de analytics atualizados.')} className="rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-2 text-sm text-cyan"
          >
            Atualizar
          </button>
        }
      >
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {data.cards.map((card) => (
            <article key={card.label} className="rounded-2xl border border-white/10 bg-ink/40 p-4">
              <p className="text-sm text-slate-300">{card.label}</p>
              <p className="mt-2 font-display text-3xl text-white">{card.value}</p>
              <p className="mt-1 text-xs uppercase tracking-[0.18em] text-cyan">{card.change}</p>
            </article>
          ))}
        </div>
      </SectionCard>

      <div className="grid gap-6 xl:grid-cols-2">
        <SectionCard title="Engagement Trend" description="Tendencia semanal de engajamento dos ativos gerados.">
          <div className="space-y-3">
            {data.engagement_trend.map((point) => (
              <div key={point.week}>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-300">
                  <span>{point.week}</span>
                  <span>{point.value}%</span>
                </div>
                <ProgressBar value={point.value} />
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Content Output by Week" description="Volume de ativos produzidos por semana.">
          <div className="space-y-3">
            {data.content_output_by_week.map((point) => (
              <div key={point.week}>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-300">
                  <span>{point.week}</span>
                  <span>{point.posts} posts</span>
                </div>
                <ProgressBar value={Math.min(100, point.posts * 2)} />
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Channel Usage" description="Distribuicao de uso por canal operacional.">
          <div className="space-y-3">
            {data.channel_usage.map((item) => (
              <div key={item.channel}>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-300">
                  <span>{item.channel}</span>
                  <span>{item.percentage}%</span>
                </div>
                <ProgressBar value={item.percentage} />
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Conversion by Campaign Type" description="Performance relativa por tipo de campanha.">
          <div className="space-y-3">
            {data.conversion_by_campaign_type.map((item) => (
              <div key={item.type}>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-300">
                  <span>{item.type}</span>
                  <span>{item.percentage}%</span>
                </div>
                <ProgressBar value={item.percentage} />
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
