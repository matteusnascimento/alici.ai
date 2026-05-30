# AXI Studio Audit

Data: 2026-05-30
Escopo: frontend React/Vite em `frontend/src/components/studio/v2`, rotas em `frontend/src/router/AppRouter.tsx`, dados locais de templates/efeitos em `frontend/src/data`, services em `frontend/src/services`.

## Resumo executivo

O AXI Studio ja esta parcialmente migrado para uma experiencia orientada por templates, IA e fluxo de criacao. Existem tres linhas arquiteturais convivendo:

1. Studio Home orientada por busca, templates, projetos e uploads.
2. Editor unificado tipo Canva em `UnifiedEditorPage`.
3. Editor de video tipo CapCut em `VideoEditorStudioPage`.

O maior risco arquitetural atual nao e falta de componentes, mas duplicacao de shells/topbars/padroes de editor. `PlatformShell` ja esconde a topbar global no Studio e remove a sidebar global para `/app/studio/editor*`, mas ainda ha dois modelos internos de editor com headers e paines proprios.

## Rotas Studio encontradas

Fonte: `frontend/src/router/AppRouter.tsx`.

### Rotas ativas

- `/app/studio` -> `StudioHomePage`
- `/app/studio/editor` -> `UnifiedEditorPage`
- `/app/studio/editor/new` -> `UnifiedEditorPage`
- `/app/studio/editor/:projectId` -> `UnifiedEditorPage`
- `/app/studio/editor/design` -> `UnifiedEditorPage`
- `/app/studio/editor/video` -> `VideoEditorStudioPage`
- `/app/studio/editor/video/:projectId` -> `VideoEditorStudioPage`
- `/app/studio/import` -> `StudioImportPage`
- `/app/studio/tools/photo-editor` -> `PhotoEditorStudioPage`
- `/app/studio/tools/remove-background` -> `RemoveBackgroundStudioPage`
- `/app/studio/tools/ad` -> `PosterStudioPage`
- `/app/studio/tools/story` -> `StoryStudioPage`
- `/app/studio/tools/caption` -> `CaptionsStudioPage`
- `/app/studio/tools/cta` -> `CaptionsStudioPage mode="cta"`
- `/app/studio/tools/copy` -> `CaptionsStudioPage mode="promo"`
- `/app/studio/remove-background` -> `RemoveBackgroundStudioPage`
- `/app/studio/projects` -> `ProjectsStudioPage`
- `/app/studio/exports` -> `ExportsStudioPage`
- `/app/studio/brand-kit/*` -> `BrandStudioPage`
- `/app/studio/templates/*` -> `TemplatesStudioPage`
- `/app/studio/assets/*` -> `AssetsStudioPage`
- `/app/studio/ai-creative/*` -> `AiCreativeStudioPage`
- `/app/studio/brand` -> `BrandStudioPage`

### Rotas legadas redirecionadas

- `/app/studio/video-editor/*` -> `/app/studio/editor/video`
- `/app/studio/photo-editor/*` -> `/app/studio/tools/photo-editor`
- `/app/studio/poster/*` -> `/app/studio/tools/ad`
- `/app/studio/banner` -> `/app/studio/tools/ad`
- `/app/studio/story` -> `/app/studio/tools/story`
- `/app/studio/story/new` -> `/app/studio/tools/story`
- `/app/studio/ad-builder` -> `/app/studio/tools/ad`
- `/app/studio/caption-generator/*` -> `/app/studio/tools/caption`
- `/app/studio/copy-generator/*` -> `/app/studio/tools/copy`

## Componentes Studio encontrados

### Paginas

- `StudioHomePage.tsx`
- `TemplatesStudioPage.tsx`
- `UnifiedEditorPage.tsx`
- `VideoEditorStudioPage.tsx`
- `AiCreativeStudioPage.tsx`
- `PhotoEditorStudioPage.tsx`
- `PosterStudioPage.tsx`
- `StoryStudioPage.tsx`
- `BannerStudioPage.tsx`
- `CaptionsStudioPage.tsx`
- `RemoveBackgroundStudioPage.tsx`
- `AssetsStudioPage.tsx`
- `BrandStudioPage.tsx`
- `ProjectsStudioPage.tsx`
- `ExportsStudioPage.tsx`
- `StudioImportPage.tsx`

### Shells, layout e estruturas de editor

- `PlatformShell.tsx`: shell global da plataforma. Esconde `Topbar` em Studio/Marketing e remove `AppSidebar` nas rotas `/app/studio/editor*`.
- `StudioShell.tsx`: shell interno de editor com `StudioTopbar`, area central, painel direito e bottom opcional.
- `UnifiedEditorPage.tsx`: editor proprio, renderiza `header` proprio em vez de usar `StudioTopbar`.
- `VideoEditorStudioPage.tsx`: editor proprio, usa `StudioTopbar`, sidebar de ferramentas, preview/canvas, timeline e painel contextual.

### Componentes de editor

- `StudioTopbar.tsx`
- `StudioSidebar.tsx`
- `StudioToolRail.tsx`
- `StudioCanvas.tsx`
- `StudioTimeline.tsx`
- `StudioBottomDock.tsx`
- `StudioInspectorPanel.tsx`
- `StudioToolContextPanel.tsx`
- `StudioVideoContextPanel.tsx`
- `StudioLayersPanel.tsx`
- `StudioAssetsPanel.tsx`
- `StudioTemplatesPanel.tsx`
- `StudioHistoryPanel.tsx`
- `StudioExportModal.tsx`
- `StudioPromptBar.tsx`
- `StudioSaveIndicator.tsx`
- `StudioVariationStrip.tsx`

### Cards e config

- `cards/StudioLinkCard.tsx`
- `cards/StudioRecentProject.tsx`
- `cards/StudioToolCard.tsx`
- `config/studioHomeConfig.ts`
- `config/studioToolsConfig.ts`
- `studioNavigation.ts`

## Layouts duplicados

### Duplicacao principal

Atualmente existem dois modelos de editor:

- `UnifiedEditorPage` tem seu proprio `header`, sidebar, canvas e painel direito dentro da propria pagina.
- `VideoEditorStudioPage` usa `StudioTopbar`, sidebar local, `StudioCanvas`, `StudioTimeline` e `StudioVideoContextPanel`.

Resultado pratico: o sistema ja evita `Header` global duplicado dentro do editor, mas ainda duplica o conceito de editor shell internamente.

### Duplicacoes especificas

- `StudioShell` existe, mas nao e a base comum dos dois editores principais.
- `UnifiedEditorPage` nao usa `StudioTopbar`.
- `VideoEditorStudioPage` nao usa `StudioShell`.
- `StudioSidebar` existe, mas a home usa um aside local e o video editor usa uma sidebar local propria.
- `studioNavigation.ts` declara secoes `create`, `manage`, `brand`, enquanto `studioToolsConfig.ts` usa `create`, `continue`, `manage`, `library`. Ha desalinhamento nominal entre `brand` e `library`.
- `StudioToolContextPanel` e `StudioVideoContextPanel` cobrem conceitos similares de painel contextual, mas separados por tipo de editor.

## Headers encontrados

- `PlatformShell` renderiza `Topbar` global fora de Studio/Marketing.
- `StudioTopbar` e usado no `VideoEditorStudioPage` e no `StudioShell`.
- `UnifiedEditorPage` renderiza um `header` proprio com salvar/exportar/duplicar.
- `StudioCanvas` aceita `showHeader`, usado como header interno de canvas quando habilitado.

Regra de arquitetura recomendada:

- Studio Home: pode usar apenas chrome da plataforma ou uma home propria, sem topbar duplicada.
- Editor: deve usar somente `EditorShell/StudioTopbar`.
- `UnifiedEditorPage` deve parar de renderizar header proprio quando for integrado ao shell comum.

## Sidebars encontradas

- `AppSidebar`: sidebar global da plataforma.
- `StudioSidebar`: sidebar Studio baseada em `studioNavigation`.
- Aside local em `StudioHomePage`: links de Projetos, Uploads, Marca.
- Sidebar local em `UnifiedEditorPage`: ferramentas `select`, `fields`, `effects`, `magic`, `layers`, `assets`.
- Sidebar local em `VideoEditorStudioPage`: ferramentas `Modelos`, `Uploads`, `Texto`, `Midia`, `Legendas`, `Ajustes`, `Efeitos`, `Audio`, `Camadas`, `Marca`, `Projetos`, `Apps`, `Midia Magica / IA`.

Recomendacao:

- Manter `AppSidebar` fora de editores full-bleed.
- Consolidar sidebar de Studio Home em uma unica fonte de navegacao.
- Consolidar sidebar de editor em uma configuracao compartilhada por design/video, com extensoes por modo.

## Painels encontrados

- Painel contextual proprio em `UnifiedEditorPage`.
- Painel contextual direito em `VideoEditorStudioPage`.
- `StudioToolContextPanel`
- `StudioVideoContextPanel`
- `StudioInspectorPanel`
- `StudioLayersPanel`
- `StudioAssetsPanel`
- `StudioTemplatesPanel`
- `StudioHistoryPanel`

Lacuna:

- Nao ha contrato unico de painel contextual por selecao (`text`, `image`, `video`, `shape`, `project`).
- Estado de selecao e ferramentas ainda ficam dentro das paginas, nao em um editor state compartilhado.

## Ferramentas existentes

### Home e criacao

- Busca na home.
- Criar por template.
- Criar design novo.
- Projetos recentes.
- Uploads recentes.
- Templates recomendados.
- Categorias de templates.

### Templates

- Modelo `StudioTemplateDefinition` com `id`, `name`, `category`, `thumbnail`, `plan`, `format`, `tags`, `fields`, `canvas.layers`.
- Templates locais em `frontend/src/data/studioTemplates.ts`.
- Categorias existentes: Marketing, Hotelaria, Redes sociais, Stories, Reels, Videos, Posters, Cardapios, Promocoes, Eventos, Landing pages, Thumbnails, Apresentacoes, Documentos, E-mail.
- Filtros em `TemplatesStudioPage`: todos, meus templates, premium, recomendados.
- Projetos locais baseados em template via `localStorage`.

### Filtros e efeitos

- CSS filters em `frontend/src/data/studioEffects.ts`.
- Grupos existentes: `image-filter`, `image-advanced`, `text-effect`, `video-transition`, `video-motion`, `video-overlay`, `magic`.
- Filtros existentes: Vintage, Retro, Nordic, Fresco, Clean, Warm, Cinematic, Contrast, Black & White, Soft.
- Efeitos/texto/transicoes existentes: Highlight, 3D, Wavy, Typewriter, Neon, Glow, Fade Up, Fade, Zoom, Glitch, Swipe, Slide, Blur, Flash, Speed Ramp, Pan, Shake, overlays.

### IA/Magic

- `MAGIC_STUDIO_ACTIONS`: Remover fundo, Magic Eraser, Generative Fill, Expandir imagem, Gerar variacoes, Melhorar qualidade, Criar imagem por prompt, Criar video por prompt.
- `UnifiedEditorPage` marca acoes Magic como "em breve" e explicita que nao simula sucesso.
- `VideoEditorStudioPage` chama endpoints reais de Studio para captions, voiceover e generate.

## Ferramentas faltantes ou incompletas

### Home

- `IA do Dia` ainda nao aparece como area dedicada.
- `Magic Studio` ainda nao e uma area forte da home.
- `Lixeira` nao aparece na sidebar atual.
- Cards exatos pedidos ainda nao estao completos: Foto, Story, Poster, Banner, Landing Page aparecem parcialmente por rotas/config, mas nao como um conjunto unico e consistente.

### Templates

- Nao ha pasta `frontend/src/templates`.
- `StudioTemplate` existe como `StudioTemplateDefinition`, mas ainda nao usa exatamente o nome do modelo pedido.
- Categorias de Hotelaria especificas faltantes: Reserva Direta, Pousada Premium, Lua de Mel, Transfer, Passeios, Restaurante, Reveillon, Carnaval.
- Categorias de Marketing especificas faltantes: Promocoes, Ofertas, Ads, Landing Pages existem parcialmente, mas nao como taxonomia estruturada.
- `Meus Templates` e `Premium` existem no filtro, mas dependem de dados locais/fallback; falta backend persistente.

### Editor de design

- Falta um `EditorShell` comum com contrato claro: Topbar, Sidebar, Canvas, ContextPanel, Timeline/BottomBar.
- Painel contextual por selecao existe parcialmente, mas nao esta tipado como matriz `text/image/video/shape`.
- Controles de texto ainda sao basicos: falta fonte, animacao, efeitos completos, camada e posicao como controles dedicados.
- Controles de imagem ainda sao basicos: falta recorte, ajustes avancados e remover fundo real.

### Editor de video

- Timeline existe e e compacta, mas ainda e uma lista visual simples de clips.
- Faltam trilhas reais de audio, legendas, transicoes aplicadas em timeline e controle de velocidade persistente.
- Preview nao deve ser coberto pela timeline; no estado atual a timeline fica abaixo do canvas no editor de video, alinhado com a regra.

### Filtros

- Taxonomia pedida ainda incompleta:
  - Para Voce: ausente.
  - Marketing: Luxury, Product, Clean; apenas Clean existe.
  - Hotelaria: Sunset, Resort, Ocean, Premium; ausentes.
  - Retrato: Soft existe, Beauty/HDR ausentes.
  - Cinema: Cinematic existe, Film/Teal Orange ausentes.
  - Vintage: Retro/Nordic existem, Grain ausente.

### Efeitos

- Imagem: Blur, Glow, Shadow, Vignette existem; Grain, Sharpen, HDR precisam ser adicionados.
- Texto: Neon, Typewriter, 3D, Highlight existem; Gradient e Wave/Wavy precisam consolidacao de nome.
- Video: Fade, Zoom, Slide, Glitch, Flash, Speed Ramp, Shake existem; Motion Blur precisa ser adicionado.
- Estrutura de pastas `effects/`, `filters/`, `transitions/`, `animations/` ainda nao existe.

### Magic Studio AXI

- Acoes existem no frontend, mas varias estao como `coming_soon`.
- Falta contrato de disponibilidade por provider existente.
- Falta fallback visual padronizado: se provider nao existir, exibir "feature indisponivel" sem executar e sem simular sucesso.

## Revenue e inteligencia fora do Studio

Estado atual conhecido:

- `/app/dashboard` redireciona para `/app/revenue`.
- `/app/agents/:id/analytics` redireciona para `/app/revenue?view=agents`.
- `RevenueIntelligencePage` e a central atual para dados gerais, pipelines, marketing e agents.
- Componentes antigos de Agent Analytics foram removidos.

Backlog solicitado pelo produto:

- Remover qualquer entrada "Analytics" remanescente do menu principal.
- Transformar Revenue em Central de Inteligencia.
- Adicionar Leads, Conversoes, Reservas, ROI, Forecast, Funil e Canais.
- Integrar WhatsApp, Instagram, TikTok, Google Ads, Site e Chatbot.
- Criar IA Insights.
- Criar Inbox Omnichannel.
- Criar alternancia IA/Humano.
- Criar Control Room em tempo real.

Observacao: isso deve ser tratado como trilha paralela de Revenue/Operations, nao como dependencia direta da refatoracao visual do Studio.

## Recomendacao de fases tecnicas

### Fase 1: Arquitetura

- Criar `EditorShell` unico.
- Fazer `UnifiedEditorPage` e `VideoEditorStudioPage` usarem o mesmo shell.
- Remover header proprio do `UnifiedEditorPage`.
- Unificar nomes de secoes `brand`/`library`.
- Garantir que `StudioTopbar` seja a unica topbar de editor.

### Fase 2: Home

- Reorganizar `StudioHomePage` em blocos: Busca, Criar Novo, Templates em Destaque, IA do Dia, Projetos Recentes, Meus Templates, Templates Premium, Uploads Recentes, Magic Studio.
- Criar cards de criacao padronizados: Video, Foto, Story, Poster, Banner, Landing Page.
- Adicionar Lixeira na navegacao.

### Fase 3: Templates

- Renomear ou aliasar `StudioTemplateDefinition` para `StudioTemplate`.
- Criar pasta `frontend/src/templates`.
- Expandir taxonomia de Marketing, Hotelaria e Social.
- Separar dados por categoria/arquivo.
- Manter `TemplatesStudioPage` como rota de descoberta e garantir abertura direta no editor.

### Fase 4-5: Editores

- Extrair estado comum de projeto/selecao.
- Tipar painel contextual por selecao.
- Consolidar sidebar de ferramentas por modo `design` e `video`.
- Garantir timeline entre 160px e 220px no modo video.

### Fase 6-7: Filtros e efeitos

- Criar estrutura `effects/filters/transitions/animations`.
- Mover `studioEffects.ts` para catalogos segmentados.
- Implementar MVP com CSS filters e Canvas API onde houver transformacao real.

### Fase 8: Magic Studio

- Criar service de disponibilidade de IA por provider.
- Bloquear feature quando provider nao estiver configurado.
- Conectar acoes a endpoints reais existentes antes de liberar CTA.
- Manter "sem mock, sem sucesso falso" como regra de UI e backend.

### Fase 9: Polimento

- Revisar responsividade desktop/mobile.
- Reduzir duplicacao de classes entre editores.
- Validar foco, hover, espacos, contraste, truncamento e timeline.

## Criterios de pronto para a proxima fase

- `npm run typecheck`
- `npm run test`
- Teste visual manual das rotas:
  - `/app/studio`
  - `/app/studio/templates`
  - `/app/studio/editor/new?templateId=hotel_promo_story_001`
  - `/app/studio/editor/video?mode=new`
- Confirmar que nenhuma tela de editor renderiza `Topbar` global da plataforma.
- Confirmar que nenhuma acao de IA mostra sucesso quando o provider/endpoint nao existe.
