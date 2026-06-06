# AXI Studio Audit

Data: 2026-05-31

## Escopo

Auditoria da estrutura atual do AXI Studio no frontend React/Vite, com foco em paginas, layouts, rotas, paineis, sidebars, cabecalhos, timeline, templates, filtros, efeitos e Magic Studio.

Termos procurados: Studio, StudioLayout, StudioShell, StudioHome, StudioEditor, EditorLayout, VideoEditor, PhotoEditor, PosterEditor, UnifiedEditor, Canvas, Toolbar, Header, Sidebar, Timeline.

## Componentes Encontrados

Componentes centrais em `frontend/src/components/studio/v2`:

- `StudioHomePage.tsx`: home criativa do Studio com busca, criar novo, templates em destaque, IA do dia, projetos recentes, uploads recentes, Magic Studio e sidebar.
- `TemplatesStudioPage.tsx`: biblioteca de templates com categorias, busca, filtros por area, badges Free/Premium, formato e CTA `Usar template`.
- `UnifiedEditorPage.tsx`: editor de design/template com topbar unica, sidebar de ferramentas, canvas, painel contextual e barra inferior/timeline simples.
- `VideoEditorStudioPage.tsx`: editor de video com topbar unica, sidebar esquerda, preview/canvas, timeline compacta e painel contextual.
- `EditorShell.tsx`: shell declarativo para editor com `Topbar`, `Sidebar`, `Canvas`, `ContextPanel` e `Timeline`.
- `StudioImportPage.tsx`: fluxo de importacao de arquivos externos.

Dados e servicos relacionados:

- `frontend/src/types/studioTemplate.ts`: modelo `StudioTemplateDefinition`, campos, layers, filtros e projetos locais.
- `frontend/src/data/studioTemplates.ts`: catalogo local inicial de templates por categoria, plano, formato, campos e layers.
- `frontend/src/data/studioEffects.ts`: biblioteca inicial de filtros, efeitos, transicoes, movimentos, texto e acoes Magic Studio.
- `frontend/src/services/studioTemplate.service.ts`: CRUD local de projetos criados a partir de templates.
- `frontend/src/services/studioEffects.service.ts`: listagem de efeitos, composicao de CSS filters e merge de filtros por layer.
- `frontend/src/hooks/useStudioV2.ts`: integracao com backend Studio v2 para projetos, assets, templates e exports.

## Rotas Existentes

Rotas Studio em `frontend/src/router/AppRouter.tsx`:

- `/app/studio`
- `/app/studio/editor`
- `/app/studio/editor/new`
- `/app/studio/editor/:projectId`
- `/app/studio/editor/design`
- `/app/studio/editor/video`
- `/app/studio/editor/video/:projectId`
- `/app/studio/import`
- `/app/studio/tools/photo-editor`
- `/app/studio/tools/remove-background`
- `/app/studio/tools/ad`
- `/app/studio/tools/story`
- `/app/studio/tools/caption`
- `/app/studio/tools/cta`
- `/app/studio/tools/copy`
- `/app/studio/remove-background`
- `/app/studio/projects`
- `/app/studio/exports`
- `/app/studio/brand-kit/*`
- `/app/studio/templates/*`
- `/app/studio/assets/*`
- `/app/studio/ai-creative/*`

Rotas legadas redirecionadas:

- `/app/studio/video-editor/*` para `/app/studio/editor/video`
- `/app/studio/photo-editor/*` para `/app/studio/tools/photo-editor`
- `/app/studio/poster/*` para `/app/studio/tools/ad`
- `/app/studio/banner` para `/app/studio/tools/ad`
- `/app/studio/story` para `/app/studio/tools/story`
- `/app/studio/story/new` para `/app/studio/tools/story`
- `/app/studio/ad-builder` para `/app/studio/tools/ad`
- `/app/studio/caption-generator/*` para `/app/studio/tools/caption`
- `/app/studio/copy-generator/*` para `/app/studio/tools/copy`
- `/app/studio/brand` para `/app/studio/brand-kit`

## Layouts e Hierarquia

Home atual:

```text
AppLayout / PlatformShell
  -> StudioHomePage
```

Editor esperado:

```text
EditorShell ou pagina de editor full-bleed
  -> Topbar
  -> Sidebar
  -> Canvas / Preview
  -> ContextPanel
  -> Timeline / Bottom bar
```

`PlatformShell.tsx` ja trata `/app/studio/editor` como modulo full-bleed, ocultando sidebar/topbar da plataforma no editor. Isso evita o padrao antigo:

```text
AppLayout
  -> StudioLayout
    -> EditorLayout
      -> Header
```

## Headers Encontrados

Cabecalhos atuais:

- `StudioHomePage.tsx`: nao usa `header` principal duplicado; renderiza conteudo da home dentro do shell da plataforma.
- `TemplatesStudioPage.tsx`: possui um `header` local da pagina de templates. Como nao e editor full-bleed, e aceitavel.
- `UnifiedEditorPage.tsx`: possui `header[data-testid="studio-editor-topbar"]` como topbar unica.
- `VideoEditorStudioPage.tsx`: usa `StudioTopbar` como topbar unica.

Duplicacoes eliminadas:

- Plataforma + Studio + Editor header no editor.
- Segunda barra "Editor / Color / IA / Audio" no editor de video.
- Titulo interno do canvas como cabecalho extra no editor de video.

Risco restante:

- Algumas rotas legadas de ferramentas (`tools/photo-editor`, `tools/ad`, `tools/story`, `tools/caption`) ainda podem ter headers proprios. Elas nao devem ser renderizadas dentro de `EditorShell` sem revisao.

## Sidebars Encontradas

- `AppSidebar.tsx`: menu principal da plataforma. Deve aparecer na home do Studio, mas nao no editor.
- `StudioHomePage.tsx`: sidebar propria da home com Studio, Templates, Projetos, Uploads, Brand Kit, Magic Studio e Lixeira.
- `UnifiedEditorPage.tsx`: rail lateral com Selecionar, Campos, Efeitos, Magic AXI, Camadas e Assets.
- `VideoEditorStudioPage.tsx`: rail lateral com Modelos, Uploads, Texto, Midia, Legendas, Ajustes, Efeitos, Audio, Camadas, Marca, Projetos, Apps e Midia Magica / IA.

## Paineis Encontrados

- `UnifiedEditorPage.tsx`: painel contextual para campos, efeitos/filtros, Magic Studio, camadas e assets.
- `VideoEditorStudioPage.tsx`: painel contextual para templates, assets, efeitos, prompt, audio, texto, legendas e camadas.
- `StudioImportPage.tsx`: painel de importacao.

## Ferramentas Existentes

Home:

- Busca
- Criar novo: Video, Foto, Story, Poster, Banner, Landing Page
- Templates em destaque
- IA do Dia
- Projetos recentes
- Meus Templates
- Templates Premium
- Uploads recentes
- Magic Studio

Templates:

- Categorias Marketing, Promocoes, Ofertas, Ads, Landing Pages, Hotelaria, Reserva Direta, Pousada Premium, Lua de Mel, Transfer, Passeios, Restaurante, Reveillon, Carnaval, Social, Redes sociais, Stories, Reels, TikTok, YouTube, Shorts, Videos, Posters, Cardapios, Eventos, Landing pages, Thumbnails, Apresentacoes, Documentos e E-mail.
- Badges Free/Premium.
- Rota para abrir template no editor.

Design editor:

- Campos dinamicos
- Selecionar layer
- Camadas
- Assets
- Filtros e efeitos via CSS filters
- Salvar, duplicar e exportar visual

Video editor:

- Modelos
- Uploads
- Texto
- Midia
- Legendas
- Ajustes
- Efeitos
- Audio
- Camadas
- Marca
- Projetos
- Apps
- Midia Magica / IA
- Timeline compacta

Filtros e efeitos:

- Filtros CSS disponiveis: Vintage, Retro, Nordic, Fresco, Clean, Warm, Cinematic, Contrast, Black & White, Soft, Luxury, Product, Sunset, Resort, Ocean, Premium, Beauty, HDR, Film, Teal Orange.
- Efeitos/imagem: Grain, Blur Background, Glitch, Vignette, Shadow, Glow, Sharpen.
- Texto: Highlight, 3D, Wavy/Wave, Gradient, Typewriter, Neon, Glow, Fade Up.
- Video: Fade, Zoom, Glitch, Swipe, Slide, Blur, Flash, Speed Ramp, Motion Blur, Pan, Zoom In, Zoom Out, Shake.

Magic Studio:

- Remover fundo
- Magic Eraser
- Generative Fill
- Expandir imagem
- Gerar variacoes
- Melhorar qualidade
- Criar imagem por prompt
- Criar video por prompt

Regra atual: acoes sem provider/endpoint real aparecem como indisponiveis/em breve, sem simular sucesso.

## Ferramentas Faltantes

Arquitetura:

- Consolidar `UnifiedEditorPage` sobre `EditorShell` para reduzir duplicacao de layout.
- Padronizar `StudioTopbar` entre design e video.
- Revisar ferramentas legadas (`PhotoEditor`, `Poster`, `Story`, `Captions`) para nao manterem headers concorrentes.

Templates:

- Persistencia backend para templates do usuario, duplicados e importados.
- Thumbnails reais dos templates no storage.
- Controle real de plano para Premium.

Editor de design:

- Painel contextual completo por tipo selecionado: texto com fonte/cor/animacao/efeito/camada/posicao; imagem com filtros/recorte/remover fundo/ajustes.
- Engine real de exportacao visual.
- Undo/redo real por historico.

Editor de video:

- Engine real de timeline/clips.
- Transicoes e efeitos aplicados no render final.
- Preview com playback real.
- Audio waveform e legendas sincronizadas.

Filtros/efeitos:

- Separar fisicamente em `effects/`, `filters/`, `transitions/` e `animations/`.
- Canvas API para efeitos que nao cabem em CSS filters.

Magic Studio:

- Integrar com providers reais do backend.
- Expor feature indisponivel quando provider ou limite estiver ausente.
- Billing/limite antes de geracoes caras.

Mobile:

- Revisao especifica do editor para padrao Canva Mobile / CapCut Mobile.

## Proxima Ordem Recomendada

1. Fase 1: consolidar `UnifiedEditorPage` e `VideoEditorStudioPage` em `EditorShell`.
2. Fase 2: finalizar home com dados reais de projetos/uploads.
3. Fase 3: mover templates locais para contrato backend sem perder fallback visual.
4. Fases 4-5: completar editor design e video com paineis contextuais reais.
5. Fases 6-7: separar filtros/efeitos em modulos dedicados.
6. Fase 8: ligar Magic Studio aos providers reais, sem mocks.
7. Fase 9: polimento responsivo e teste visual.
