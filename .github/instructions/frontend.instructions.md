---
applyTo: "frontend/src/**/*.{ts,tsx}"
---

# Padrões Frontend — alici.ai

## Chamadas de API
- Sempre usar `apiFetch<T>()` de `services/api.ts`; nunca `fetch()` direto
- Tratar erros com `catch (err) { setError(err instanceof ApiError ? err.message : 'Erro') }`
- Token em `localStorage` com chave `axi_token` — já gerenciado por `api.ts`, não manipular diretamente

## Componentes React
- Componentes funcionais; ordem: tipos/interface → estado → handlers → return JSX
- Loading com `boolean`; erro com `string | null`
- Props interface explícita acima do componente (não inline)

## TypeScript
- Interfaces de domínio em `src/types/`; um arquivo por domínio
- Campos opcionais com `| null` ou `?`; evitar `any`

## Tailwind
- Paleta: `cyan` = primária, `rose` = erro, `slate` = neutro
- Bordas glass: `border border-white/10`; fundos: `bg-white/5`
- Desabilitar botões: `disabled:opacity-50 disabled:cursor-not-allowed`

## Roteamento
- Rotas de app autenticado sob `/app/...`
- Usar `react-router-dom` — não manipular `window.location` diretamente
