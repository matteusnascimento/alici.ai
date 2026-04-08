import { SimpleWorkspacePage } from './SimpleWorkspacePage';

export function CampaignStudioPage() {
  return (
    <SimpleWorkspacePage
      type="campaign"
      title="Criar Campanha"
      subtitle="Descreva seu produto e objetivo para montar uma campanha base com etapas orientadas."
      tools={['Briefing', 'Oferta', 'Publico', 'Criativos', 'Copy', 'Distribuicao', 'A/B']}
      promptPlaceholder="Descreva produto, publico, oferta e objetivo para gerar uma campanha base"
    />
  );
}
