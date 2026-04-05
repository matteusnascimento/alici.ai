import type {
  AdsInput,
  AdsOutput,
  AudioToolsInput,
  AudioToolsOutput,
  AutoEnhanceInput,
  AutoEnhanceOutput,
  CaptionsInput,
  CaptionsOutput,
  CloudAsset,
  LibraryTemplate,
  MarketingToolsInput,
  MarketingToolsOutput,
  PhotoEditorInput,
  PhotoEditorOutput,
  PosterInput,
  PosterOutput,
  ProductPhotosInput,
  ProductPhotosOutput,
  RemoveBackgroundInput,
  RemoveBackgroundOutput,
  RetouchInput,
  RetouchOutput,
  TeleprompterInput,
  TeleprompterOutput,
} from '../types/studio';

const delay = (ms = 700) => new Promise((resolve) => setTimeout(resolve, ms));

export async function generateAds(input: AdsInput): Promise<AdsOutput> {
  await delay();
  return {
    campaignHeadline: `${input.businessName}: ${input.objective} em ${input.platform}`,
    mainCopy: `${input.productService} para ${input.targetAudience} com oferta ${input.offer} e tom ${input.tone}.`,
    shortCopyVariation: `Resultado em ${input.segment} com ${input.campaignType}.`,
    ctaSuggestions: [input.cta, 'Falar com especialista', 'Quero diagnostico'],
    creativeAngle: `Angulo: dor de ${input.targetAudience} + ganho imediato + prova social.`,
    hookIdeas: ['Pare de perder leads no meio do funil', 'Ajuste simples que aumenta conversao', '3 passos para escalar sem caos'],
    painPoints: ['Baixa previsibilidade', 'Baixa taxa de resposta', 'Mensagem desalinhada'],
    objections: ['Nao sei se funciona no meu nicho', 'Parece caro', 'Sem tempo para implantar'],
    positioningSummary: `${input.businessName} como opcao premium e objetiva para ${input.segment}.`,
  };
}

export async function generateProductPhotos(input: ProductPhotosInput): Promise<ProductPhotosOutput> {
  await delay(850);
  return {
    previews: [
      `Preview ${input.visualStyle} 01`,
      `Preview ${input.visualStyle} 02`,
      `Preview ${input.visualStyle} 03`,
    ],
    styleVariations: [
      `${input.visualStyle} com fundo ${input.backgroundStyle}`,
      `${input.visualStyle} com foco em detalhes`,
      `${input.visualStyle} para ${input.platformDestination}`,
    ],
    exportFormats: [input.outputFormat, 'PNG', 'WEBP'],
  };
}

export async function generatePoster(input: PosterInput): Promise<PosterOutput> {
  await delay(760);
  return {
    posterBrief: `Poster ${input.style} para ${input.targetAudience} promovendo ${input.eventOrProduct}.`,
    layoutSuggestion: 'Hero forte no topo, bloco de oferta central, CTA destacado no rodape.',
    headlineHierarchy: [input.title, input.subtitle, input.offer],
    colorStyleRecommendation: `Base dark com destaque ciano e contraste areia para CTA em ${input.sizeFormat}.`,
    exportBlock: `${input.title}\n${input.subtitle}\n${input.offer}\n${input.cta}`,
  };
}

export async function applyPhotoEdit(input: PhotoEditorInput): Promise<PhotoEditorOutput> {
  await delay(620);
  return {
    history: [
      `Ferramenta aplicada: ${input.selectedTool}`,
      `Configuracoes: ${JSON.stringify(input.settings)}`,
      'Resultado mock gerado com sucesso',
    ],
    processedPreview: `Preview editado via ${input.selectedTool}`,
  };
}

export async function removeBackground(input: RemoveBackgroundInput): Promise<RemoveBackgroundOutput> {
  await delay(620);
  return {
    summary: `Fundo removido para ${input.uploads.length || 1} arquivo(s).`,
    processedPreview: 'Preview transparente pronto para export.',
  };
}

export async function retouchImage(input: RetouchInput): Promise<RetouchOutput> {
  await delay(640);
  return {
    beforeAfterSummary: `Retoque ${input.retouchMode} com intensidade ${input.intensity} em modo ${input.cleanupMode}.`,
    processedPreview: 'Preview de retoque aplicado com comparativo before/after.',
  };
}

export async function autoEnhanceImage(input: AutoEnhanceInput): Promise<AutoEnhanceOutput> {
  await delay(580);
  return {
    enhancementsApplied: [
      `Mode: ${input.enhancementMode}`,
      'Ajuste automatico de contraste',
      'Correção de ruido e nitidez',
      `Saida: ${input.outputSize}`,
    ],
    processedPreview: 'Preview auto-enhanced pronto para comparacao.',
  };
}

export async function generateCaptions(input: CaptionsInput): Promise<CaptionsOutput> {
  await delay(700);
  const blocks = [
    '00:00 Introducao do tema e contexto',
    '00:08 Desenvolvimento com proposta de valor',
    '00:16 CTA e direcionamento final',
  ];
  return {
    subtitleBlocks: blocks,
    captionText: `Legenda em ${input.language} com tom ${input.tone} para ${input.captionType}.`,
    socialCaptionSuggestion: 'Hook + beneficio + CTA para comentario/direct.',
    exportText: blocks.join('\n'),
  };
}

export async function generateAudioScript(input: AudioToolsInput): Promise<AudioToolsOutput> {
  await delay(690);
  return {
    audioScript: `Script de ${input.duration} para ${input.platform} com tom ${input.tone}.`,
    narrationSequence: ['Abertura com hook', 'Contexto + dor', 'Solução + prova', 'CTA final'],
    ctaEnding: 'Fale com nossa equipe agora e receba o roteiro completo.',
    speakingGuide: 'Pausas curtas, ênfase em palavras-chave e ritmo crescente no fechamento.',
  };
}

export async function generateTeleprompter(input: TeleprompterInput): Promise<TeleprompterOutput> {
  await delay(560);
  const words = input.scriptText.trim().split(/\s+/).filter(Boolean).length;
  const timing = Math.max(0.5, words / Math.max(80, input.readingSpeedWpm));
  const segments = input.scriptText.split('\n').filter((line) => line.trim());
  return {
    formattedScriptBlocks: segments.length ? segments : ['Bloco 1', 'Bloco 2', 'Bloco 3'],
    timingEstimateMinutes: Number(timing.toFixed(1)),
    segmentedReadingBlocks: segments.length ? segments.map((line, index) => `Bloco ${index + 1}: ${line}`) : ['Bloco 1', 'Bloco 2'],
  };
}

export async function generateMarketingAsset(input: MarketingToolsInput): Promise<MarketingToolsOutput> {
  await delay(620);
  return {
    lines: [
      `Tab ativo: ${input.tab}`,
      'Diagnostico do contexto e oportunidades',
      'Plano de acao em 3 blocos',
      'Copys/roteiros para execucao imediata',
    ],
  };
}

export function getLibraryTemplates(): LibraryTemplate[] {
  return [
    {
      id: 'hotel-launch',
      title: 'Hotel Launch Campaign',
      category: 'Hospitalidade',
      description: 'Pacote completo de anuncios + stories + copy de reserva.',
      targetToolRoute: '/app/studio/ads',
      presetData: { segment: 'hotelaria', tone: 'premium' },
    },
    {
      id: 'ecommerce-photo',
      title: 'Ecommerce Product Visual',
      category: 'Ecommerce',
      description: 'Preset de fotos de produto para social e catalogo.',
      targetToolRoute: '/app/studio/product-photos',
      presetData: { visualStyle: 'ecommerce clean', outputFormat: '1080x1080' },
    },
    {
      id: 'clinic-whatsapp',
      title: 'Clinic Follow-up Flow',
      category: 'Saude',
      description: 'Sequencia de mensagens para follow-up e fechamento.',
      targetToolRoute: '/app/studio/marketing-tools',
      presetData: { tab: 'whatsapp' },
    },
  ];
}

export function getCloudAssets(): CloudAsset[] {
  return [
    { id: 'asset-1', name: 'campanha-abril-kit.png', category: 'imagem', sizeKb: 420 },
    { id: 'asset-2', name: 'roteiro-vsl-q2.txt', category: 'texto', sizeKb: 34 },
    { id: 'asset-3', name: 'audio-hook-vendas.mp3', category: 'audio', sizeKb: 3180 },
  ];
}
