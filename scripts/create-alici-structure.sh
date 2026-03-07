#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-frontend/alici-platform}"
TARGET="$(pwd)/${PROJECT_ROOT}"

echo "Creating ALICI structure in: ${TARGET}"

mkdir -p "${TARGET}"

DIRS=(
  "app/(platform)/dashboard"
  "app/(platform)/ai-studio/chat/[conversationId]"
  "app/(platform)/ai-studio/playground"
  "app/(platform)/ai-studio/prompts/create"
  "app/(platform)/ai-studio/prompts/[promptId]"
  "app/(platform)/ai-studio/workflows/builder"
  "app/(platform)/ai-studio/workflows/[workflowId]"
  "app/(platform)/ai-studio/automations"
  "app/(platform)/agents/create"
  "app/(platform)/agents/[agentId]"
  "app/(platform)/assistants/create"
  "app/(platform)/assistants/[assistantId]"
  "app/(platform)/knowledge-base"
  "app/(platform)/vector-db"
  "app/(platform)/media/audio"
  "app/(platform)/media/images"
  "app/(platform)/media/videos"
  "app/(platform)/media/documents"
  "app/(platform)/datasets"
  "app/(platform)/fine-tuning"
  "app/(platform)/developers/api-keys"
  "app/(platform)/developers/webhooks"
  "app/(platform)/developers/sdk"
  "app/(platform)/developers/logs"
  "app/(platform)/integrations/whatsapp"
  "app/(platform)/integrations/telegram"
  "app/(platform)/integrations/slack"
  "app/(platform)/integrations/discord"
  "app/(platform)/storage"
  "app/(platform)/analytics"
  "app/(platform)/usage"
  "app/(platform)/billing"
  "app/(platform)/team"
  "app/(platform)/permissions"
  "app/(platform)/security"
  "app/(platform)/notifications"
  "app/(platform)/marketplace"
  "app/(platform)/templates"
  "app/(platform)/settings"
  "app/(platform)/admin"
  "features/dashboard/components"
  "features/dashboard/hooks"
  "features/dashboard/services"
  "features/dashboard/store"
  "features/dashboard/types"
  "features/dashboard/pages"
  "features/chat/components"
  "features/chat/hooks"
  "features/chat/services"
  "features/chat/store"
  "features/agents/components"
  "features/agents/hooks"
  "features/assistants/components"
  "features/workflows/components"
  "features/prompts/components"
  "features/knowledge/components"
  "features/vector/components"
  "features/media/components"
  "features/analytics/components"
  "features/billing/components"
  "features/integrations/components"
  "features/team/components"
  "features/auth/components"
  "components/navigation"
  "components/charts"
  "components/tables"
  "components/forms"
  "components/modals"
  "components/ui"
  "layouts"
  "services"
  "store"
  "hooks"
  "lib"
  "config"
  "types"
  "styles"
  "public"
)

for dir in "${DIRS[@]}"; do
  mkdir -p "${TARGET}/${dir}"
done

create_page() {
  local file="$1"
  local title="$2"
  if [ ! -f "${file}" ]; then
    cat > "${file}" <<EOF
export default function Page() {
  return (
    <main className="p-6">
      <h1 className="text-2xl font-semibold">${title}</h1>
      <p className="mt-2 text-sm text-slate-300">Module scaffold ready.</p>
    </main>
  );
}
EOF
  fi
}

create_page "${TARGET}/app/(platform)/dashboard/page.tsx" "Dashboard"
create_page "${TARGET}/app/(platform)/ai-studio/chat/page.tsx" "AI Studio Chat"
create_page "${TARGET}/app/(platform)/agents/page.tsx" "Agents"
create_page "${TARGET}/app/(platform)/assistants/page.tsx" "Assistants"
create_page "${TARGET}/app/(platform)/knowledge-base/page.tsx" "Knowledge Base"
create_page "${TARGET}/app/(platform)/vector-db/page.tsx" "Vector Database"
create_page "${TARGET}/app/(platform)/analytics/page.tsx" "Analytics"
create_page "${TARGET}/app/(platform)/billing/page.tsx" "Billing"
create_page "${TARGET}/app/(platform)/settings/page.tsx" "Settings"

echo "ALICI structure ready."
