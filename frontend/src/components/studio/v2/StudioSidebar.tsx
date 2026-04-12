import { Link, useLocation } from 'react-router-dom';

import { studioNavItems, studioSections } from './studioNavigation';

const sectionDescriptions: Record<string, string> = {
  create: 'Comece novas pecas e formatos',
  edit: 'Ajuste visual, recorte e melhorias',
  content: 'Gere textos e conteudo rapido',
  brand: 'Mantenha identidade e ativos',
  projects: 'Acompanhe historico e entregas',
};

const itemDescriptions: Record<string, string> = {
  poster: 'Arte vertical com assistencia IA',
  story: 'Formato rapido para redes sociais',
  banner: 'Criacao horizontal para campanhas',
  ad: 'Criativo para anuncios de performance',
  thumbnail: 'Capas de alto impacto visual',
  'video-create': 'Video inicial com roteiro assistido',
  'photo-editor': 'Edicao e ajustes finos de imagem',
  'video-editor': 'Edicao de video no fluxo completo',
  'remove-bg': 'Recorte automatico de fundo',
  retouch: 'Correcao de detalhes e pele',
  enhance: 'Melhoria rapida de qualidade',
  resize: 'Redimensionamento por canal',
  filters: 'Estilo visual e acabamento',
  captions: 'Legendas automaticas para video',
  'ad-copy': 'Texto persuasivo para anuncios',
  cta: 'Chamadas para acao otimizadas',
  headlines: 'Titulos com foco em clique',
  descricao: 'Descricao clara para produto',
  roteiro: 'Estrutura de roteiro para video',
  'brand-kit': 'Guia visual da marca',
  logos: 'Gestao de logotipos da marca',
  paletas: 'Cores oficiais e combinacoes',
  templates: 'Modelos prontos para acelerar',
  assets: 'Biblioteca de arquivos visuais',
  projects: 'Projetos criados no Studio',
  campanhas: 'Agrupamento por objetivo',
  exportados: 'Arquivos ja publicados',
  historico: 'Versoes e evolucao de trabalho',
};

export function StudioSidebar() {
  const location = useLocation();
  const activeItem = studioNavItems.find((item) => item.route === location.pathname);

  return (
    <aside className="h-full rounded-3xl border border-white/10 bg-[linear-gradient(165deg,rgba(7,13,30,0.96),rgba(8,18,40,0.9))] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
      <div className="mb-4 rounded-2xl border border-white/10 bg-white/[0.03] px-3 py-3">
        <p className="text-[11px] uppercase tracking-[0.28em] text-cyan-300">Ferramentas</p>
        <p className="mt-1 text-xs text-slate-300">Escolha o modulo que controla seu editor.</p>
      </div>
      <div className="max-h-[calc(100vh-13rem)] space-y-4 overflow-y-auto pr-1">
        {studioSections.map((section) => (
          <section key={section.key} className="rounded-2xl border border-white/8 bg-black/20 p-2.5">
            <div className="px-2 pb-2">
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">{section.label}</p>
              <p className="mt-1 text-[11px] text-slate-500">{sectionDescriptions[section.key]}</p>
            </div>
            <div className="space-y-1.5">
              {studioNavItems.filter((item) => item.section === section.key).map((item) => {
                const active = activeItem ? activeItem.key === item.key : location.pathname === item.route;
                return (
                  <Link
                    key={`${section.key}-${item.key}`}
                    to={item.route}
                    className={`group block rounded-xl border px-3 py-2.5 transition ${
                      active
                        ? 'border-cyan-300/35 bg-cyan-300/12 text-cyan-50 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]'
                        : 'border-transparent text-slate-300 hover:border-white/10 hover:bg-white/[0.04] hover:text-white'
                    }`}
                  >
                    <p className="text-sm font-medium leading-5">{item.label}</p>
                    <p className={`text-[11px] leading-4 ${active ? 'text-cyan-100/70' : 'text-slate-500 group-hover:text-slate-400'}`}>
                      {itemDescriptions[item.key] || 'Ferramenta criativa do Studio'}
                    </p>
                  </Link>
                );
              })}
            </div>
          </section>
        ))}
      </div>
    </aside>
  );
}
