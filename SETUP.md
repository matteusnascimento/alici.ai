# 🤖 ALICI™ - Setup & Deployment

## 🚀 Início Rápido Local

### 1. Clonar e instalar dependências
```bash
git clone https://github.com/matteusnascimento/alici.ai.git
cd alici.ai
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configurar banco de dados
```bash
# Copiar exemplo
cp .env.example .env

# Editar .env com sua string de conexão Neon:
# DATABASE_URL=postgresql://user:password@host.neon.tech/alici?sslmode=require
```

### 3. Inicializar banco de dados
```bash
python init_db.py
```
Isso cria a tabela `memoria` no Neon.

### 4. Executar servidor local
```bash
python main.py
```
Acesse: **http://localhost:5000**

---

## 📦 Estrutura do Projeto

```
alici.ai/
├── main.py                 # 🎯 Flask app principal
├── engine.py               # 🧠 5-layer decision engine
├── database.py             # 🗄️  PostgreSQL/Neon integration
├── identidade.py           # 🎭 Personality constant
├── resposta.py             # 📝 Local Q&A rules (~80 patterns)
├── intencao.py             # 🔍 Intent detection (web search trigger)
├── web_search.py           # 🌐 DuckDuckGo API wrapper
├── sistema_emocoes.py      # 💭 Emotion detection
├── init_db.py              # 🗄️  Database initialization script
├── requirements.txt        # 📚 Python dependencies
├── .env.example            # 🔑 Configuration template
└── Static/
    └── Imagens/Avatar/     # 🖼️  Avatar images
```

---

## 🎯 5-Layer Decision Pipeline

Cada pergunta passa por **5 camadas** sequenciais:

1. **Identity** (Imutável): "quem é você" → resposta fixa
2. **Memory** (Rápido): Busca exata em PostgreSQL
3. **Local Rules** (Padrões): Keywords em `resposta.py`
4. **Web Search** (Externo): DuckDuckGo se `precisa_pesquisa_web()`
5. **Fallback** (Gracioso): "Ainda não tenho essa informação..."

```python
resposta = gerar_resposta(pergunta)
# Sempre executa em ordem, short-circuits se encontrar resposta
```

---

## 🗄️ PostgreSQL Schema

```sql
CREATE TABLE memoria (
    id SERIAL PRIMARY KEY,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    confianca INT DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_memoria_pergunta ON memoria (pergunta);
```

**Confidence Scoring:**
- Primeira resposta = `confianca: 1`
- Cada repetição incrementa `confianca`
- Queries retornam resposta com maior confiança

---

## 🚀 Deploy no Render.com

### Pré-requisitos
- Conta em [Render.com](https://render.com)
- Banco de dados [Neon.tech](https://neon.tech) (Free tier: 3GB storage)
- Git e GitHub (repositório público)

### Steps

1. **Preparar banco Neon**
   - Criar projeto em neon.tech
   - Copiar connection string: `postgresql://user:password@host.neon.tech/dbname?sslmode=require`

2. **Clonar no Render**
   - Dashboard → New → Web Service
   - Repository: `https://github.com/matteusnascimento/alici.ai`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn main:app`

3. **Variáveis de Ambiente**
   - Add environment variable: `DATABASE_URL` = sua string Neon
   - Free tier: http://alici-ai.onrender.com

4. **Inicializar banco**
   ```bash
   # SSH no Render ou via local e execute:
   python init_db.py
   ```

---

## 🔧 Adicionando Novas Regras Q&A

Edit [resposta.py](resposta.py#L8):

```python
def responder_local(pergunta):
    pergunta = pergunta.lower().strip()
    
    # Exemplo: nova regra para weather
    if any(k in pergunta for k in ["clima", "tempo", "chuva"]):
        return "Desculpe, não tenho acesso ao previsão de tempo em tempo real."
    
    # ... outras regras
```

Test:
```bash
python -c "from resposta import responder_local; print(responder_local('qual é o clima?'))"
```

---

## 🐛 Debugging

### Ver logs do servidor
```bash
# Terminal 1: servidor rodando
python main.py

# Terminal 2: testar endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"olá"}'
```

### Verificar conexão ao banco
```bash
python -c "from database import conectar; print('✅ Conexão OK' if conectar() else '❌ Erro')"
```

### Testar engine completo
```bash
python teste_engine_completo.py
```

---

## ⚠️ Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| `relation "memoria" does not exist` | Tabela não criada | Execute `python init_db.py` |
| `no module named psycopg2` | Dependência faltando | `pip install psycopg2-binary` |
| `could not connect to server` | DATABASE_URL inválida | Verifique .env e permissões Neon |
| Respostas sempre fallback | Memory vazia, regras não match | Use `teste_engine_completo.py` para debug |

---

## 📝 Padrões & Convenções

### Case Normalization (CRÍTICO!)
```python
pergunta = pergunta.lower().strip()  # SEMPRE fazer primeiro
```
- DB armazena `pergunta` em lowercase
- Todos os padrões usam `.lower()`
- Não fazer isso = silent memory misses

### Responder Padrão em resposta.py
```python
if any(k in pergunta for k in ["padrão1", "padrão2"]):
    return "Resposta aqui..."
```
- Múltiplos keywords = robusto a typos
- Case-insensitive automático
- Fácil manutenção

### DB Cleanup (Previne Memory Leaks!)
```python
try:
    conn = conectar()
    cur = conn.cursor()
    # query
    conn.commit()
finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()
```
Missing = 504 errors depois de ~50 queries

---

## 📚 Recursos

- **Flask Docs**: https://flask.palletsprojects.com
- **Psycopg2 Docs**: https://www.psycopg.org
- **DuckDuckGo API**: https://duckduckgo.com/api
- **Neon Docs**: https://neon.tech/docs
- **Render Docs**: https://render.com/docs

---

## 📄 Licença

MIT License - veja LICENSE para detalhes

---

**Última atualização**: Jan 24, 2026
