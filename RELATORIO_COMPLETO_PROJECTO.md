# Relatório Completo do Projecto — ALICI™ AI

## 1. Visão Geral

**Nome do projecto:** ALICI™ AI  
**Versão da API:** 2.2  
**Criador:** Mateus Nascimento dos Santos  
**Descrição:** ALICI é uma inteligência artificial foundation model desenvolvida do zero em português, com identidade proprietária, memória persistente, suporte multimodal e escalabilidade prevista até 70 bilhões de neurônios. O projecto expõe uma API REST construída com FastAPI, integra modelos de classificação de intenção textual (NLP), autenticação JWT com refresh token rotativo, histórico de conversas persistido em banco de dados e uma camada de billing com planos de subscrição.

---

## 2. Arquitectura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cliente (Browser / App)                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTPS
┌───────────────────────────────▼─────────────────────────────────┐
│                        FastAPI Application                        │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────┐ │
│  │ RequestID    │  │  RateLimit       │  │       CORS         │ │
│  │ Middleware   │  │  Middleware      │  │    Middleware      │ │
│  └──────────────┘  └──────────────────┘  └────────────────────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                         Routers                           │    │
│  │  /auth  /chat  /history  /billing  /health  /media       │    │
│  └───────────────────────────┬──────────────────────────────┘    │
│                              │                                    │
│  ┌────────────────┐  ┌───────▼─────────┐  ┌──────────────────┐  │
│  │  AuthService   │  │   AI Services   │  │  MediaService    │  │
│  │  (JWT, bcrypt) │  │  (NLP, Vision)  │  │  (Image/Audio)   │  │
│  └───────┬────────┘  └───────┬─────────┘  └──────────────────┘  │
│          │                   │                                    │
│  ┌───────▼────────┐  ┌───────▼──────────────────┐               │
│  │  Repositories  │  │  Text Model Loaders       │               │
│  │  (User/History │  │  (R2 primary / HF backup) │               │
│  │   /RefToken)   │  └───────────────────────────┘               │
│  └───────┬────────┘                                              │
└──────────┼────────────────────────────────────────────────────────┘
           │
┌──────────▼────────────────────┐     ┌──────────────────────────┐
│  PostgreSQL (Neon) / SQLite   │     │  Cloudflare R2 / HF Hub  │
│  (users, history, memoria,    │     │  (modelos ML artefactos) │
│   subscriptions, conversations│     └──────────────────────────┘
│   messages, refresh_tokens)   │
└───────────────────────────────┘
```

---

## 3. Pilha Tecnológica

| Camada | Tecnologia | Versão |
|---|---|---|
| Framework web | FastAPI | 0.104.1 |
| Servidor ASGI | Uvicorn (standard) | 0.24.0 |
| Validação de esquemas | Pydantic | 2.4.2 |
| Autenticação | python-jose (JWT) | 3.3.0 |
| Hashing de senhas | passlib (bcrypt) / bcrypt | 1.7.4 / 3.2.2 |
| Machine Learning | TensorFlow / Keras | 2.18.0 |
| Aritmética numérica | NumPy | 1.26.2 |
| Base de dados (cloud) | PostgreSQL via psycopg2-binary | 2.9.9 |
| Armazenamento de modelos | Cloudflare R2 (via boto3) | 1.34.162 |
| Modelos alternativos | HuggingFace Hub / Transformers | 0.17.3 / 4.35.0 |
| Inferência de linguagem | PyTorch | 2.1.0 |
| Busca web | requests | 2.31.0 |
| Configuração | python-dotenv | 1.0.0 |
| Deploy | Render (Gunicorn + Uvicorn) | 21.2.0 |
| Runtime | Python | 3.11 |

---

## 4. Estrutura de Directorias

```
alici.ai/
├── alici_api/                    # Pacote principal da API
│   ├── app.py                    # Fábrica da aplicação FastAPI
│   ├── config.py                 # Configuração via variáveis de ambiente
│   ├── dependencies.py           # Dependências partilhadas (get_current_user)
│   ├── responses.py              # Helpers de resposta padronizada (Codes)
│   ├── schemas.py                # DTOs Pydantic (Request bodies)
│   ├── middleware/
│   │   ├── rate_limit.py         # Rate limit global por IP/rota
│   │   └── request_id.py        # Correlação por X-Request-ID
│   ├── repositories/
│   │   ├── user_repository.py    # Acesso a dados de utilizadores
│   │   ├── history_repository.py # Acesso ao histórico de mensagens
│   │   └── refresh_token_repository.py # Gestão de refresh tokens
│   ├── routes/
│   │   ├── auth.py               # /auth (register, login, refresh, logout)
│   │   ├── chat.py               # /chat (texto e imagem)
│   │   ├── history.py            # /history (listar e apagar)
│   │   ├── media.py              # /generate-image, /generate-audio, /generate-video, /analyze-image
│   │   ├── billing.py            # /billing/plans, /billing/create-checkout
│   │   ├── health.py             # /health, /api/status
│   │   └── pages.py              # Páginas HTML (chat.html, index.html, login.html)
│   └── services/
│       ├── ai.py                 # Flags de disponibilidade e helpers de IA
│       ├── auth_service.py       # Lógica de negócio de autenticação
│       ├── media_service.py      # Geração e análise de media
│       ├── text_model_r2.py      # Loader do modelo NLP via Cloudflare R2
│       └── text_model_hf.py      # Loader alternativo via HuggingFace Hub
├── artifacts/
│   ├── alici_cpu_simple/         # Artefactos do modelo local
│   └── alici_cpu_simple_r2_cache/ # Cache local do R2
├── Static/
│   ├── css/style.css             # Estilos da interface web
│   ├── js/app.js                 # Lógica frontend
│   └── Imagens/Avatar/           # Imagens de avatar da ALICI
├── templates/
│   ├── chat.html                 # Interface de chat
│   ├── index.html                # Página principal
│   ├── login.html                # Página de login/registo
│   └── quantum.html              # Página experimental
├── auth.py                       # Utilitários JWT (create/verify tokens)
├── database.py                   # Conexão e DDL (PostgreSQL / SQLite)
├── engine.py                     # Motor de resposta textual
├── identidade.py                 # Identidade e personalidade da ALICI
├── intencao.py                   # Classificação de intenção
├── intents.json                  # Dataset de intenções
├── logger.py                     # Logger estruturado
├── resposta.py                   # Lógica de geração de resposta
├── sistema_emocoes.py            # Sistema de emoções da ALICI
├── web_search.py                 # Módulo de busca web
├── train_alici_cpu_simple.py     # Script de treino do modelo NLP
├── requirements.txt              # Dependências Python
├── Procfile                      # Configuração de deploy no Render
├── runtime.txt                   # Versão do runtime Python
├── .env.example                  # Modelo de variáveis de ambiente
├── FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md  # Ficha técnica do modelo ML
└── README.md                     # Documentação principal da API
```

---

## 5. Modelo de Dados (Base de Dados)

O sistema suporta PostgreSQL (produção via Neon) e SQLite (desenvolvimento local), configurado via `DATABASE_URL`.

### Tabelas

#### `users`
| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL / INTEGER PK | Identificador único |
| nome | TEXT NOT NULL | Nome do utilizador |
| email | TEXT UNIQUE NOT NULL | Email (único) |
| senha_hash | TEXT NOT NULL | Hash bcrypt da senha |
| plano | TEXT DEFAULT 'free' | Plano de subscrição |
| mensagens_hoje | INTEGER DEFAULT 0 | Contador diário de mensagens |
| criado_em | TIMESTAMP | Data de criação |

#### `historia` / `history`
| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL / INTEGER PK | Identificador único |
| user_id | INTEGER | Referência ao utilizador |
| pergunta | TEXT NOT NULL | Mensagem enviada |
| resposta | TEXT NOT NULL | Resposta da ALICI |
| criado_em | TIMESTAMP | Data da troca |

#### `memoria`
| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL / INTEGER PK | Identificador único |
| pergunta | TEXT NOT NULL | Padrão aprendido |
| resposta | TEXT NOT NULL | Resposta associada |
| confianca | INTEGER DEFAULT 1 | Nível de confiança |
| criado_em | TIMESTAMP | Data de criação |

#### `refresh_tokens`
| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL / INTEGER PK | Identificador único |
| user_id | INTEGER NOT NULL | Referência ao utilizador |
| jti | TEXT UNIQUE NOT NULL | JWT ID único do token |
| revoked | BOOLEAN DEFAULT FALSE | Estado de revogação |
| expires_at | TIMESTAMP NOT NULL | Data de expiração |
| criado_em | TIMESTAMP | Data de emissão |

#### `subscriptions`
| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL / INTEGER PK | Identificador único |
| user_id | INTEGER NOT NULL | Referência ao utilizador |
| stripe_id | TEXT | ID de checkout Stripe |
| status | TEXT DEFAULT 'inactive' | Estado da subscrição |
| plano | TEXT DEFAULT 'free' | Plano activo |
| renovacao | TIMESTAMP | Próxima renovação |
| criado_em | TIMESTAMP | Data de criação |

#### `conversations`
| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL / INTEGER PK | Identificador único |
| user_id | INTEGER NOT NULL | Referência ao utilizador |
| titulo | TEXT | Título da conversa |
| criado_em | TIMESTAMP | Data de criação |

#### `messages`
| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL / INTEGER PK | Identificador único |
| conversation_id | INTEGER | Referência à conversa |
| role | TEXT NOT NULL | Papel (user / assistant) |
| content | TEXT NOT NULL | Conteúdo da mensagem |
| criado_em | TIMESTAMP | Data da mensagem |

---

## 6. Autenticação e Autorização

O sistema implementa autenticação baseada em JWT (JSON Web Tokens) com dois tipos de token:

- **Access Token** — curta duração (padrão: 60 minutos), tipo `access`, para autenticar chamadas à API.
- **Refresh Token** — longa duração (padrão: 7 dias), tipo `refresh`, para renovar o access token sem nova autenticação. Implementa rotação e revogação persistida em base de dados (campo `jti` + flag `revoked`).

### Fluxo de autenticação

```
1. POST /auth/register  → cria utilizador com senha em bcrypt hash
2. POST /auth/login     → valida credenciais, emite access + refresh token
3. POST /auth/refresh   → valida refresh token (jti, revogação, expiração),
                          revoga o token antigo, emite novo par de tokens
4. POST /auth/logout    → revoga todos os refresh tokens do utilizador
```

### Validações de segurança implementadas
- Senha mínima de 8 caracteres e máximo de 72 bytes (limite bcrypt).
- Nome de utilizador com mínimo de 2 caracteres.
- Email único por utilizador.
- Verificação do campo `type` no payload JWT (`access` vs `refresh`).
- Sem vazamento de erros internos — mensagens de erro genéricas para o cliente.

---

## 7. Endpoints da API

Todos os endpoints autenticados exigem o header `Authorization: Bearer <access_token>`.

### Autenticação (`/auth`)

| Método | Rota | Autenticado | Descrição |
|---|---|---|---|
| POST | `/auth/register` | Não | Regista novo utilizador |
| POST | `/auth/login` | Não | Autentica e devolve tokens |
| POST | `/auth/refresh` | Não | Renova access token via refresh token |
| POST | `/auth/logout` | Sim | Revoga todos os refresh tokens |

### Chat (`/chat`)

| Método | Rota | Autenticado | Descrição |
|---|---|---|---|
| POST | `/chat` | Sim | Envia pergunta, recebe resposta da ALICI |
| POST | `/chat/image` | Sim | Envia imagem + prompt, recebe análise |

### Histórico (`/history`)

| Método | Rota | Autenticado | Descrição |
|---|---|---|---|
| GET | `/history` | Sim | Lista histórico do utilizador (limite: 50–200) |
| DELETE | `/history` | Sim | Apaga todo o histórico |

### Multimédia

| Método | Rota | Autenticado | Descrição |
|---|---|---|---|
| POST | `/generate-image` | Sim | Gera imagem a partir de prompt |
| POST | `/generate-audio` | Sim | Gera áudio a partir de texto |
| POST | `/generate-video` | Sim | Gera vídeo a partir de prompt |
| POST | `/analyze-image` | Sim | Analisa imagem enviada via upload |

### Billing (`/billing`)

| Método | Rota | Autenticado | Descrição |
|---|---|---|---|
| GET | `/billing/plans` | Sim | Lista planos disponíveis e plano actual |
| POST | `/billing/create-checkout` | Sim | Inicia checkout (Stripe-ready) |

### Saúde e Estado

| Método | Rota | Autenticado | Descrição |
|---|---|---|---|
| GET | `/health` | Não | Estado geral da aplicação e dos modelos |
| GET | `/api/status` | Sim | Estado da sessão autenticada |

### Páginas Web

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Página inicial (`index.html`) |
| GET | `/chat` | Interface de chat (`chat.html`) |
| GET | `/login` | Página de login/registo (`login.html`) |

---

## 8. Planos de Subscrição e Limites

| Plano | Preço (BRL/mês) | Mensagens/dia | Requisições/min (chat) |
|---|---|---|---|
| Free | R$ 0 | 20 | 20 |
| Pro | R$ 49 | 300 | 120 |
| Ultra | R$ 99 | 2.000 | 300 |
| Enterprise | Sob consulta | Ilimitado | Ilimitado |

O limite diário é verificado por contagem de mensagens na tabela `history`. O rate limit por minuto usa uma janela deslizante em memória (thread-safe via `threading.Lock`).

---

## 9. Rate Limiting

São aplicadas duas camadas de rate limiting:

1. **Rate limit global (middleware)** — por IP + rota, configurable via variáveis de ambiente. Exclui `/health` e `/`. Devolve HTTP 429 ao ultrapassar o limite.
2. **Rate limit por utilizador/plano no chat** — janela de 60 segundos, limite dependente do plano. Devolve HTTP 429 com detalhe do plano e limite.

---

## 10. Modelo de IA Textual (NLP)

O modelo de classificação de intenção é um modelo Keras sequencial treinado com o dataset `intents.json` (5 classes em português). Para detalhes completos, consulte [FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md](./FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md).

### Resumo

| Parâmetro | Valor |
|---|---|
| Tipo | Classificação de intenção (NLP) |
| Framework | TensorFlow / Keras |
| Arquitectura | Embedding → BiLSTM → Dropout → Dense → Softmax |
| Classes | `saudacao`, `despedida`, `criador`, `agradecimento`, `ajuda` |
| Amostras de treino | 22 (split 80/20) |
| Parâmetros treináveis | 1.413.125 |
| Val accuracy | 0.2000 ⚠️ equivale a acerto aleatório (5 classes → 1/5) |
| Confiança mínima | 0.55 (configurável via `ALICI_INTENT_MIN_CONFIDENCE`) |

### Carregamento do modelo

O modelo é carregado na inicialização da API com estratégia de fallback:

1. **Primário:** Cloudflare R2 (via `boto3`) — artefactos descarregados para cache local `/tmp/alici_cpu_simple_r2_cache`.
2. **Fallback:** HuggingFace Hub — Space `Matteusnascimento/alici.ai`.

---

## 11. Sistema de Emoções e Identidade

A ALICI implementa um sistema de emoções (`sistema_emocoes.py`) e um módulo de identidade (`identidade.py`) que definem a personalidade da IA:

- **Identidade:** A ALICI sabe quem a criou, qual a sua missão, arquitectura e diferenciais.
- **Emoções:** As respostas podem incluir um componente emocional activado pelo parâmetro `incluir_emocao: true` no pedido de chat.
- **Busca web:** O módulo `web_search.py` permite à ALICI pesquisar informação actualizada quando necessário.

---

## 12. Variáveis de Ambiente

Consulte `.env.example` para a lista completa. As mais relevantes:

### Segurança / JWT
| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | — | Chave secreta JWT (obrigatória em produção) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Duração do access token |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | `10080` | Duração do refresh token (7 dias) |

### Base de dados
| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | — | URL de conexão (postgresql:// ou sqlite:///) |

### CORS
| Variável | Padrão | Descrição |
|---|---|---|
| `ENV` | `development` | Ambiente (`development` ou `production`) |
| `CORS_ALLOWED_ORIGINS` | `*` (dev) | Origens permitidas, separadas por vírgula |

### Rate Limit
| Variável | Padrão | Descrição |
|---|---|---|
| `RATE_LIMIT_ENABLED` | `true` | Activa/desactiva rate limiting global |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Janela temporal |
| `RATE_LIMIT_MAX_REQUESTS` | `60` | Máximo de pedidos por janela |

### Modelo NLP — Cloudflare R2
| Variável | Padrão | Descrição |
|---|---|---|
| `ALICI_R2_ACCOUNT_ID` | — | ID da conta R2 |
| `ALICI_R2_ACCESS_KEY` | — | Chave de acesso R2 |
| `ALICI_R2_SECRET_KEY` | — | Chave secreta R2 |
| `ALICI_R2_BUCKET` | — | Nome do bucket |
| `ALICI_R2_MODEL_PREFIX` | — | Prefixo dos artefactos no bucket |
| `ALICI_MODEL_CACHE_DIR` | `/tmp/alici_cpu_simple_r2_cache` | Directório de cache local |
| `ALICI_INTENT_MIN_CONFIDENCE` | `0.55` | Confiança mínima para classificar intenção |

### Modelo NLP — HuggingFace (fallback)
| Variável | Padrão | Descrição |
|---|---|---|
| `ALICI_HF_REPO_ID` | `Matteusnascimento/alici.ai` | ID do repositório/Space HF |
| `ALICI_HF_REPO_TYPE` | `space` | Tipo de repositório HF |
| `HUGGINGFACE_TOKEN` | — | Token de acesso HuggingFace |
| `ALICI_HF_CACHE_DIR` | `/tmp/alici_hf_cache` | Directório de cache local |

### Billing
| Variável | Padrão | Descrição |
|---|---|---|
| `STRIPE_SECRET_KEY` | — | Chave secreta Stripe (activa checkout real) |

---

## 13. Deploy e Infraestrutura

### Render (produção)

O projecto está configurado para deploy no Render através do `Procfile`:

```
web: uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT
```

O ficheiro `.renderignore` exclui ficheiros desnecessários do deploy (ex.: `node_modules`, `.git`, ficheiros de cache).

### Execução local

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com as suas configurações

# 3. Iniciar o servidor de desenvolvimento
uvicorn alici_api.app:app --reload
```

---

## 14. Segurança

| Medida | Implementação |
|---|---|
| Hashing de senhas | bcrypt com passlib (salt automático) |
| Autenticação sem estado | JWT com verificação de tipo (`access`/`refresh`) |
| Revogação de tokens | JTI persistido em base de dados com flag `revoked` |
| Rate limiting | Middleware global + por utilizador/plano no chat |
| Correlação de pedidos | Header `X-Request-ID` gerado por pedido |
| Tratamento de erros | Sem exposição de stack traces ao cliente |
| CORS | Configurável por ambiente (`ENV=production` exige origens explícitas) |
| Credenciais | Exclusivamente via variáveis de ambiente (nunca em código-fonte) |
| Upload de ficheiros | Validação de `content_type`, limpeza garantida de ficheiros temporários |

---

## 15. Códigos de Resposta Padronizados

Todos os endpoints devolvem respostas JSON com a estrutura:

```json
{
  "status": "sucesso" | "erro",
  "code": "<CODIGO>",
  "message": "<mensagem opcional>",
  ...dados adicionais
}
```

### Códigos de sucesso

| Código | Significado |
|---|---|
| `OK-0000` | Sucesso genérico |
| `OK-HEALTH-200` | Health check OK |
| `OK-AUTH-201` | Registo concluído |
| `OK-AUTH-200` | Login / refresh OK |
| `OK-AUTH-204` | Logout OK |
| `OK-CHAT-200` | Resposta de chat devolvida |
| `OK-CHAT-IMG-200` | Resposta de chat com imagem devolvida |
| `OK-HIST-200` | Histórico listado |
| `OK-HIST-204` | Histórico apagado |
| `OK-MEDIA-IMG-200` | Imagem gerada |
| `OK-MEDIA-AUD-200` | Áudio gerado |
| `OK-MEDIA-VID-200` | Vídeo gerado |
| `OK-MEDIA-ANL-200` | Análise de imagem concluída |
| `OK-BILLING-PLANS-200` | Planos listados |
| `OK-BILLING-CHK-200` | Checkout criado |

### Códigos de erro

| Código | HTTP | Significado |
|---|---|---|
| `ERR-REQ-400` | 400 | Pedido inválido |
| `ERR-AUTH-401` | 401 | Não autenticado |
| `ERR-AUTH-403` | 403 | Acesso negado (ex.: limite diário) |
| `ERR-REQ-404` | 404 | Recurso não encontrado |
| `ERR-REQ-422` | 422 | Erro de validação de esquema |
| `ERR-RATE-429` | 429 | Rate limit excedido |
| `ERR-SVC-503` | 503 | Serviço de IA indisponível |
| `ERR-SYS-500` | 500 | Erro interno do servidor |

---

## 16. Limitações e Recomendações

| Limitação | Recomendação |
|---|---|
| Dataset de NLP muito pequeno (22 amostras, split 80/20 resulta em apenas 4–5 amostras de validação) | Expandir `intents.json` com mais padrões e classes |
| Val accuracy de 0.20 — igual ao acerto aleatório para 5 classes (1/5 = 0.20); **modelo não está pronto para produção neste estado** | Treinar novo ciclo com dataset maior (mínimo recomendado: 100+ amostras por classe); avaliar F1 por classe |
| Rate limiting em memória (não partilhado entre instâncias) | Migrar para Redis para ambientes multi-instância |
| Billing sem integração Stripe completa | Implementar webhook Stripe para activação automática de planos |
| Modelo de visão sem implementação activa (`VISAO_DISPONIVEL` pode ser False) | Integrar modelo de visão estável (ex.: CLIP, LLaVA) |
| Tabela `memoria` sem vínculo explícito a `user_id` | Associar aprendizados a utilizadores para personalização |

---

## 17. Roadmap

| Fase | Funcionalidade |
|---|---|
| v2.3 | Integração Stripe completa (webhook + activação de plano automática) |
| v2.4 | Redis para rate limiting distribuído e cache de sessão |
| v2.5 | Expansão do dataset NLP + avaliação por classe (F1, recall) |
| v3.0 | Modelo de linguagem proprietário (124M parâmetros base, escalável a 70B) |
| v3.x | Tokenizer proprietário ALICI (irreplicável) |
| v4.0 | Multimodalidade completa (visão, áudio, vídeo) em produção |

---

## 18. Referências

- [README.md](./README.md) — Documentação da API (rotas, variáveis, execução local)
- [FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md](./FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md) — Ficha técnica detalhada do modelo NLP
- [.env.example](./.env.example) — Modelo completo de configuração de variáveis de ambiente
- [HuggingFace Space — Matteusnascimento/alici.ai](https://huggingface.co/spaces/Matteusnascimento/alici.ai) — Space de alojamento alternativo do modelo
