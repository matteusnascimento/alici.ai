# 🤖 ALICI - Deploy no Render

## Instruções de Deploy

### 1. **Preparar o Repositório Git**

```bash
cd c:\alici.ai
git add .
git commit -m "🚀 ALICI Production Ready - Deploy Render"
git push origin main
```

### 2. **Configurar no Render.com**

#### a) Criar novo Web Service
1. Acesse [render.com](https://render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub

#### b) Configurações do Serviço

| Campo | Valor |
|-------|-------|
| **Name** | alici-api |
| **Runtime** | Python 3.11 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn main:app --workers 2 --bind 0.0.0.0:$PORT --timeout 60` |

#### c) Variáveis de Ambiente

Adicione em "Environment":
```
DATABASE_URL=postgresql://[user]:[pass]@[neon-host].neon.tech/alici?sslmode=require
SECRET_KEY=[seu-secret-key-aleatorio]
PORT=8000
```

### 3. **Configurar Banco de Dados Neon**

1. Acesse [neon.tech](https://neon.tech)
2. Crie um novo projeto PostgreSQL
3. Copie a CONNECTION STRING
4. Cole em `DATABASE_URL` no Render

### 4. **Deploy**

O Render fará auto-deploy toda vez que você fizer push para main:

```bash
git push origin main
```

---

## 🎯 Endpoints Disponíveis (após deploy)

```
GET  /                    → UI Holográfica
POST /chat                → Chat ALICI
GET  /status              → Health Check
```

---

## 📋 Checklist de Produção

- [x] Procfile configurado
- [x] requirements.txt atualizado
- [x] .env.example criado
- [x] runtime.txt com Python 3.11
- [x] .renderignore criado
- [x] build.sh com setup
- [x] Testes passando (✅ 3/3)
- [x] Modelo CIFAR-100 treinado
- [x] Git pronto para push

---

## 🔑 Variáveis Críticas

### DATABASE_URL (OBRIGATÓRIO)
```
postgresql://[user]:[password]@[host].neon.tech/[dbname]?sslmode=require
```

### SECRET_KEY (OBRIGATÓRIO)
```bash
# Gerar uma nova chave
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ✅ Próximas Ações

1. ✅ Fazer push para GitHub
2. ✅ Conectar repositório no Render
3. ✅ Configurar variáveis de ambiente
4. ✅ Configurar banco Neon
5. ✅ Deploy automático

---

## 🚀 Status: PRONTO PARA PRODUÇÃO!

```
✅ ALICI responde
✅ ALICI aprende
✅ ALICI pesquisa
✅ Testes: 100% passou
✅ Modelo: Treinado
✅ Deploy: Configurado
```
