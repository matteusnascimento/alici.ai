# ALICI Platform Frontend (Next.js)

Professional frontend scaffold for ALICI using:

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Zustand for state management
- Axios for API client
- Feature-driven modular architecture

## Architecture

```text
frontend/alici-platform
- app
- features
- components
- layouts
- services
- store
- hooks
- lib
- config
- types
- styles
- public
```

## Quick Start

```bash
cd frontend/alici-platform
npm install
npm run dev
```

Set API URL:

```bash
cp .env.example .env.local
```

## Scaffold Scripts

From repository root:

PowerShell:

```powershell
./scripts/create-alici-structure.ps1
```

Bash:

```bash
bash ./scripts/create-alici-structure.sh
```

Both scripts create and expand folder/module structure without removing existing files.

## Current Included Modules

- Dashboard feature with:
- page composition
- dedicated hook
- service layer
- zustand store
- typed contracts
- reusable components
- Agents feature with page, service, store and hooks
- Workflows feature with page, service, store and hooks
- Billing feature with page, service, store and hooks
- Integrations feature with page, service, store and hooks
- API client with auth interceptors and token refresh flow
- UI kit base: Button, Card, Input, Modal, Badge, Tabs, Table, Select, Dropdown, Tooltip

## Next Recommended Steps

1. Add auth feature module (`features/auth`) with route guards.
2. Add shared design system components under `components/ui`.
3. Connect `dashboardService` to real backend endpoint `/dashboard`.
4. Add test stack (Vitest + Testing Library + Playwright).
