# 🚀 GUIA DEPLOY RENDER.COM

## ⚡ Quick Deploy (5 minutos)

### 1️⃣ Preparar Repositório GitHub

Seu repositório já está pronto em: **https://github.com/matteusnascimento/alici.ai**

Verifique se tem:
```
✅ main.py
✅ requirements.txt
✅ Procfile
✅ .env.example
✅ runtime.txt
```

### 2️⃣ Criar Banco de Dados Neon

```
1. Ir a https://neon.tech
2. Sign up (grátis)
3. Criar projeto "alici"
4. Copiar "CONNECTION STRING":
   postgresql://user:password@host.neon.tech/alici?sslmode=require
```

**Guarde esta string!** Será usada em Render.

### 3️⃣ Criar Aplicação em Render

```
1. Ir a https://render.com
2. Sign up (grátis com email)
3. Dashboard → "New +" → "Web Service"
4. Conectar repositório GitHub:
   - Selecione: matteusnascimento/alici.ai
   - Branch: main
   - Build command: pip install -r requirements.txt
   - Start command: gunicorn main:app
```

### 4️⃣ Configurar Variáveis de Ambiente

Em Render → Settings → Environment Variables:

```
DATABASE_URL = postgresql://user:password@host.neon.tech/alici?sslmode=require
PYTHON_VERSION = 3.11
FLASK_ENV = production
```

**⚠️ CRÍTICO**: Colar exatamente a string do Neon em `DATABASE_URL`

### 5️⃣ Deploy!

Render detecta `Procfile` e inicia automaticamente.

Você verá:
```
Building...
Installing dependencies...
Starting web service...
✅ Live at: https://alici-ai.onrender.com
```

---

## 🔧 Troubleshooting Render

### ❌ "Build failed"
```
Solução:
1. Verificar requirements.txt
2. Em Render → Logs → ver erro específico
3. git push novamente
```

### ❌ "Application error"
```
Solução:
1. DATABASE_URL configurada?
2. Executar: python init_db.py (cria tabela)
3. Ver logs em Render dashboard
```

### ❌ "timeout after 30s"
```
Solução:
1. Aumentar timeout em Procfile:
   web: gunicorn main:app --timeout 60
2. git push novamente
```

### ❌ "Database connection refused"
```
Solução:
1. Testar DATABASE_URL localmente:
   python -c "from database import conectar; conectar()"
2. Verificar IP whitelist no Neon (deve estar vazio = open)
```

---

## 📊 Monitorar Aplicação

### Ver Logs em Tempo Real
```
Em Render Dashboard:
  Serviços → alici-ai → Logs
  (auto-refresh)
```

### Testar Endpoint
```bash
# Replace YOUR_URL com https://alici-ai.onrender.com

curl -X POST YOUR_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"quem é você"}'

# Response esperada:
{
  "resposta": "Olá! Eu sou a Alici..."
}
```

### Ver Banco de Dados
```
Em Neon Dashboard:
  Projects → alici → Tables
  Query editor para ver dados
```

---

## 🔄 Deploy Automático com Git

Render deteta **automaticamente** quando você faz `git push`:

```bash
# Seu código local
git add .
git commit -m "feat: Adicionar nova funcionalidade"
git push

# Em 30 segundos:
# Render detecta push
# Faz rebuild
# Redeploy automático
# ✅ Vivo em produção
```

---

## 💰 Custos

| Serviço | Plano Grátis | Preço |
|---------|-------------|-------|
| Render.com | ✅ Sim | $7/mês depois |
| Neon PostgreSQL | ✅ Sim (3GB) | $14/mês depois |
| **Total** | **✅ Grátis** | ~$21/mês depois |

---

## 🎯 Checklist Deploy

- [ ] Repository pronto no GitHub
- [ ] Neon banco criado
- [ ] DATABASE_URL copiada
- [ ] Render app criado
- [ ] Variáveis de ambiente configuradas
- [ ] Procfile correto
- [ ] git push feito
- [ ] ✅ Aplicação live!

---

## 📝 Próximas Features em Produção

Quando quiser adicionar novas features:

```bash
# 1. Desenvolver localmente
# 2. Testar com: python main.py
# 3. Commit + Push
git push

# 4. Render faz rebuild automaticamente
# 5. Novo código já está em produção!
```

---

**URL Final**: https://alici-ai.onrender.com ✅
