# 🧪 Guia de Teste - Tema e Preferências de Usuário

## Status da Implementação

✅ **Backend**: Testes passando (4/4)
✅ **Frontend**: Build produção compilado com sucesso
✅ **Integração**: ThemeProvider integrado ao app
✅ **Funcionalidade**: Pronto para teste end-to-end

---

## Como Testar Localmente

### 1. Iniciar Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Disponível em `http://localhost:8000`

### 2. Iniciar Frontend (Dev)

```bash
cd frontend
npm run dev
```

Disponível em `http://localhost:5173`

### 3. Cenário de Teste - Autenticação + Carregamento de Tema

**Passos:**

1. **Ir para login**: `http://localhost:5173/login`
2. **Fazer login** com credenciais válidas
3. **Observar**: Ao entrar na plataforma, `useInitializeTheme()` carrega automaticamente
   - Verifica localStorage (cache rápido)
   - Requisita `/api/account/preferences` ao backend
   - Aplica tema ao DOM

### 4. Cenário de Teste - Alterar Preferências

**Passos:**

1. **Ir para**: `/app/account/personalization`
2. **Alterações visuais** (preview atualiza em tempo real):
   - Alterar "Tema" de `dark` para `light`
   - Observar `<ThemePreview>` mudar cores/fundo
   - Alterar "Cor de destaque" para `blue`
   - Observar preview refletir mudança
3. **Clicar** "Salvar alterações"
4. **Observar**:
   - Spinner de loading
   - API PUT para `/api/account/preferences`
   - Toast "Preferências atualizadas com sucesso"
   - Elementos da página **refletem mudança imediatamente**
5. **Recarregar página** (F5)
6. **Verificar**: Tema persiste ✅

---

## Cenários de Teste Avançados

### Teste A: Sincronização com localStorage

```javascript
// Console do navegador (DevTools > Console)
JSON.parse(localStorage.getItem('axi_theme_cache'))
// Saída esperada:
// { theme_mode: 'dark', accent_color: 'cyan' }
```

### Teste B: Verificar Aplicação ao DOM

```javascript
// Console do navegador
document.documentElement.getAttribute('data-theme')
// Saída: 'dark' ou 'light'

document.documentElement.getAttributeNS(null, 'data-accent')
// Saída: 'cyan' ou outra cor

getComputedStyle(document.documentElement)
  .getPropertyValue('--accent-color')
// Saída: '#6ee7f9' (HEX da cor)
```

### Teste C: Múltiplas Abas (Sincronização)

1. **Abrir duas abas** do app em `localhost:5173`
2. **Aba 1**: Ir para `/app/account/personalization`
3. **Aba 1**: Alterar tema para `light` e salvar
4. **Aba 2**: Recarregar (F5)
5. **Aba 2**: Tema também está `light` ✅ (persistência em banco)

### Teste D: Logout e Re-login

1. **Fazer login** com usuário A, tema `dark`
2. **Alterar** para `light` e salvar
3. **Logout**
4. **Login novamente** com usuário A
5. **Tema aparece `light`** ✅

### Teste E: Diferentes Usuários

1. **Usuário A**: Login, alterar para `light`, salvar
2. **Usuário A**: Logout
3. **Usuário B**: Login
4. **Usuário B**: Tema é `dark` (padrão dele) ✅
5. **Usuário B**: Alterar para `orange`, salvar
6. **Usuário B**: Logout
7. **Usuário A**: Login
8. **Usuário A**: Tema é `light` ✅ (suas preferências)

---

## Verificação de Endpoints

### GET /api/account/preferences

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/account/preferences
```

**Resposta esperada:**
```json
{
  "language": "pt-BR",
  "voice": "neutral",
  "theme_mode": "dark",
  "accent_color": "cyan",
  "haptic_feedback": false,
  "background_conversation": true,
  "autocomplete": true,
  "trending": true,
  "sequence": false,
  "split_mode": false
}
```

### PUT /api/account/preferences

```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "pt-BR",
    "voice": "neutral",
    "theme_mode": "light",
    "accent_color": "blue",
    "haptic_feedback": false,
    "background_conversation": true,
    "autocomplete": true,
    "trending": true,
    "sequence": false,
    "split_mode": false
  }' \
  http://localhost:8000/api/account/preferences
```

---

## Estrutura de Componentes

```
App (main.tsx)
└── ThemeProvider ✅ (ThemeContext.tsx)
    └── AuthProvider
        └── ToastProvider
            └── AppRouter
                └── ProtectedRoute
                    ├── useInitializeTheme() ✅ (carrega prefs ao login)
                    └── PlatformShell
                        └── AccountShell
                            ├── AccountPersonalizationPage ✅
                            │   └── PreferencesForm ✅
                            │       └── ThemePreview ✅
                            └── AccountLanguagePage ✅
```

---

## Arquivos Críticos

| Arquivo | Propósito | Status |
|---------|-----------|--------|
| `frontend/src/contexts/ThemeContext.tsx` | Contexto global + applyTheme() | ✅ |
| `frontend/src/hooks/useInitializeTheme.ts` | Inicialização ao login | ✅ |
| `frontend/src/components/account/ThemePreview.tsx` | Preview em tempo real | ✅ |
| `frontend/src/utils/colorMap.ts` | Mapeamento de cores | ✅ |
| `frontend/src/router/ProtectedRoute.tsx` | Inicializa tema | ✅ |
| `frontend/src/components/account/pages/AccountPersonalizationPage.tsx` | Página de preferências | ✅ |
| `frontend/src/components/account/pages/AccountLanguagePage.tsx` | Página de idioma | ✅ |
| `backend/app/api/routes/account.py` | Rotas de preferências | ✅ |
| `backend/app/services/account_service.py` | Lógica de persistência | ✅ |
| `backend/app/models/setting.py` | Modelo UserSettings | ✅ |

---

## Checklist de Validação

- [ ] Login automáticamente carrega tema do usuário
- [ ] Preview atualiza conforme altera opções
- [ ] "Salvar alterações" persiste no backend
- [ ] Página reflete tema após salvar
- [ ] Recarregar mantém tema
- [ ] Logout e login mantém preferências
- [ ] localStorage tem `axi_theme_cache`
- [ ] DOM tem `data-theme` e `data-accent`
- [ ] CSS variable `--accent-color` contém HEX
- [ ] Toast aparece após salvar
- [ ] Múltiplos usuários têm preferências independentes

---

## Troubleshooting

**P: Tema não persiste após reload?**
A: Verificar:
1. `getAccountPreferences()` retorna 200
2. localStorage tem `axi_theme_cache`
3. Usuário está autenticado

**P: Preview não atualiza?**
A: Verificar:
1. `ThemePreview` está renderizando em `PreferencesForm`
2. Props `accentColor` e `themeMode` são passadas corretamente

**P: Cor de destaque não muda visualmente?**
A: Verificar:
1. `applyTheme()` está sendo chamado
2. `--accent-color` CSS variable está sendo setada
3. Componentes usam `var(--accent-color)` ou classes Tailwind

---

## Conclusão

A implementação está **completa e pronta para teste**. Todos os componentes estão integrados, testes passando, e a build do frontend está compilada com sucesso.
