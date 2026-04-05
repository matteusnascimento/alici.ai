import type {
  ContentPlanInput,
  ContentPlanResult,
  CreativeIdea,
  CreativeIdeasInput,
  FunnelInput,
  FunnelResult,
  LandingPageInput,
  LandingPageResult,
  MarketingAnalytics,
  MarketingCampaignInput,
  MarketingCampaignResult,
  MarketingTemplate,
  PostCopyInput,
  PostCopyResult,
  WhatsAppFlowInput,
  WhatsAppFlowResult,
} from '../types/marketing';

const wait = (ms = 700) => new Promise((resolve) => setTimeout(resolve, ms));

function pickToneLine(tone: string) {
  const normalized = tone.toLowerCase();
  if (normalized.includes('premium')) return 'com autoridade premium e foco em valor percebido';
  if (normalized.includes('direto')) return 'com clareza comercial e senso de urgencia';
  if (normalized.includes('human')) return 'com conversa proxima e linguagem acessivel';
  return `com tom ${tone}`;
}

export async function generateCampaign(payload: MarketingCampaignInput): Promise<MarketingCampaignResult> {
  await wait();
  return {
    campaign_headline: `${payload.business_name}: ${payload.campaign_goal} em ${payload.channel}`,
    primary_copy: `Para ${payload.target_audience}, posicionamos a oferta ${payload.offer} ${pickToneLine(payload.tone)} para acelerar ${payload.campaign_goal}.`,
    secondary_copy: `Campanha ${payload.campaign_type} para o segmento ${payload.market_segment} com investimento ${payload.budget_range} e foco em conversao consistente.`,
    cta_suggestions: [
      payload.call_to_action,
      'Quero receber a proposta agora',
      'Falar com especialista AXI hoje',
      'Ativar plano de crescimento',
    ],
    offer_angle: `Angulo principal: transformar ${payload.offer} em decisao de compra imediata para ${payload.target_audience}.`,
    pain_points: [
      'Baixa consistencia de leads qualificados',
      'Campanhas sem narrativa clara de valor',
      'Tempo alto entre primeiro contato e fechamento',
    ],
    objections: [
      'Preco percebido acima do mercado',
      'Duvida sobre retorno no curto prazo',
      'Receio de mudanca de fornecedor atual',
    ],
    positioning_summary: `${payload.business_name} se posiciona como opcao de referencia para ${payload.market_segment} com promessa de resultado concreto e mensuravel.`,
    creative_suggestion: `Criativo recomendado: video curto com prova social + comparativo antes/depois + CTA ${payload.call_to_action}.`,
  };
}

export async function generateCreativeIdeas(payload: CreativeIdeasInput): Promise<CreativeIdea[]> {
  await wait(650);
  return Array.from({ length: 8 }).map((_, index) => ({
    title: `${index + 1}. ${payload.platform} idea para ${payload.niche}`,
    concept: `Conteudo focado em ${payload.objective} para ${payload.audience}, destacando diferencial pratico do negocio.`,
    hook: `"Se voce atua em ${payload.niche}, esse ajuste aumenta resultado em 7 dias"`,
    cta: `Convide para acao: ${payload.objective} com proximo passo claro no final.`,
  }));
}

export async function generateContentPlan(payload: ContentPlanInput): Promise<ContentPlanResult> {
  await wait(760);
  return {
    weekly_plan: [
      `Semana 1: awareness sobre ${payload.business_type}`,
      'Semana 2: autoridade com provas e bastidores',
      'Semana 3: aquecimento para oferta principal',
      'Semana 4: conversao com oferta e urgencia controlada',
    ],
    monthly_plan: [
      `Mes planejado para ${payload.goal}`,
      `${payload.frequency_per_week} publicacoes por semana em ${payload.platform}`,
      `Pilares priorizados: ${payload.content_pillars}`,
    ],
    content_pillar_breakdown: [
      'Educacao de mercado',
      'Prova de resultado',
      'Oferta e posicionamento',
      'Retencao e comunidade',
    ],
    posting_suggestions: [
      'Segunda: insight rapido + hook forte',
      'Quarta: case ou bastidor com autoridade',
      'Sexta: oferta e CTA direto para contato',
    ],
    campaign_dates: ['Dia 03: abertura', 'Dia 12: reforco social', 'Dia 20: sprint de conversao', 'Dia 28: fechamento'],
    grouped_ideas: {
      attraction: ['Reels de dor latente', 'Story com enquete de diagnostico', 'Carrossel de erros comuns'],
      authority: ['Estudo de caso local', 'Checklist tecnico de decisao', 'Analise comparativa de abordagem'],
      conversion: ['Oferta com bonus de curto prazo', 'Sequencia de prova + CTA', 'Post de ultima chamada'],
      retention: ['Mensagem de onboarding', 'Conteudo de uso avancado', 'Oferta de continuidade mensal'],
    },
  };
}

export async function generatePostCopy(payload: PostCopyInput): Promise<PostCopyResult> {
  await wait(700);
  return {
    main_copy: `${payload.product_service} para ${payload.audience}: estrategia ${payload.tone} orientada para ${payload.goal}. ${payload.cta}`,
    variations: [
      `Variante 1: narrativa curta com foco em dor e ganho imediato de ${payload.audience}.`,
      'Variante 2: prova social + resultado numerico + convite para conversa.',
      `Variante 3: chamada direta para ${payload.content_type} com objeções antecipadas.`,
    ],
    cta_lines: [payload.cta, 'Chame no direct para receber o plano', 'Clique e veja a estrutura completa'],
    hashtags: ['#marketingdigital', '#crescimento', '#negocioslocais', '#axi', '#performance'],
    hook_suggestion: `"A maioria perde vendas por ignorar este ponto em ${payload.product_service}"`,
  };
}

export async function generateFunnel(payload: FunnelInput): Promise<FunnelResult> {
  await wait(760);
  return {
    stages: [
      {
        stage: 'Top of Funnel',
        content: `Conteudos de descoberta em ${payload.acquisition_channel}`,
        messaging_goal: 'Gerar atencao e diagnostico de dor',
        cta: 'Baixar guia rapido',
        objections: 'Nao vejo urgencia agora',
        nurturing: 'Sequencia educativa curta com prova social',
      },
      {
        stage: 'Middle of Funnel',
        content: 'Comparativos, estudos de caso e bastidores de execucao',
        messaging_goal: 'Construir confianca e reduzir risco percebido',
        cta: 'Agendar conversa de estrategia',
        objections: 'Nao sei se funciona para meu negocio',
        nurturing: 'Conteudo por segmento e FAQ de implementacao',
      },
      {
        stage: 'Bottom of Funnel',
        content: `Oferta ${payload.offer} com deadline e bonus`,
        messaging_goal: 'Converter decisao com clareza comercial',
        cta: 'Fechar agora',
        objections: 'Preco e prazo de retorno',
        nurturing: 'Follow-up com simulacao de retorno',
      },
      {
        stage: 'Remarketing',
        content: 'Criativos de retomada com prova de resultado',
        messaging_goal: 'Reativar leads mornos',
        cta: 'Retomar proposta',
        objections: 'Perdi o timing',
        nurturing: 'Mensagem de recuperacao em 3 toques',
      },
      {
        stage: 'Conversion Sequence',
        content: 'Sequencia final com CTA crescente',
        messaging_goal: `Concluir ${payload.funnel_objective}`,
        cta: 'Confirmar adesao',
        objections: 'Preciso pensar mais',
        nurturing: 'Oferta de entrada com baixo risco',
      },
    ],
  };
}

export async function generateWhatsAppFlow(payload: WhatsAppFlowInput): Promise<WhatsAppFlowResult> {
  await wait(750);
  return {
    sequence: [
      `1) Abertura: contato inicial para ${payload.business_type} com contexto da demanda`,
      `2) Qualificacao: pergunta objetiva para mapear estagio ${payload.customer_stage}`,
      `3) Valor: argumento de oferta ${payload.offer} com beneficio central`,
      '4) Convite: proposta de proximo passo com horario sugerido',
      '5) Follow-up: retomada amigavel com opcao de resposta rapida',
      '6) Fechamento: confirmacao e instrucoes de onboarding',
    ],
    follow_up_timing: ['+15 min apos primeiro contato', '+24h com prova social', '+72h com encerramento da condicao'],
    variations: [
      'Variacao A: linguagem consultiva com perguntas abertas',
      'Variacao B: roteiro direto com foco em oferta e prazo',
      'Variacao C: abordagem humanizada com gatilho de confianca',
    ],
    human_version: 'Oi! Vi seu interesse e quero te ajudar a escolher a melhor opcao sem complicacao. Posso te fazer duas perguntas rapidas?',
    direct_version: `Temos uma opcao alinhada ao seu objetivo (${payload.objective}). Quer que eu te envie a proposta agora?`,
  };
}

export async function generateLandingPage(payload: LandingPageInput): Promise<LandingPageResult> {
  await wait(720);
  return {
    hero_title: `${payload.promise} para ${payload.audience}`,
    subtitle: `${payload.business} apresenta uma oferta objetiva para acelerar resultados com linguagem ${payload.tone}.`,
    benefit_bullets: [
      'Implementacao rapida com foco em resultado comercial',
      'Roteiro claro para reduzir dispersao operacional',
      'Acompanhamento de KPIs para evolucao continua',
    ],
    offer_section: `Oferta principal: ${payload.offer} com estrutura em etapas e onboarding orientado.`,
    objections_section: ['"Isso serve para meu perfil?"', '"Quanto tempo para ter retorno?"', '"Como fica suporte apos contratacao?"'],
    faq: [
      'Como funciona a implementacao?',
      'Qual o prazo para primeiros resultados?',
      'Existe personalizacao por segmento?',
    ],
    final_cta: payload.cta_objective,
    proof_section: 'Sugestao de prova: depoimentos + mini-cases com antes/depois + numeros de conversao.',
  };
}

export async function getMarketingAnalytics(): Promise<MarketingAnalytics> {
  await wait(500);
  return {
    cards: [
      { label: 'Campanhas criadas', value: '42', change: '+18% no mes' },
      { label: 'Posts gerados', value: '176', change: '+22% no mes' },
      { label: 'Funis ativos', value: '9', change: '+2 novos' },
      { label: 'Oportunidades de conversao', value: '63', change: '+11% na semana' },
      { label: 'Fluxos WhatsApp criados', value: '27', change: '+6 esta semana' },
      { label: 'Templates salvos', value: '14', change: '+3 no mes' },
    ],
    engagement_trend: [
      { week: 'S1', value: 42 },
      { week: 'S2', value: 55 },
      { week: 'S3', value: 61 },
      { week: 'S4', value: 73 },
    ],
    content_output_by_week: [
      { week: 'S1', posts: 21 },
      { week: 'S2', posts: 33 },
      { week: 'S3', posts: 46 },
      { week: 'S4', posts: 51 },
    ],
    channel_usage: [
      { channel: 'Instagram', percentage: 37 },
      { channel: 'WhatsApp', percentage: 24 },
      { channel: 'Facebook', percentage: 19 },
      { channel: 'Google', percentage: 20 },
    ],
    conversion_by_campaign_type: [
      { type: 'Lead generation', percentage: 34 },
      { type: 'Sales', percentage: 29 },
      { type: 'Launch', percentage: 18 },
      { type: 'Remarketing', percentage: 19 },
    ],
  };
}

export function getTemplateLibrary(): MarketingTemplate[] {
  return [
    {
      id: 'hotel',
      title: 'Hotel Revenue Sprint',
      niche: 'Hotel',
      description: 'Campanhas para ocupacao direta e reservas recorrentes em baixa temporada.',
      included_assets: ['Campanha de ocupacao', 'Fluxo WhatsApp de reserva', 'Landing de pacote'],
      profile: {
        businessName: 'Hotel Vista Mar',
        marketSegment: 'hotelaria urbana',
        audience: 'casais e familias em viagens curtas',
        offer: 'pacote de fim de semana com cafe premium',
        tone: 'premium consultivo',
        platform: 'Instagram',
      },
    },
    {
      id: 'pousada',
      title: 'Pousada Escape Plan',
      niche: 'Pousada',
      description: 'Estrutura para aumentar reservas em datas especiais e feriados prolongados.',
      included_assets: ['Calendario sazonal', 'Criativos de experiencia', 'Copy de oferta limitada'],
      profile: {
        businessName: 'Pousada Serra Azul',
        marketSegment: 'hospitalidade regional',
        audience: 'casais em busca de descanso',
        offer: 'pacote romântico com late checkout',
        tone: 'acolhedor premium',
        platform: 'Instagram',
      },
    },
    {
      id: 'restaurant',
      title: 'Restaurant Table Engine',
      niche: 'Restaurant',
      description: 'Plano para lotacao em dias de baixa e aumento de ticket medio por reserva.',
      included_assets: ['Sequencia de stories', 'Funil de reserva', 'Copy para menu sazonal'],
      profile: {
        businessName: 'Bistro Alto',
        marketSegment: 'gastronomia local',
        audience: 'publico que busca experiencia premium',
        offer: 'menu degustacao com harmonizacao',
        tone: 'sofisticado direto',
        platform: 'Instagram',
      },
    },
    {
      id: 'clinic',
      title: 'Clinic Trust Builder',
      niche: 'Clinic',
      description: 'Roteiros para autoridade, educacao de paciente e conversao com seguranca.',
      included_assets: ['Calendario educativo', 'Post institucional', 'Fluxo de follow-up'],
      profile: {
        businessName: 'Clinica Prime',
        marketSegment: 'saude e bem-estar',
        audience: 'adultos com foco em qualidade de vida',
        offer: 'plano de acompanhamento trimestral',
        tone: 'tecnico humanizado',
        platform: 'Instagram',
      },
    },
    {
      id: 'local-commerce',
      title: 'Local Commerce Booster',
      niche: 'Local Commerce',
      description: 'Modelo para atracao de fluxo local e campanhas por bairro.',
      included_assets: ['Anuncios geolocalizados', 'WhatsApp de recuperacao', 'CTA para visita'],
      profile: {
        businessName: 'Casa Central',
        marketSegment: 'comercio local',
        audience: 'moradores da regiao com alta intencao de compra',
        offer: 'condicao especial para primeira compra',
        tone: 'direto e confiavel',
        platform: 'Multi-channel',
      },
    },
    {
      id: 'digital-service',
      title: 'Digital Service Pipeline',
      niche: 'Digital Service',
      description: 'Estrutura para consultorias e servicos digitais com venda consultiva.',
      included_assets: ['Funil B2B', 'Landing de diagnostico', 'Copy de reuniao'],
      profile: {
        businessName: 'Growth Lab',
        marketSegment: 'servicos digitais',
        audience: 'gestores comerciais e marketing leads',
        offer: 'diagnostico de crescimento em 7 dias',
        tone: 'estrategico premium',
        platform: 'LinkedIn + WhatsApp',
      },
    },
    {
      id: 'real-estate',
      title: 'Real Estate Momentum',
      niche: 'Real Estate',
      description: 'Campanhas para captacao de leads qualificados e visitas agendadas.',
      included_assets: ['Criativos de tour', 'Sequencia de qualificacao', 'Oferta por bairro'],
      profile: {
        businessName: 'AXI Imoveis',
        marketSegment: 'mercado imobiliario',
        audience: 'familias em busca de mudanca',
        offer: 'consultoria de compra com simulacao financeira',
        tone: 'consultivo e seguro',
        platform: 'Instagram + Google',
      },
    },
    {
      id: 'beauty',
      title: 'Beauty Booking Machine',
      niche: 'Beauty Business',
      description: 'Plano para aumentar agenda recorrente e ticket por pacote de servico.',
      included_assets: ['Stories de agenda', 'Oferta de recorrencia', 'Fluxo de reativacao'],
      profile: {
        businessName: 'Studio Aura',
        marketSegment: 'beleza e estetica',
        audience: 'mulheres 23-45 com foco em autocuidado',
        offer: 'pacote mensal com bonus de manutencao',
        tone: 'aspiracional humano',
        platform: 'Instagram + WhatsApp',
      },
    },
  ];
}
