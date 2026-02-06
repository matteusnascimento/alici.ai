# 🚀 Deploy ALICI no Render - Guia Rápido

## ✅ Pré-requisitos

- [x] Código no GitHub: https://github.com/matteusnascimento/alici.ai
- [x] Banco Neon configurado
- [x] DATABASE_URL: `postgresql://neondb_owner:npg_YA5DVX0fvWrg@ep-frosty-shape-a8fhb2m2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require`

---

## 📋 Passo a Passo (5 minutos)

### 1️⃣ Criar Conta no Render

1. Acesse: https://dashboard.render.com
2. Clique em **"Get Started"** ou **"Sign Up"**
3. Faça login com **GitHub** (recomendado)

---

### 2️⃣ Criar Novo Web Service

1. No dashboard, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte sua conta do GitHub (se ainda não conectou)
4. Selecione o repositório: **`matteusnascimento/alici.ai`**
5. Clique em **"Connect"**

---

### 3️⃣ Configurar Web Service

Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Name** | `alici-api` (ou nome de sua escolha) |
| **Region** | `Oregon (US West)` ou mais próximo |
| **Branch** | `main` |
| **Root Directory** | _(deixe em branco)_ |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | _(auto-detecta o Procfile)_ |
| **Instance Type** | `Free` (grátis) ou `Starter` ($7/mês) |

---

### 4️⃣ Adicionar Variáveis de Ambiente

Role até **"Environment Variables"** e adicione:

```env
DATABASE_URL=postgresql://neondb_owner:npg_YA5DVX0fvWrg@ep-frosty-shape-a8fhb2m2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require

SECRET_KEY=ALICI_PRODUCTION_SECRET_KEY_2026_CHANGE_THIS

ENV=production

PORT=8000
```

**⚠️ IMPORTANTE:** Mude o `SECRET_KEY` para algo único e seguro!

**Como gerar SECRET_KEY seguro:**
```bash
# No PowerShell:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 5️⃣ Deploy Automático

1. Clique em **"Create Web Service"**
2. Aguarde o build (2-5 minutos)
3. Você verá os logs em tempo real:

```
==> Building...
Installing dependencies from requirements.txt
==> Build successful!

==> Starting...
[INFO] 🚀 Iniciando ALICI na porta 8000...
[INFO] 🗄️  Usando PostgreSQL/Neon
[INFO] ✅ Tabelas criadas com sucesso
[INFO] ✓ ALICI pronta para conversar!
==> Service is live!
```

4. URL gerada automaticamente: `https://alici-api.onrender.com`

---

## 🎉 Pronto! ALICI Online

### Acessar Chat:
```
https://alici-api.onrender.com
```

### Testar API:
```
https://alici-api.onrender.com/api/status
```

### Documentação:
```
https://alici-api.onrender.com/docs
```

---

## 🔄 Deploy Automático

Toda vez que você fizer **push** no GitHub:
1. Render detecta automaticamente
2. Faz rebuild
3. Atualiza o serviço
4. **Zero downtime!**

---

## 🌐 Domínio Customizado (Opcional)

### Se você tem um domínio próprio:

1. No Render, vá em **Settings** → **Custom Domains**
2. Clique em **"Add Custom Domain"**
3. Digite seu domínio: `alici.seusite.com`
4. Configure DNS no seu provedor:

```
Type: CNAME
Name: alici
Value: alici-api.onrender.com
```

5. Aguarde propagação DNS (5-60 minutos)
6. ✅ SSL automático via Let's Encrypt!

---

## 📊 Monitoramento

### No Dashboard do Render você pode ver:

- 📈 **Métricas**: CPU, RAM, latência
- 📝 **Logs**: Logs em tempo real
- 🔄 **Deploys**: Histórico de deployments
- ⚙️ **Settings**: Configurações e variáveis

### Logs em Tempo Real:
```bash
# Via Render CLI (opcional):
render logs alici-api --tail
```

---

## ⚡ Otimizações (Opcional)

### 1. Aumentar Performance

No Render, ajuste:
- **Instance Type**: Starter ($7/mês)
- **Auto-deploy**: Enabled
- **Health Check Path**: `/api/status`

### 2. Adicionar Redis (Cache)

```env
REDIS_URL=redis://...
```

### 3. Background Workers

Para tarefas pesadas, crie um **Background Worker** separado.

---

## 🆘 Troubleshooting

### "Application failed to start"

**Solução:**
1. Verifique logs no Dashboard
2. Certifique-se que `DATABASE_URL` está correto
3. Verifique se `requirements.txt` tem todas as dependências

### "502 Bad Gateway"

**Solução:**
1. Aguarde 1-2 minutos (cold start)
2. Verifique se PORT=8000 está nas variáveis
3. Reinicie o serviço: Settings → Manual Deploy

### "Database connection failed"

**Solução:**
1. Teste conexão no Neon: https://console.neon.tech
2. Verifique se `sslmode=require` está na DATABASE_URL
3. Confirme que o banco não está pausado (Neon scale-to-zero)

---

## 💰 Custos

### Free Tier (Render):
- ✅ 750 horas/mês grátis
- ✅ SSL automático
- ⚠️ Sleep após 15 min inativo
- ⚠️ Cold start: ~30 segundos

### Starter ($7/mês):
- ✅ Sempre ativo (sem sleep)
- ✅ Mais CPU/RAM
- ✅ Melhor performance

### Neon (Banco):
- ✅ 3GB grátis
- ✅ Scale-to-zero
- ✅ SSL incluído

---

## 🎯 Checklist Final

- [ ] Render conectado ao GitHub
- [ ] DATABASE_URL configurado
- [ ] SECRET_KEY mudado para produção
- [ ] Build bem-sucedido
- [ ] Chat acessível na URL pública
- [ ] API `/api/status` retorna OK
- [ ] Usuários conseguem se registrar
- [ ] Histórico salva no Neon
- [ ] Auto-deploy funcionando

---

## 🚀 Links Úteis

- **Render Dashboard:** https://dashboard.render.com
- **Neon Console:** https://console.neon.tech
- **Seu Repositório:** https://github.com/matteusnascimento/alici.ai
- **Documentação Render:** https://render.com/docs

---

✅ **ALICI agora está na nuvem! 🌐**

**Criado por:** Mateus Nascimento dos Santos  
**Email:** mateus-nascimentodossantos@hotmail.com  
**Instagram:** @matteus_nascimento_ofc
