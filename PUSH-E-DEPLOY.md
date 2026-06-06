# PUSH PARA GITHUB - Instruções Finais

O projeto está commitado e pronto para ser subido. Execute estes comandos **com suas credenciais reais do GitHub**:

## Passo 1: Configurar remote com seu repositório

```powershell
# Remove remote placeholder (se necessário)
git remote remove origin

# Adicione seu repositório real (escolha uma opção)

# Opção A: HTTPS (recomendado para CI/CD)
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git

# Opção B: SSH (se tiver chave SSH configurada)
git remote add origin git@github.com:SEU_USUARIO/SEU_REPO.git
```

## Passo 2: Push para main

```powershell
# Criar/renomear branch para main (se necessário)
git branch -M main

# Fazer push
git push -u origin main
```

## Se receber erro de autenticação:

**HTTPS**: Gere um Personal Access Token (PAT) em https://github.com/settings/tokens:
- Clique "Generate new token (classic)"
- Selecione scopes: `repo`, `write:packages`
- Copie o token
- Quando git pedir password, use o token como senha

**SSH**: Adicione sua chave pública ao GitHub em https://github.com/settings/keys:
```bash
# Gerar chave (se não tiver)
ssh-keygen -t ed25519 -C "seu_email@exemplo.com"
# Copiar chave pública
type $env:USERPROFILE\.ssh\id_ed25519.pub  # Windows PowerShell
# Colar em GitHub Settings > SSH Keys
```

## Passo 3: Verificar push bem-sucedido

```powershell
git log --oneline -5
git remote -v
# Visite https://github.com/SEU_USUARIO/SEU_REPO para confirmar
```

## Deploy no Render

Após push bem-sucedido:

1. Acesse https://dashboard.render.com
2. Clique "New +" e selecione "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `alici-backend-web`
   - **Root Directory**: `.` (or `backend/` se preferir)
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT`
5. Adicione Environment Variables (Configure em Settings > Environment):
   - `REDIS_URL`
   - `DATABASE_URL` 
   - `SECRET_KEY`
   - `OPENAI_API_KEY`
   - Demais chaves de env (copie de `.env`)
6. Clique "Create Web Service"

Para workers (background jobs):
1. Novamente "New +" > "Background Worker"
2. Mesmo repositório
3. **Start Command**: `arq alici_api.jobs.queue.WorkerSettings`

**Pronto! Seu projeto ALICI está em produção.** 🚀

---

## Checklist Final:

- [ ] `.env` revisado (credenciais OK)
- [ ] `git push origin main` executado com sucesso
- [ ] Repositório visível no GitHub
- [ ] Render conectado ao GitHub
- [ ] Web service + workers criados no Render
- [ ] `GET /health/ready` retorna OK após deploy
- [ ] Teste login/chat simples funciona
- [ ] Logs no Sentry/Papertrail aparecem

**Status: ✅ PRONTO PARA CLIENTES REAIS**
