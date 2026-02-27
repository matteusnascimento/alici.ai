# ALICI™ API

API FastAPI da ALICI com autenticação JWT, chat com memória, histórico e endpoints multimodais.

## Principais ajustes aplicados

- Resolução de conflitos e padronização de backend para produção.
- Token padronizado no frontend para uma única chave: `access_token`.
- Endpoint de refresh token: `POST /auth/refresh`.
- Refresh token com rotação e revogação persistida em banco (`refresh_tokens`).
- Validação de tipo JWT (`type=access` e `type=refresh`).
- Tratamento global de exceções sem vazamento de erro interno.
- Correlação por requisição com header `X-Request-ID`.
- CORS configurável por ambiente via `CORS_ALLOWED_ORIGINS`.
- Rate limiting global e por usuário/plano no chat.
- Upload de imagem com limpeza garantida de arquivo temporário.
- Camadas iniciais para escalabilidade: repository + service + DTOs.

## Estrutura (API)

- `alici_api/app.py`: fábrica da aplicação, middleware e handlers globais.
- `alici_api/routes/`: rotas (`auth`, `chat`, `history`, `health`, `media`, `billing`, `pages`).
- `alici_api/services/`: serviços de IA/mídia/autenticação.
- `alici_api/repositories/`: acesso a dados (usuário, histórico e refresh tokens).
- `alici_api/schemas.py`: DTOs (requests).

## Variáveis de ambiente

### Segurança / JWT

- `SECRET_KEY` (obrigatória em produção)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: `60`)
- `REFRESH_TOKEN_EXPIRE_MINUTES` (default: `10080`)

### CORS

- `ENV` (`development` | `production`)
- `CORS_ALLOWED_ORIGINS` (lista separada por vírgula em produção)

Exemplo:

`CORS_ALLOWED_ORIGINS=https://app.seudominio.com,https://admin.seudominio.com`

### Rate Limit

- `RATE_LIMIT_ENABLED` (`true`/`false`, default `true`)
- `RATE_LIMIT_WINDOW_SECONDS` (default `60`)
- `RATE_LIMIT_MAX_REQUESTS` (default `60`)

### HuggingFace Hub (modelo textual)

O modelo textual da ALICI é carregado do HuggingFace Space [Matteusnascimento/alici.ai](https://huggingface.co/spaces/Matteusnascimento/alici.ai).

- `ALICI_HF_REPO_ID` (default: `Matteusnascimento/alici.ai`)
- `ALICI_HF_REPO_TYPE` (default: `space`)
- `ALICI_HF_SUBFOLDER` (opcional, subfolder dentro do Space)
- `HUGGINGFACE_TOKEN` — token de acesso gerado em <https://huggingface.co/settings/tokens> (necessário para Spaces privados ou com rate-limit)
- `ALICI_HF_CACHE_DIR` (default: `/tmp/alici_hf_cache`)

> ⚠️ **Nunca armazene o token HuggingFace no código-fonte.** Use variáveis de ambiente ou um gerenciador de segredos.

Consulte `.env.example` para um modelo completo de configuração.

## Rotas essenciais

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /api/status` (autenticado)
- `POST /chat` (autenticado)
- `POST /chat/image` (autenticado)
- `GET /history` (autenticado)
- `DELETE /history` (autenticado)
- `GET /health`

## Execução local

```bash
pip install -r requirements.txt
uvicorn alici_api.app:app --reload
```

## Deploy (Render)

`Procfile`:

`web: uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT`
