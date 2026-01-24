# 🔐 ALICI™ AUTHENTICATION SYSTEM - GUIA COMPLETO

**Data:** 24 de janeiro de 2026  
**Versão:** 2.0  
**Status:** ✅ Pronto para produção

---

## 📋 Sumário Executivo

Implementei um **sistema de autenticação profissional** para a ALICI™ com:

✅ **FastAPI + JWT** - API moderna e segura  
✅ **PostgreSQL (Neon)** - Banco de dados em nuvem  
✅ **Criptografia bcrypt** - Senhas seguras  
✅ **UI moderna** - Estilo ChatGPT  
✅ **Histórico por usuário** - Memória persistente  
✅ **Sistema Free/Pro** - Preparado para monetização

---

## 🏗️ Arquitetura

```
Frontend (Login + Chat)
    ↓
FastAPI (/auth/login, /auth/register, /chat, /chat/image)
    ↓
JWT Token (autenticação stateless)
    ↓
PostgreSQL/Neon (users, history)
    ↓
ALICI™ Core (engine.py, model_inference.py)
```

---

## 📁 Arquivos Criados/Modificados

### Frontend
```
templates/
├── login.html (✅ Novo) - Tela de login + cadastro
├── chat.html (✅ Novo) - Tela de chat protegida

static/
├── login.css (✅ Novo) - Estilos ChatGPT
├── login.js (✅ Novo) - Lógica de autenticação
├── chat.css (✅ Novo) - Estilos do chat
├── chat.js (✅ Novo) - Cliente de chat
```

### Backend
```
auth.py (✅ Novo)
  - hash_password() - Criptografia bcrypt
  - verify_password() - Verificação segura
  - create_access_token() - Geração de JWT
  - decode_token() - Validação de JWT
  - verify_token() - Verificação com "Bearer"

database_auth.py (✅ Novo)
  - criar_usuario() - INSERT em users
  - buscar_usuario_por_email() - SELECT
  - buscar_usuario_por_id() - SELECT
  - salvar_historico() - INSERT em history
  - buscar_historico() - SELECT com limite
  - criar_tabelas() - Setup inicial

main_auth.py (✅ Novo)
  - FastAPI app
  - Endpoints de autenticação
  - Endpoints de chat (protegidos)
  - Endpoints de histórico
  - Health checks

requirements.txt (✅ Atualizado)
  - FastAPI 0.104.1
  - python-jose (JWT)
  - passlib + bcrypt
  - psycopg (PostgreSQL)
  - email-validator
  - Todas as dependências para IA

.env.example (✅ Atualizado)
  - DATABASE_URL (Neon)
  - SECRET_KEY (JWT)
  - PORT, ENV, MODEL_PATH
```

---

## 🚀 INSTALAÇÃO LOCAL (10 MIN)

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

**Nota:** TensorFlow é opcional se for só testar autenticação
```bash
# Sem TensorFlow (teste rápido)
pip install fastapi uvicorn python-jose passlib email-validator psycopg python-dotenv

# Com TensorFlow (completo)
pip install -r requirements.txt  # ~500 MB, 5-10 min
```

### 2. Configurar Banco de Dados

Obtenha uma conexão do Neon:
```bash
# Neon Cloud (gratuito): https://console.neon.tech
# Copie a connection string

# .env
DATABASE_URL=postgresql://user:pass@ep-xxxx.neon.tech/neondb?sslmode=require
SECRET_KEY=sua-chave-secreta-aqui
```

### 3. Criar Tabelas
```bash
python -c "from database_auth import criar_tabelas; criar_tabelas()"
# Output: ✅ Tabelas criadas/verificadas com sucesso!
```

### 4. Iniciar Servidor
```bash
# Desenvolvimento
uvicorn main_auth:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn main_auth:app --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000**

---

## 📚 ENDPOINTS DA API

### Autenticação (Sem proteção)

#### **POST /auth/register**
Registra novo usuário

**Request:**
```json
{
  "nome": "João Silva",
  "email": "joao@example.com",
  "senha": "MinhaSenh@1234"
}
```

**Response (201):**
```json
{
  "status": "sucesso",
  "mensagem": "Usuário criado com sucesso",
  "usuario": {
    "id": 1,
    "nome": "João Silva",
    "email": "joao@example.com"
  }
}
```

#### **POST /auth/login**
Faz login e retorna JWT

**Request:**
```json
{
  "email": "joao@example.com",
  "senha": "MinhaSenh@1234"
}
```

**Response (200):**
```json
{
  "status": "sucesso",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "nome": "João Silva",
    "email": "joao@example.com",
    "plano": "free"
  }
}
```

---

### Chat (COM proteção JWT)

#### **POST /chat**
Envia pergunta para IA

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Request:**
```json
{
  "pergunta": "Quem é você?",
  "incluir_emocao": false
}
```

**Response (200):**
```json
{
  "status": "sucesso",
  "resposta": "Sou a ALICI™, assistente de IA avançada...",
  "usuario": "João Silva"
}
```

#### **POST /chat/image**
Análise de imagem com modelo CNN

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data
```

**Body:**
```
imagem: [arquivo PNG/JPG]
```

**Response (200):**
```json
{
  "status": "sucesso",
  "classe": "gato",
  "confianca": 94.5,
  "resposta": "Detectei um **gato** com **94.5%** de confiança!",
  "alternativas": [
    {"classe": "tigre", "confianca": 3.2}
  ]
}
```

---

### Histórico (COM proteção JWT)

#### **GET /history?limit=50**
Retorna histórico do usuário

**Response (200):**
```json
{
  "status": "sucesso",
  "total": 5,
  "historico": [
    {
      "id": 1,
      "pergunta": "Quem é você?",
      "resposta": "Sou a ALICI...",
      "criado_em": "2026-01-24T10:30:00"
    }
  ]
}
```

#### **DELETE /history**
Limpa o histórico

**Response (200):**
```json
{
  "status": "sucesso",
  "mensagem": "Histórico limpo"
}
```

---

### Health & Status

#### **GET /health**
Status da aplicação (sem autenticação)

```json
{
  "status": "ok",
  "ia_disponivel": true,
  "timestamp": "2026-01-24T10:30:00"
}
```

#### **GET /api/status**
Status com informações do usuário (COM autenticação)

```json
{
  "usuario": "João Silva",
  "plano": "free",
  "ia_disponivel": true,
  "timestamp": "2026-01-24T10:30:00"
}
```

---

## 🧪 TESTES COM CURL

### 1. Registrar usuário
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João",
    "email": "joao@test.com",
    "senha": "Senha123!"
  }'
```

### 2. Fazer login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@test.com",
    "senha": "Senha123!"
  }'
```

**Copie o `access_token` retornado**

### 3. Usar token para chat
```bash
TOKEN="seu_token_aqui"

curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pergunta": "Olá!"
  }'
```

### 4. Enviar imagem
```bash
TOKEN="seu_token_aqui"

curl -X POST http://localhost:8000/chat/image \
  -H "Authorization: Bearer $TOKEN" \
  -F "imagem=@animais_preditos/predicao_1.png"
```

---

## 🔐 SEGURANÇA

### Senha
```python
# Entrada: "Minha123!"
# Bcrypt (one-way hashing):
# $2b$12$R9h/cIPz0gi.URNNGS3H2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUe
```

### Token JWT
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxIiwiZW1haWwiOiJqb2FvQHRlc3QuY29tIiwiaWF0IjoxNjc0MjQyMDAwLCJleHAiOjE2NzQzMjgwMDB9.
abc123def456...
```

**Payload decodificado:**
```json
{
  "sub": "1",         // user_id
  "email": "joao@test.com",
  "iat": 1674242000,  // issued at
  "exp": 1674328000   // expiration (24h depois)
}
```

---

## 📊 BANCO DE DADOS (Schema)

### Tabela `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    plano TEXT DEFAULT 'free',  -- 'free' ou 'pro'
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Tabela `history`
```sql
CREATE TABLE history (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_history_user_id ON history(user_id);
```

---

## 🌐 DEPLOY NO RENDER

### 1. Preparar Repositório
```bash
# Adicionar ao git
git add main_auth.py auth.py database_auth.py templates/ static/ requirements.txt .env.example
git commit -m "🔐 Sistema de autenticação JWT com FastAPI"
git push origin main
```

### 2. Criar Procfile
```procfile
web: uvicorn main_auth:app --host 0.0.0.0 --port $PORT
```

### 3. No Dashboard Render
1. Novo "Web Service"
2. Conectar repositório GitHub
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main_auth:app --host 0.0.0.0 --port $PORT`
5. Variáveis de ambiente:
   ```
   DATABASE_URL=postgresql://...  (Neon)
   SECRET_KEY=sua-chave-secreta
   PORT=10000
   ```

### 4. Acessar
```
https://seu-app.onrender.com
```

---

## 🛠️ TROUBLESHOOTING

### Erro: "Access denied for user"
**Causa:** DATABASE_URL incorreta

**Solução:**
```bash
# Verificar formato
# postgresql://user:password@host/db?sslmode=require

# No .env, sem aspas!
DATABASE_URL=postgresql://user:pass@ep-xxxx.neon.tech/neondb?sslmode=require
```

### Erro: "Email already exists"
```bash
# Usuário já registrado, tente outro email
```

### Erro 401: "Token inválido"
**Causa:** Token expirou (24h) ou incorreto

**Solução:**
```bash
# Fazer login novamente para obter novo token
```

### Erro: "Tabelas não encontradas"
**Solução:**
```bash
python -c "from database_auth import criar_tabelas; criar_tabelas()"
```

---

## 📈 ROADMAP PÓS-DEPLOY

1. **Refresh Tokens** - Token de 24h + refresh token de 7 dias
2. **2FA** - Autenticação de dois fatores
3. **OAuth** - Login com Google/GitHub
4. **Rate Limiting** - Limitar requisições por plano
5. **Admin Dashboard** - Gerenciar usuários
6. **Billing** - Stripe integration para Pro
7. **API Keys** - Para integração com terceiros

---

## 📞 ESTRUTURA COMPLETA (Resumo)

```
app/
├── main_auth.py          (FastAPI app + endpoints)
├── auth.py               (JWT + bcrypt)
├── database_auth.py      (PostgreSQL operations)
├── requirements.txt      (Dependências)
├── .env.example          (Configuração template)
│
├── templates/
│   ├── login.html        (Tela de login)
│   └── chat.html         (Tela de chat protegida)
│
├── static/
│   ├── login.css         (Estilos)
│   ├── login.js          (Lógica frontend)
│   ├── chat.css          (Estilos chat)
│   └── chat.js           (Cliente chat)
│
└── Procfile              (Instrução de deploy)
```

---

## ✅ Checklist de Implementação

- [x] Frontend login + registro (HTML/CSS/JS)
- [x] Backend FastAPI com endpoints
- [x] Autenticação JWT + tokens
- [x] Criptografia bcrypt
- [x] PostgreSQL schema + queries
- [x] Histórico por usuário
- [x] Proteção de rotas com JWT
- [x] Chat endpoint protegido
- [x] Análise de imagem protegida
- [x] Health checks
- [x] CORS configurado
- [x] Documentação completa
- [x] .env.example
- [x] requirements.txt atualizado
- [ ] Deploy no Render
- [ ] Testes em produção
- [ ] Integração com avatar

---

**Status:** 🎉 PRONTO PARA DEPLOY

Próximos passos:
1. Configurar Neon (database)
2. Criar .env com DATABASE_URL + SECRET_KEY
3. Executar: `python -c "from database_auth import criar_tabelas; criar_tabelas()"`
4. Testar localmente: `uvicorn main_auth:app --reload`
5. Deploy no Render
