# Deploy Frontend no Render — Passo a Passo Exato

## Estado Atual

```
Backend:  ✅ https://alici-ai.onrender.com (Web Service)
Frontend: ❌ (não publicado — Static Site precisa ser criado)
```

---

## Pré-requisitos

- [ ] Repositório GitHub com código atualizado (✅ já feito em main)
- [ ] Conta Render (você já tem)
- [ ] render.yaml com serviço axi-frontend definido (✅ já existe)

---

## Passo 1: Ir para o Render Dashboard

1. Abra: https://dashboard.render.com
2. Faça login com sua conta do GitHub

---

## Passo 2: Criar novo Static Site

1. Clique em **`New +`** (canto superior direito)
2. Escolha **`Static Site`**

---

## Passo 3: Conectar repositório

1. Escolha **`Deploy existing repository`**
2. Procure por: `alici.ai`
3. Clique em **`Connect`** (do lado direito do repo)

---

## Passo 4: Configurar o serviço

### Name

```
axi-frontend
```

### Root Directory

```
frontend
```

### Build Command

```bash
npm install && npm run build
```

### Publish Directory

```
dist
```

### (Opcional) Environment Variables

Se quiser override, adicione:

```
VITE_API_URL = https://alici-ai.onrender.com/api
```

(Foi definido no render.yaml, mas pode confirmar aqui)

---

## Passo 5: Deploy

1. Clique em **`Create Static Site`**
2. Aguarde o build:
   - npm install (30-60s)
   - npm run build (10-20s)
   - Upload para CDN (5-10s)

---

## Passo 6: Verificar

Quando terminar, você verá algo tipo:

```
✓ Your site is live at: https://axi-frontend.onrender.com
```

---

## Passo 7: Testar (no browser)

1. Abra: https://axi-frontend.onrender.com
2. Você deve ver:
   - Landing page (tela de login / signup)
   - Dashboard (se já logado)
   - Sem erro de CORS
   - Sem erro 50x no console

---

## Checklist de Validação

- [ ] Frontend abre sem erro
- [ ] Página de login carrega
- [ ] Network tab mostra `/api/*` chamando `https://alici-ai.onrender.com/api`
- [ ] Login funciona (cria usuário ou retorna token)
- [ ] Dashboard carrega após login
- [ ] `/health` do backend responde (teste em https://alici-ai.onrender.com/health)

---

## Troubleshooting

### Build falhou com "npm command not found"

❌ Problema: Node.js não está instalado

✅ Fix: Render detecta `package.json` e instala automaticamente. Se falhar, cheque se há `package.json` na raiz de `frontend/`.

### Site abre mas mostra 404

❌ Problema: Root Directory não está correto

✅ Fix: Vá para Settings > Root Directory, confirme: `frontend`

### API retorna erro de CORS

❌ Problema: Backend CORS_ALLOWED_ORIGINS não inclui frontend URL

✅ Fix: Ir no backend Web Service → Settings → Environment → confirme:

```
CORS_ALLOWED_ORIGINS = https://axi-frontend.onrender.com
```

Se changed, clique Deploy → redeploy backend

### Login não funciona

❌ Problema: Frontend não consegue chegar na API

✅ Testes:
1. Abra DevTools (F12)
2. Vá em Network
3. Tente fazer login
4. Clique na requisição POST `/auth/login`
5. Veja o URL completo que foi chamado
6. Teste no postman: `curl -X POST https://alici-ai.onrender.com/api/auth/login ...`

---

## URLs Finais

| Serviço  | URL                                    |
|----------|----------------------------------------|
| Frontend | https://axi-frontend.onrender.com      |
| Backend  | https://alici-ai.onrender.com          |
| Docs API | https://alici-ai.onrender.com/docs     |
| Health   | https://alici-ai.onrender.com/health   |

---

## Próximos Passos (depois de validar)

1. ✅ Frontend e backend rodando
2. ⏳ Setup de domínio customizado (ex: `axi.ai` → frontend, `api.axi.ai` → backend)
3. ⏳ CI/CD automático no GitHub Actions
4. ⏳ Monitoramento e alertas

---

## Dúvidas Comuns

**P: Por que separar frontend e backend?**  
R: Escalabilidade, cache, CDN, deploy independente.

**P: E o domínio principal (alici-ai.onrender.com)?**  
R: Hoje aponta para backend. Quando subir frontend, você pode redirecionar para frontend ou usar API em subdomínio. Mais detalhes no final.

**P: Preciso fazer algo no render.yaml?**  
R: Não — ele já está atualizado (Commit 7e061ba). O render.yaml tem VITE_API_URL apontando para API.

---
