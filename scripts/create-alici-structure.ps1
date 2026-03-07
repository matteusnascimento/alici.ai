param(
  [string]$ProjectRoot = "frontend/alici-platform"
)

$ErrorActionPreference = "Stop"

function Ensure-Dir {
  param([string]$Path)
  [System.IO.Directory]::CreateDirectory($Path) | Out-Null
}

function Ensure-Page {
  param([string]$Path, [string]$Title)

  if (-not (Test-Path -LiteralPath $Path)) {
    $content = @"
export default function Page() {
  return (
    <main className="p-6">
      <h1 className="text-2xl font-semibold">$Title</h1>
      <p className="mt-2 text-sm text-slate-300">Module scaffold ready.</p>
    </main>
  );
}
"@
    Set-Content -LiteralPath $Path -Value $content -Encoding UTF8
  }
}

$root = Resolve-Path . | Select-Object -ExpandProperty Path
$target = Join-Path $root $ProjectRoot

Write-Host "Creating ALICI structure in: $target"

$dirs = @(
  "app/(platform)/dashboard",
  "app/(platform)/ai-studio/chat/[conversationId]",
  "app/(platform)/ai-studio/playground",
  "app/(platform)/ai-studio/prompts/create",
  "app/(platform)/ai-studio/prompts/[promptId]",
  "app/(platform)/ai-studio/workflows/builder",
  "app/(platform)/ai-studio/workflows/[workflowId]",
  "app/(platform)/ai-studio/automations",
  "app/(platform)/agents/create",
  "app/(platform)/agents/[agentId]",
  "app/(platform)/assistants/create",
  "app/(platform)/assistants/[assistantId]",
  "app/(platform)/knowledge-base",
  "app/(platform)/vector-db",
  "app/(platform)/media/audio",
  "app/(platform)/media/images",
  "app/(platform)/media/videos",
  "app/(platform)/media/documents",
  "app/(platform)/datasets",
  "app/(platform)/fine-tuning",
  "app/(platform)/developers/api-keys",
  "app/(platform)/developers/webhooks",
  "app/(platform)/developers/sdk",
  "app/(platform)/developers/logs",
  "app/(platform)/integrations/whatsapp",
  "app/(platform)/integrations/telegram",
  "app/(platform)/integrations/slack",
  "app/(platform)/integrations/discord",
  "app/(platform)/storage",
  "app/(platform)/analytics",
  "app/(platform)/usage",
  "app/(platform)/billing",
  "app/(platform)/team",
  "app/(platform)/permissions",
  "app/(platform)/security",
  "app/(platform)/notifications",
  "app/(platform)/marketplace",
  "app/(platform)/templates",
  "app/(platform)/settings",
  "app/(platform)/admin",
  "features/dashboard/components",
  "features/dashboard/hooks",
  "features/dashboard/services",
  "features/dashboard/store",
  "features/dashboard/types",
  "features/dashboard/pages",
  "features/chat/components",
  "features/chat/hooks",
  "features/chat/services",
  "features/chat/store",
  "features/agents/components",
  "features/agents/hooks",
  "features/assistants/components",
  "features/workflows/components",
  "features/prompts/components",
  "features/knowledge/components",
  "features/vector/components",
  "features/media/components",
  "features/analytics/components",
  "features/billing/components",
  "features/integrations/components",
  "features/team/components",
  "features/auth/components",
  "components/navigation",
  "components/charts",
  "components/tables",
  "components/forms",
  "components/modals",
  "components/ui",
  "layouts",
  "services",
  "store",
  "hooks",
  "lib",
  "config",
  "types",
  "styles",
  "public"
)

foreach ($dir in $dirs) {
  Ensure-Dir (Join-Path $target $dir)
}

$pages = @(
  @{ Path = "app/(platform)/dashboard/page.tsx"; Title = "Dashboard" },
  @{ Path = "app/(platform)/ai-studio/chat/page.tsx"; Title = "AI Studio Chat" },
  @{ Path = "app/(platform)/agents/page.tsx"; Title = "Agents" },
  @{ Path = "app/(platform)/assistants/page.tsx"; Title = "Assistants" },
  @{ Path = "app/(platform)/knowledge-base/page.tsx"; Title = "Knowledge Base" },
  @{ Path = "app/(platform)/vector-db/page.tsx"; Title = "Vector Database" },
  @{ Path = "app/(platform)/analytics/page.tsx"; Title = "Analytics" },
  @{ Path = "app/(platform)/billing/page.tsx"; Title = "Billing" },
  @{ Path = "app/(platform)/settings/page.tsx"; Title = "Settings" }
)

foreach ($page in $pages) {
  $fullPath = Join-Path $target $page.Path
  Ensure-Dir (Split-Path $fullPath)
  Ensure-Page -Path $fullPath -Title $page.Title
}

Write-Host "ALICI structure ready." -ForegroundColor Green
