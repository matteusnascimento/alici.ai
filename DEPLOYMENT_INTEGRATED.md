# 🚀 ALICI™ - Guia Integrado de Deployment

## 📋 Visão Geral

Este guia consolida todas as informações para fazer deploy da ALICI em produção.

---

## 🎯 Opções de Deploy

### 1️⃣ Render.com (Recomendado - Grátis)
- ✅ Deploy automático via GitHub
- ✅ SSL gratuito
- ✅ Domínio grátis (.onrender.com)
- ⚠️ Cold start (~1 min após 15 min inativo)

### 2️⃣ Heroku
- ✅ Simples de usar
- ✅ Add-ons PostgreSQL
- ❌ Não é mais grátis (mínimo $7/mês)

### 3️⃣ AWS/DigitalOcean/GCP
- ✅ Total controle
- ✅ Sem cold starts
- ❌ Mais complexo
- ❌ Custo variável

### 4️⃣ Docker (Qualquer provedor)
- ✅ Portável
- ✅ Reprodutível
- ⚠️ Requer conhecimento Docker

---

## 🚀 Deploy no Render.com

### Pré-requisitos

1. Conta GitHub: https://github.com
2. Conta Render: https://render.com
3. Conta Neon (PostgreSQL): https://neon.tech

### Passo 1: Preparar Banco de Dados (Neon)

1. Acessar https://neon.tech
2. Criar conta (grátis)
3. Criar novo projeto:
   - Nome: `alici-production`
   - Região: `US East (Ohio)` ou mais próximo
4. Copiar **Connection String**:
   ```
   postgresql://user:password@host.neon.tech/alici?sslmode=require
   ```

### Passo 2: Push para GitHub

```bash
# Clonar localmente (se ainda não tem)
git clone https://github.com/matteusnascimento/alici.ai.git
cd alici.ai

# Fazer alterações (se necessário)
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Passo 3: Configurar Render

1. Acessar https://dashboard.render.com
2. Clicar **New +** → **Web Service**
3. Conectar repositório GitHub:
   - Repository: `matteusnascimento/alici.ai`
   - Branch: `main`

4. Configurar Service:
   ```
   Name: alici-ai
   Environment: Python 3
   Region: Oregon (ou mais próximo)
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. Selecionar plan:
   - **Free** (recomendado para testes)
   - Limitações: 750h/mês, sleep após 15 min inativo

6. **Environment Variables** (IMPORTANTE):
   ```
   DATABASE_URL = postgresql://user:password@host.neon.tech/alici?sslmode=require
   FLASK_ENV = production
   DEBUG = False
   SECRET_KEY = [gerar chave secreta forte]
   ```

7. Clicar **Create Web Service**

### Passo 4: Inicializar Banco

Após deploy, executar uma vez:

**Opção A - Via Shell Render:**
1. Dashboard → Service → Shell
2. Executar:
   ```bash
   python init_db.py
   ```

**Opção B - Via Script Local:**
```bash
# Localmente, com DATABASE_URL de produção
DATABASE_URL="postgresql://..." python init_db.py
```

### Passo 5: Verificar

Acessar:
```
https://alici-ai.onrender.com/health
```

Deve retornar:
```json
{
  "status": "ok",
  "ia_disponivel": true,
  "timestamp": "2026-02-02T..."
}
```

---

## 🐳 Deploy com Docker

### Dockerfile

Crie `Dockerfile` na raiz:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

Para desenvolvimento local com PostgreSQL:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: alici
      POSTGRES_USER: alici
      POSTGRES_PASSWORD: alici123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://alici:alici123@db:5432/alici
      FLASK_ENV: development
      DEBUG: True
    depends_on:
      - db
    volumes:
      - .:/app

volumes:
  postgres_data:
```

### Executar

```bash
# Build
docker-compose build

# Run
docker-compose up

# Inicializar DB
docker-compose exec app python init_db.py

# Acessar
# http://localhost:8000
```

---

## ☁️ Deploy em Outros Provedores

### Heroku

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Criar app
heroku create alici-ai

# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main

# Configurar env vars
heroku config:set FLASK_ENV=production
heroku config:set DEBUG=False

# Inicializar DB
heroku run python init_db.py

# Verificar
heroku open
```

### AWS Elastic Beanstalk

```bash
# Instalar EB CLI
pip install awsebcli

# Inicializar
eb init -p python-3.11 alici-ai

# Criar ambiente
eb create alici-production

# Deploy
eb deploy

# Configurar RDS PostgreSQL separadamente
# E adicionar DATABASE_URL nas env vars
```

### DigitalOcean App Platform

1. Dashboard → Apps → Create App
2. Conectar GitHub
3. Configurar:
   - Type: Web Service
   - Build: `pip install -r requirements.txt`
   - Run: `uvicorn main:app --host 0.0.0.0 --port 8080`
4. Adicionar PostgreSQL Database
5. Deploy

---

## 🔒 Segurança em Produção

### Variáveis de Ambiente Críticas

**NUNCA commitar .env no Git!**

```bash
# .gitignore deve conter:
.env
*.env
.env.*
```

### Gerar SECRET_KEY Forte

```python
import secrets
print(secrets.token_urlsafe(32))
# Use este valor em SECRET_KEY
```

### HTTPS/SSL

- Render.com: SSL automático ✅
- Docker: Use nginx + Let's Encrypt
- AWS: Use Load Balancer com ACM

### Rate Limiting

Adicionar em `main_auth.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("20/minute")
def chat(request: Request, ...):
    # ...
```

### Monitoramento

```python
# Adicionar logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.post("/chat")
def chat(...):
    logger.info(f"User {user['id']} asked: {req.pergunta[:50]}")
    # ...
```

---

## 📊 Monitoramento e Logs

### Render Logs

```bash
# Via dashboard
Render Dashboard → Service → Logs (live tail)

# Via CLI
render logs -s alici-ai -f
```

### Métricas

Adicionar endpoint de métricas:

```python
@app.get("/metrics")
def metrics():
    # Usar Prometheus client
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")
```

### Alertas

Configurar em Render:
- Dashboard → Service → Settings → Notifications
- Webhook para Slack/Discord/Email

---

## 🔄 CI/CD

### GitHub Actions

Criar `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python teste_engine_completo.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

---

## 🐛 Troubleshooting em Produção

### Cold Starts (Render Free Tier)

**Sintoma:** Primeiro request lento (~30-60s)

**Soluções:**
1. Upgrade para Render Paid ($7/mês)
2. Keep-alive ping externo:
   ```bash
   # Cron job a cada 10 minutos
   */10 * * * * curl https://alici-ai.onrender.com/health
   ```

### Database Connection Timeout

**Sintoma:** `could not connect to server`

**Soluções:**
1. Verificar DATABASE_URL está correta
2. Neon: Verificar IP whitelist (Neon Free Tier não requer)
3. Aumentar connection pool:
   ```python
   conn = psycopg2.connect(
       DATABASE_URL,
       connect_timeout=10,
       options="-c statement_timeout=30000"
   )
   ```

### Out of Memory

**Sintoma:** Render logs mostram `OOMKilled`

**Soluções:**
1. Não carregar todos os modelos .h5 de uma vez
2. Lazy loading:
   ```python
   modelo = None
   def get_modelo():
       global modelo
       if modelo is None:
           modelo = tf.keras.models.load_model("modelo.h5")
       return modelo
   ```
3. Upgrade para plan maior

---

## 📈 Escalabilidade

### Horizontal Scaling

```yaml
# render.yaml
services:
  - type: web
    name: alici-api
    env: python
    numInstances: 3  # 3 instances
    plan: standard
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def buscar_memoria_cached(pergunta):
    return buscar_memoria(pergunta)
```

### Database Pooling

```python
import psycopg2.pool

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)
```

---

## ✅ Checklist de Deploy

- [ ] Código testado localmente
- [ ] .env em .gitignore
- [ ] requirements.txt atualizado
- [ ] Banco Neon criado e DATABASE_URL configurada
- [ ] Push para GitHub
- [ ] Render service criado
- [ ] Environment variables configuradas
- [ ] Deploy realizado
- [ ] init_db.py executado
- [ ] /health endpoint testado
- [ ] Login/registro testado
- [ ] Chat testado
- [ ] Logs monitorados

---

## 📞 Suporte

- **GitHub Issues**: https://github.com/matteusnascimento/alici.ai/issues
- **Render Docs**: https://render.com/docs
- **Neon Docs**: https://neon.tech/docs

---

**Última atualização**: 2026-02-02
