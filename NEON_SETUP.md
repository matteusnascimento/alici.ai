# 🗄️ ALICI + Neon PostgreSQL

## 📌 Por que Neon?

O ALICI usa **Neon PostgreSQL** como banco de dados principal porque:

- ✅ **Serverless** - Escala automaticamente
- ✅ **Grátis até 3GB** - Perfeito para começar
- ✅ **PostgreSQL real** - 100% compatível
- ✅ **Branching** - Crie ambientes facilmente
- ✅ **Scale-to-zero** - Não paga quando não usa
- ✅ **Rápido** - Otimizado para cloud

## 🚀 Setup Rápido (5 minutos)

### 1. Criar conta no Neon

1. Acesse: https://neon.tech
2. Clique em **Sign Up** (grátis)
3. Faça login com GitHub/Google

### 2. Criar banco de dados

1. No dashboard, clique em **New Project**
2. Nome: `alici-database`
3. Região: Escolha a mais próxima (ex: `US East (Ohio)`)
4. PostgreSQL version: `16` (mais recente)
5. Clique em **Create Project**

### 3. Copiar Connection String

Após criar, você verá a **Connection String**:

```
postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 4. Configurar ALICI

Edite o arquivo `.env`:

```bash
DATABASE_URL=postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 5. Criar tabelas

```bash
python init_db.py
```

### 6. Testar conexão

```bash
python test_db.py
```

Deve mostrar:
```
============================================================
🧪 TESTE DE BANCO DE DADOS ALICI
============================================================

📊 Status:
   Banco habilitado: True
   Tipo: PostgreSQL ✅

🔧 Criando tabelas...
   ✅ Tabelas criadas
...
```

### 7. Executar ALICI

```bash
python main.py
```

Acesse: http://localhost:8000

---

## 📊 Estrutura do Banco

O ALICI cria automaticamente 3 tabelas:

### 1. **memoria** - Aprendizado da IA
```sql
CREATE TABLE memoria (
    id SERIAL PRIMARY KEY,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    confianca INT DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. **users** - Usuários do sistema
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    plano TEXT DEFAULT 'free',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. **history** - Histórico de conversas
```sql
CREATE TABLE history (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Comandos Úteis

### Ver dados no Neon

1. Acesse o dashboard: https://console.neon.tech
2. Selecione seu projeto
3. Clique em **SQL Editor**
4. Execute:

```sql
-- Ver aprendizado da IA
SELECT * FROM memoria ORDER BY confianca DESC LIMIT 10;

-- Ver usuários
SELECT id, nome, email, plano FROM users;

-- Ver últimas conversas
SELECT * FROM history ORDER BY criado_em DESC LIMIT 20;
```

### Resetar banco (CUIDADO!)

```sql
-- Apagar todos os dados
TRUNCATE memoria, users, history RESTART IDENTITY CASCADE;
```

### Backup manual

```bash
# Via pg_dump (precisa ter PostgreSQL instalado localmente)
pg_dump "postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require" > backup.sql

# Restaurar
psql "postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require" < backup.sql
```

---

## 💡 Dicas de Produção

### 1. Usar variáveis de ambiente

Nunca comite a `DATABASE_URL` no Git!

**Render.com:**
```bash
# No dashboard do Render, adicione:
DATABASE_URL=postgresql://...
```

**Vercel:**
```bash
vercel env add DATABASE_URL
```

**Docker:**
```dockerfile
ENV DATABASE_URL=postgresql://...
```

### 2. Connection Pooling

O ALICI já usa connection pooling via context managers:
```python
with get_db_connection() as conn:
    # Conexão automática
```

### 3. Monitoramento

No Neon Dashboard:
- **Monitoring** → Veja uso de CPU/RAM
- **Branches** → Crie ambientes de teste
- **Settings** → Configure limites

### 4. Scale Up

Plano grátis:
- ✅ 3 GB storage
- ✅ 100 horas compute/mês
- ✅ 1 projeto

Plano Pro ($19/mês):
- ✅ Ilimitado storage
- ✅ Compute ilimitado
- ✅ Projetos ilimitados
- ✅ Branching ilimitado

---

## 🐛 Troubleshooting

### Erro: "could not connect to server"

**Causa:** Firewall bloqueando conexão

**Solução:**
1. Verifique se `?sslmode=require` está na URL
2. Teste a conexão:
```bash
python -c "import psycopg2; psycopg2.connect('postgresql://...')"
```

### Erro: "password authentication failed"

**Causa:** Credenciais inválidas

**Solução:**
1. No Neon Dashboard → **Settings** → **Reset Password**
2. Copie a nova CONNECTION STRING
3. Atualize o `.env`

### Erro: "relation does not exist"

**Causa:** Tabelas não foram criadas

**Solução:**
```bash
python init_db.py
```

### Banco muito lento

**Causa:** Plano Free em scale-to-zero

**Solução:**
1. Primeira consulta é sempre mais lenta (cold start)
2. Depois fica rápido por ~5 minutos
3. Upgrade para Pro para evitar cold starts

---

## 📚 Recursos

- 📖 [Documentação Neon](https://neon.tech/docs/introduction)
- 🎓 [Quickstart](https://neon.tech/docs/get-started-with-neon/signing-up)
- 💬 [Discord](https://discord.gg/neon)
- 🐛 [GitHub Issues](https://github.com/neondatabase/neon/issues)

---

**Última atualização:** 2026-02-05  
**ALICI versão:** 2.0
