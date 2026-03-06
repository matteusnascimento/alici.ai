# ALICI™ Platform - Enterprise AI Infrastructure

> **O Futuro da Infraestrutura de IA** - Mecanismo de IA Multimodal com Memória Neural Persistente

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🔥 O que é a ALICI?

A **plataforma enterprise** de IA multimodal que combina:

- 🤖 **Chat Inteligente** com memória persistente
- 🎨 **Geração de Imagens** via DALL-E/OpenAI
- 🔊 **Síntese de Voz** com qualidade premium
- 📹 **Geração de Vídeos** (breve)
- 📊 **Analytics Avançado** com Mixpanel
- 💳 **Sistema de Cobrança** integrado com Stripe
- 🔑 **API Keys** para desenvolvedores
- 🏢 **Multi-Tenant** com organizações isoladas
- 🚀 **Deploy Pronto** para produção

## ✨ Funcionalidades Implementadas

### 🎯 Landing Page Premium
- Design inspirado no OpenAI com tema escuro
- Partículas animadas interativas
- Gradientes animados e efeitos de glow
- Totalmente responsivo

### 🔐 Autenticação Completa
- JWT com refresh token rotation
- Rate limiting por usuário/plano
- Middleware de segurança avançado
- Suporte a múltiplos provedores

### 💬 Chat com Memória
- Histórico persistente
- Rate limiting inteligente (20-300 req/min)
- Suporte multimodal (texto + imagem)
- Emoções contextuais

### 🎨 Geração Multimídia
- Imagens via OpenAI DALL-E
- Áudio via TTS
- Vídeos (em desenvolvimento)
- Upload e análise de arquivos

### 📊 Analytics & Monitoramento
- Integração com Mixpanel
- Métricas de uso em tempo real
- Funnels de conversão
- Logs estruturados

### 💰 Sistema de Cobrança
- Integração completa com Stripe
- Webhooks para eventos de cobrança
- Planos flexíveis (Free/Pro/Ultra/Enterprise)
- Trial automático

### 🚀 Deploy & Infraestrutura
- Pronto para Render/Heroku
- PostgreSQL + Redis (opcional)
- Docker support
- CDN para assets estáticos

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** - Framework web assíncrono
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e sessões (opcional)
- **TensorFlow/PyTorch** - Modelos de IA

### Frontend
- **Vanilla JS** - Sem frameworks pesados
- **CSS3** - Animações e efeitos modernos
- **Lucide Icons** - Ícones vetoriais
- **Chart.js** - Gráficos interativos

### IA & ML
- **OpenAI GPT-4** - Chat e geração
- **Hugging Face** - Modelos customizados
- **Qdrant** - Vector database
- **LoRA** - Fine-tuning eficiente

### Cloud & DevOps
- **Stripe** - Pagamentos
- **AWS S3/R2** - Armazenamento
- **Render** - Deploy
- **Mixpanel** - Analytics

## 🚀 Quick Start

### Opção 1: Setup Automático

```bash
./setup.sh
```

### Opção 2: Manual

```bash
git clone https://github.com/matteusnascimento/alici.ai.git
cd alici.ai
pip install -r requirements.txt
cp .env.example .env
# Edite o .env com suas chaves
python main.py
```

### Opção 3: Docker

```bash
# Desenvolvimento com PostgreSQL + Redis
docker-compose up

# Produção
docker build -t alici .
docker run -p 8000:8000 alici
```

Acesse: http://localhost:8000

## 📋 Variáveis de Ambiente

### Essenciais
```env
ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-jwt-key
```

### Opcionais (IA & Pagamentos)
```env
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_test_...
MIXPANEL_TOKEN=...
HUGGINGFACE_API_KEY=hf_...
```

## 📊 API Endpoints

### Autenticação
- `POST /auth/login` - Login
- `POST /auth/register` - Registro
- `POST /auth/refresh` - Refresh token

### Chat
- `POST /chat/message` - Enviar mensagem
- `GET /chat/history` - Histórico

### Multimídia
- `POST /media/generate-image` - Gerar imagem
- `POST /media/generate-audio` - Gerar áudio
- `POST /media/analyze-image` - Analisar imagem

### Cobrança
- `GET /billing/plans` - Listar planos
- `POST /billing/create-checkout` - Criar checkout Stripe

## 🎨 Personalização

### Tema
O design usa CSS custom properties para fácil personalização:

```css
:root {
  --primary: #6366f1;
  --secondary: #8b5cf6;
  --dark: #0f172a;
}
```

### Landing Page
- Partículas interativas no `landing.js`
- Gradientes animados
- Efeitos de glassmorphism

## 📈 Roadmap

- [ ] Vídeo generation completo
- [ ] Multi-tenant architecture
- [ ] API rate limiting avançado
- [ ] Dashboard admin
- [ ] Integração WhatsApp/Slack
- [ ] Modelos customizados por usuário

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Contato

**Matheus Nascimento**
- Email: contato@alici.ai
- LinkedIn: [linkedin.com/in/matteusnascimento](https://linkedin.com/in/matteusnascimento)
- Twitter: [@matteusnasc](https://twitter.com/matteusnasc)

---

**ALICI™** - Construindo o futuro da IA, uma API por vez. 🚀

O modelo textual da ALICI é carregado do HuggingFace Space <a href="https://huggingface.co/spaces/Matteusnascimento/alici.ai">Matteusnascimento/alici.ai</a>.

- `ALICI_HF_REPO_ID` (default: `Matteusnascimento/alici.ai`)
- `ALICI_HF_REPO_TYPE` (default: `space`)
- `ALICI_HF_SUBFOLDER` (opcional, subfolder dentro do Space)
- `HUGGINGFACE_TOKEN` — token de acesso gerado em <a href="https://huggingface.co/settings/tokens">https://huggingface.co/settings/tokens</a> (necessário para Spaces privados ou com rate-limit)
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
