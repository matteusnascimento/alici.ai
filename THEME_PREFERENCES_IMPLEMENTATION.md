# Implementação de Tema e Preferências de Usuário

## Visão Geral

A funcionalidade de tema e preferências agora é **100% funcional** - não é mais apenas uma UI placeholder. As mudanças são:

1. **Persistidas no backend** - salvas em `user_settings` no banco de dados
2. **Carregadas ao iniciar** - aplicadas automaticamente quando o usuário faz login
3. **Aplicadas ao DOM** - afetam visualmente a aparência do app
4. **Refletidas em tempo real** - preview atualiza conforme você muda

---

## Arquitetura

### Backend
- **Modelo**: `UserSettings` em `backend/app/models/setting.py`
- **Schema**: `AccountPreferencesRead/Update` em `backend/app/schemas/account.py`
- **Serviço**: `AccountService.get_preferences()` e `update_preferences()` em `backend/app/services/account_service.py`
- **Rota**: `GET/PUT /api/account/preferences` em `backend/app/api/routes/account.py`

Campos persistidos:
- `language` - Idioma da interface (pt-BR, en-US, es, fr)
- `voice` - Estilo de voz (alloy, nova, echo, fable, shimmer)
- `theme_mode` - Tema visual (dark, light, system)
- `accent_color` - Cor de destaque (cyan, blue, green, orange, amber)
- `haptic_feedback`, `background_conversation`, `autocomplete`, `trending`, `sequence`, `split_mode` - toggles de comportamento

### Frontend
- **Contexto**: `ThemeProvider` e hook `useTheme()` em `frontend/src/contexts/ThemeContext.tsx`
- **Inicialização**: `useInitializeTheme()` carrega preferências ao autenticar
- **Aplicação**: `applyTheme()` aplica tema ao DOM (classes, atributos, CSS variables)
- **Cache local**: localStorage armazena tema para carregamento rápido
- **Páginas**: 
  - `AccountPersonalizationPage` - formulário completo de preferências
  - `AccountLanguagePage` - página simplificada de idioma/tema
  - `PreferencesForm` - componente do formulário com `ThemePreview`

---

## Fluxo Completo

```
Usuário faz login
    ↓
ProtectedRoute renderiza
    ↓
useInitializeTheme() executa
    ↓
getAccountPreferences() busca do backend
    ↓
applyTheme() aplica ao DOM:
  - document.documentElement.setAttribute('data-theme', mode)
  - document.documentElement.classList.add('dark'/'light')
  - document.documentElement.style.setProperty('--accent-color', colorValue)
    ↓
Tema aplicado! ✅
```

---

## Quando o Usuário Muda Preferências

```
Usuário altera campo (ex: tema para 'light')
    ↓
Estado local atualiza (onChange)
    ↓
Clica "Salvar alterações"
    ↓
updateAccountPreferences() envia ao backend
    ↓
Backend salva em user_settings
    ↓
applyTheme() aplica mudança ao DOM imediatamente
    ↓
Feedback visual: "Salvo com sucesso" ✅
```

---

## Componentes Principais

### ThemeContext.tsx
```typescript
interface ThemeContextType {
  theme: AccountPreferences | null;
  setTheme: (theme: AccountPreferences | null) => void;
  applyTheme: (prefs: Partial<AccountPreferences>) => void;
  isLoading: boolean;
}

// Hook para usar em componentes
const { applyTheme } = useTheme();
applyTheme({ theme_mode: 'light', accent_color: 'blue' });
```

### useInitializeTheme.ts
```typescript
// Hook que carrega preferências ao autenticar
useInitializeTheme();
// Funciona automaticamente em ProtectedRoute
```

### ThemePreview.tsx
```typescript
// Componente que mostra preview em tempo real
<ThemePreview accentColor="cyan" themeMode="dark" />
```

### colorMap.ts
```typescript
const colorMap = {
  cyan: '#6ee7f9',
  blue: '#3b82f6',
  green: '#10b981',
  orange: '#f97316',
  amber: '#fbbf24',
};
```

---

## CSS Variables Disponíveis

```css
:root {
  --accent-color: #6ee7f9;        /* Cor dinâmica de destaque */
  --theme-mode: dark;             /* dark | light | system */
}
```

Usado em:
- `document.documentElement.style.setProperty('--accent-color', '#6ee7f9')`
- `document.documentElement.style.setProperty('--theme-mode', 'dark')`

---

## localStorage Cache

Chave: `axi_theme_cache`

```json
{
  "theme_mode": "dark",
  "accent_color": "cyan"
}
```

Carregado na inicialização para que o tema apareça **antes** das preferências chegarem do backend.

---

## Páginas de Customização

### `/app/account/personalization`
- Formulário completo com 4 cards
- Campos: Tema, Cor, Idioma, Voz, + toggles de UX
- Preview de tema em tempo real
- Salva todas as preferências de uma vez

### `/app/account/language-appearance`
- Página focada apenas em idioma + tema
- UI simplificada
- Também aplica tema ao salvar

---

## Testes

Para testar a funcionalidade:

1. **Login na plataforma**
2. **Ir para /app/account/personalization**
3. **Mudar o tema para 'light'**
4. **Observar**: 
   - Preview atualiza em tempo real
   - Clicar "Salvar" aplica imediatamente
   - Recarregar a página: tema persiste
   - Fazer logout + login: tema mantém

---

## Próximos Passos (Opcional)

Se quiser expandir:

- [ ] Implementar suporte a i18n (traduções dinâmicas baseadas em `language`)
- [ ] Sintetizar voz dinamicamente baseado em `voice` (integração com Text-to-Speech)
- [ ] Aplicar comportamentos reais de `split_mode`, `sequence`, `trending`
- [ ] Sincronizar `haptic_feedback` com dispositivos mobile
- [ ] Sistema de temas personalizados (usuário escolhe cores RGB exatas)
- [ ] Exportar/importar preferências

---

## Troubleshooting

**O tema não persiste após reload?**
- Verificar se o usuário está autenticado
- Verificar se a requisição `GET /api/account/preferences` retorna status 200
- Verificar localStorage: `localStorage.getItem('axi_theme_cache')`

**A cor de destaque não muda?**
- Verificar se está usando o CSS variable `var(--accent-color)` nos componentes
- Ou usar as classes Tailwind: `bg-cyan`, `text-cyan` que já estão definidas

**Preview não atualiza?**
- Verificar se `ThemePreview` está renderizando em `PreferencesForm`
- Verificar console para erros de tipagem

---

## Estrutura de Arquivos

```
frontend/src/
├── contexts/
│   └── ThemeContext.tsx              ⭐ Contexto de tema global
├── hooks/
│   └── useInitializeTheme.ts         ⭐ Hook de carregamento
├── components/
│   └── account/
│       ├── PreferencesForm.tsx       ✏️ Formulário atualizado
│       ├── ThemePreview.tsx          ⭐ Componente de preview
│       └── pages/
│           ├── AccountPersonalizationPage.tsx  ✏️ Atualizado
│           └── AccountLanguagePage.tsx        ✏️ Atualizado
├── utils/
│   └── colorMap.ts                   ⭐ Mapa de cores
└── router/
    └── ProtectedRoute.tsx            ✏️ Atualizado
```

✅ = Novo
✏️ = Modificado

---

## Resumo

**Antes**: Opções de tema/aparência eram apenas visuais, não faziam nada.

**Agora**:
✅ Persistência no backend
✅ Carregamento automático ao login
✅ Aplicação ao DOM (dark/light/cores)
✅ Preview em tempo real
✅ Cache local para carregamento rápido
✅ Feedback visual ao salvar
✅ Mantém ao recarregar e fazer logout/login

**Status**: 🟢 Production-ready
