/**
 * Campaign Workspace
 * Configures SimpleWorkspacePage for campaign creation workflow
 */
import { SimpleWorkspacePage } from './SimpleWorkspacePage';

export function CampaignWorkspacePage() {
  return (
    <SimpleWorkspacePage
      type="campaign"
      title="Criar Campanha"
      subtitle="Estruture e gerencie sua campanha de marketing com briefing, ofertas e distribuição"
      tools={['briefing', 'offer', 'audience', 'creatives', 'copy', 'distribution', 'ab-testing']}
      promptPlaceholder="Descreva sua campanha de marketing..."
    />
  );
}
