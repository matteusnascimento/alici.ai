# AXI Marketing and Integrations Readiness

## Marketing

- `/app/marketing` remains the Marketing hub.
- Operational menus navigate to real routes:
  - `/app/marketing/planning`
  - `/app/marketing/plans/new`
  - `/app/marketing/campaigns`
  - `/app/marketing/campaigns/new`
  - `/app/marketing/audiences`
  - `/app/marketing/creatives`
  - `/app/marketing/automations`
  - `/app/marketing/calendar`
  - `/app/marketing/reports`
  - `/app/marketing/insights`
- Plans and campaigns reuse the real `MarketingProject` persistence layer.
- Audiences and calendar events now have dedicated persistent backend models.
- Creative actions open Studio routes with Marketing source parameters.
- Empty metrics remain explicit empty states and do not simulate external performance.

## Integrations

Supported operational cards:

- WhatsApp
- Instagram
- Messenger
- Website Chat
- Meta Ads
- Google Ads
- OmniBees
- Stripe

Shared actions:

- Connect
- Disconnect
- Test connection
- Sync

The backend returns real status values:

- `connected`
- `pending_setup`
- `auth_required`
- `disconnected`
- `error`

Sync does not return fake success. If a provider is not connected and validated, `/api/integrations/{provider}/sync` returns a real `422` error.

## External Dependencies

The following still require production credentials and webhook/OAuth completion before real external data can flow:

- Meta OAuth and webhooks for Instagram, Messenger and Meta Ads.
- Google Ads OAuth and customer id.
- OmniBees endpoint and API credentials.
- WhatsApp Business webhook validation.
- Stripe billing remains in the existing billing module; the integrations page only exposes operational status.
