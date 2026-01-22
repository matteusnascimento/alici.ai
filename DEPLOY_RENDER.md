# 🚀 DEPLOY ALICI™ NO RENDER

## ✅ Pré-requisitos

- Conta no [Render.com](https://render.com)
- PostgreSQL (recomendado: [Neon](https://neon.tech))
- GitHub conta com acesso ao repositório

---

## 📋 PASSOS DE DEPLOY

### 1️⃣ Preparar Neon (PostgreSQL)

```
1. Acesse neon.tech
2. Create new project
3. Crie um banco chamado "alici"
4. Copie a connection string: postgresql://user:password@host/alici?sslmode=require
5. Guarde para usar no Render
```

### 2️⃣ Criar Web Service no Render

```
1. Acesse render.com/dashboard
2. New → Web Service
3. Connect GitHub repository (matteusnascimento/alici.ai)
4. Configure:
   - Name: alici-api (ou seu nome)
   - Root Directory: . (raiz)
   - Runtime: Python 3.11
   - Build command: pip install -r requirements.txt
   - Start command: gunicorn main_fastapi:app -w 4
5. Create Web Service
```

### 3️⃣ Adicionar Variáveis de Ambiente

No painel do Render, vá para Environment:

```
DATABASE_URL=postgresql://user:password@neon-host/alici?sslmode=require
SECRET_KEY=sua-chave-super-secreta-mude-isso
PORT=8000
```

**IMPORTANTE**: Gere uma SECRET_KEY segura:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4️⃣ Criar Extensão pgvector no Neon

Conecte ao banco Neon (via psql ou interface) e execute:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 5️⃣ Deploy

- Push para main branch vai triggar deploy automático
- Monitore em Render dashboard
- Logs estarão visíveis em tempo real

---

## 🧪 Testar Deploy

Depois que o deploy terminar:

```bash
# Health check
curl https://seu-app.onrender.com/health

# Swagger docs
https://seu-app.onrender.com/docs

# Testar login
curl -X POST https://seu-app.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome":"Test","email":"test@example.com","senha":"password123456"}'
```

---

## ⚠️ Troubleshooting

### Build fails com "torch not found"
- Solução: pytorch é pesado. Se der erro, remova de requirements.txt temporariamente ou use versão pré-compilada

### Database connection error
- Verifique DATABASE_URL em Environment
- Confirme que pgvector extension foi criada
- Teste conexão local primeiro

### Secret key error
- Gere uma nova com: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Atualize no Render dashboard

---

## 🔄 Atualizações Futuras

Qualquer novo push para `main` vai:
1. Triggar rebuild automático
2. Executar `pip install -r requirements.txt`
3. Rodar `gunicorn main_fastapi:app -w 4`
4. Restartar o serviço

---

## 📊 Monitoramento

No Render dashboard você pode ver:
- Logs de build e runtime
- Métricas de CPU/memória
- Histórico de deploys
- Restart automático se cair

---

## 💡 Dicas

- Use `render.com/docs` para troubleshooting
- PostgreSQL Neon tem free tier generoso
- Render free tier funciona bem para MVP
- Considere pagar quando atingir 1000+ usuários

---

**Deploy está vivo quando:**
✅ Build passou
✅ Health check retorna 200
✅ Swagger docs (`:8000/docs`) está acessível

🚀 **Seu ALICI™ está no ar!**
