# ALICI — Documentação Completa do Projeto

ALICI é uma API FastAPI com autenticação JWT, chat com memória, regras locais, fallback em modelo fundacional e camada multimodal (imagem, áudio, vídeo e análise de imagem).

## 1. Visão Geral

- Linguagem: Python
- Framework: FastAPI
- Auth: JWT + bcrypt
- Banco: PostgreSQL (Neon) ou SQLite
- Frontend: templates HTML + JS estático
- Entrypoint principal: `main.py`

Fluxo central de resposta textual:
1) identidade
2) memória persistente
3) regras locais
4) busca web
5) modelo fundacional
6) fallback

## 2. Estrutura Atual

```
alici.ai/
├── main.py
├── app.py
├── auth.py
├── database.py
├── engine.py
├── identidade.py
├── intencao.py
├── logger.py
├── resposta.py
├── sistema_emocoes.py
├── web_search.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── templates/
│   ├── login.html
│   ├── index.html
│   ├── chat.html
│   └── quantum.html
├── static/
├── Static/
├── generated/
│   ├── images/
│   ├── audios/
│   └── videos/
└── alici_api/
    ├── app.py
    ├── dependencies.py
    ├── schemas.py
    ├── routes/
    │   ├── auth.py
    │   ├── chat.py
    │   ├── history.py
    │   ├── health.py
    │   ├── pages.py
    │   └── media.py
    └── services/
        ├── ai.py
        └── media_service.py
```

## 3. Módulos Principais

### `main.py`
- Entrypoint para execução local e ASGI.
- Importa `app` de `alici_api.app`.

### `alici_api/app.py`
- Cria app FastAPI.
- Configura CORS.
- Monta static files (`/static`, `/Static`, `/generated`).
- Registra rotas (`auth`, `chat`, `media`, `history`, `pages`, `health`).
- Inicializa banco no startup (`criar_tabelas`).

### `engine.py`
- Cérebro de resposta textual em camadas.
- Integra memória (`database.py`), regras (`resposta.py`), web (`web_search.py`) e modelo fundacional.

### `database.py`
- Conexão com PostgreSQL/SQLite.
- CRUD de usuários, memória e histórico.
- Aprendizado com incremento de confiança.

### `auth.py`
- Hash e verificação de senha.
- Emissão e validação JWT.

### `alici_api/services/media_service.py`
- MVP multimodal:
  - `generate_image(prompt)` → SVG em `generated/images`
  - `generate_audio(text)` → WAV em `generated/audios`
  - `generate_video(prompt)` → job placeholder em `generated/videos`
  - `analyze_image_bytes(...)` → fallback de análise quando visão não disponível

## 4. Rotas da API

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`

### Chat
- `POST /chat`
- `POST /chat/image`

### Histórico
- `GET /history?limit=50`
- `DELETE /history`

### Health/Status
- `GET /health`
- `GET /api/status`

### Páginas
- `GET /`
- `GET /chat`
- `GET /dashboard`

### Multimodal
- `POST /generate-image`
- `POST /generate-audio`
- `POST /generate-video`
- `POST /analyze-image` (multipart/form-data)

## 5. Contratos de Requisição/Resposta

### `POST /generate-image`
Body:
```json
{ "prompt": "cidade cyberpunk neon" }
```
Resposta:
```json
{ "status": "sucesso", "url": "/generated/images/arquivo.svg", "usuario": "Nome" }
```

### `POST /generate-audio`
Body:
```json
{ "texto": "Olá, eu sou a Alici." }
```
Resposta:
```json
{ "status": "sucesso", "audio_url": "/generated/audios/arquivo.wav", "usuario": "Nome" }
```

### `POST /generate-video`
Body:
```json
{ "prompt": "voo por uma cidade futurista" }
```
Resposta:
```json
{ "status": "sucesso", "job_id": "video_xxx", "video_url": "/generated/videos/video_xxx.json", "message": "...", "usuario": "Nome" }
```

### `POST /analyze-image`
Form-data:
- campo `file`

Resposta (fallback):
```json
{ "status": "sucesso", "usuario": "Nome", "resultado": { "descricao": "...", "tipo": "image/jpeg" } }
```

## 6. Configuração de Ambiente

Variáveis recomendadas:

```env
ENV=development
PORT=8000
SECRET_KEY=sua_chave_forte
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
OPENAI_API_KEY=...

# Modelo textual no Cloudflare R2
ALICI_R2_ACCOUNT_ID=...
ALICI_R2_ACCESS_KEY=...
ALICI_R2_SECRET_KEY=...
ALICI_R2_BUCKET=alici-lake
ALICI_R2_MODEL_PREFIX=models/alici_cpu_simple
ALICI_MODEL_CACHE_DIR=/tmp/alici_cpu_simple_r2_cache
ALICI_R2_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
ALICI_INTENT_MIN_CONFIDENCE=0.55
```

Observações:
- Sem `DATABASE_URL`, o banco fica indisponível para operações persistentes.
- Em produção, `SECRET_KEY` deve ser obrigatoriamente segura.
- No startup da API, o modelo textual é baixado do R2 para cache local temporário e usado no `engine.py` antes da camada de busca web.
- O `.keras` não é carregado diretamente por stream do R2; ele é baixado para cache e então carregado pelo TensorFlow (comportamento esperado em cloud).

## 7. Execução Local

1. Instalar dependências
```bash
pip install -r requirements.txt
```

2. Rodar aplicação
```bash
python main.py
```

3. Acessar
- App: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

## 8. Deploy

### Render
- Procfile atual:
```txt
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Runtime
- Python definido em `runtime.txt`.

## 9. Segurança e Limites (Recomendado)

- Restringir CORS por domínio em produção.
- Limitar tamanho de upload em rotas de mídia.
- Aplicar rate limiting por usuário/token.
- Sanitizar prompts e logs sensíveis.

## 10. Limitações Conhecidas

- Geração de vídeo está em modo MVP assíncrono (job placeholder).
- Geração de imagem/áudio multimodal atual é baseline local (não modelo pesado de produção).
- Persistência de arquivos `generated/` em ambientes efêmeros pode ser perdida após restart.

## 11. Próximos Passos Técnicos

1. Integrar provider real de imagem/vídeo/TTS (OpenAI, Replicate, etc).
2. Mover `generated/` para storage persistente (S3/R2/GCS).
3. Implementar fila de jobs para vídeo (Redis + worker).
4. Adicionar observabilidade (métricas, tracing, logs estruturados).
5. Adicionar testes automatizados de rotas críticas.

## 12. Licença/Manutenção

Projeto mantido por equipe Alici. Ajustes de arquitetura devem priorizar:
- compatibilidade de contratos frontend/backend;
- estabilidade do fluxo de autenticação;
- separação clara entre `routes` e `services`.
