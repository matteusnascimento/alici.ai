# Alici 🤖

Alici é uma inteligência artificial com memória persistente usando PostgreSQL (Neon).

## 🚀 Funcionalidades

- **Memória Persistente**: Aprende com cada interação e guarda conhecimento no banco de dados
- **Busca na Web**: Quando não sabe algo, busca informações atualizadas na internet
- **Interface Web Moderna**: Chat interativo com design futurístico
- **API RESTful**: Endpoints para integração com outros sistemas
- **Fácil Deploy**: Configurado para publicação no Render

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Flask**: Framework web leve e poderoso
- **PostgreSQL (Neon)**: Banco de dados para memória persistente
- **psycopg2**: Conector PostgreSQL para Python
- **Gunicorn**: Servidor WSGI para produção
- **HTML/CSS/JS**: Interface web moderna e responsiva

## 📁 Estrutura do Projeto

```
alici/
├── main.py          # API principal (Flask)
├── engine.py        # Cérebro da Alici
├── resposta.py      # Inteligência base (fallback)
├── database.py      # Conexão Neon + Memória da IA
├── web_search.py    # Busca externa (quando não souber)
├── requirements.txt # Dependências Python
├── Procfile         # Configuração para Render
├── .env.example     # Exemplo de variáveis de ambiente
└── README.md        # Este arquivo
```

## 🚀 Como Rodar Localmente

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Configurar variáveis de ambiente**:
```bash
# Copie o exemplo e preencha com suas credenciais
cp .env.example .env
# Edite o arquivo .env com sua DATABASE_URL do Neon
```

3. **Rodar a aplicação**:
```bash
python main.py
```

4. **Acessar**:
- Interface Web: `http://localhost:5000`
- API Status: `http://localhost:5000/status`
- API Chat: `http://localhost:5000/chat`

## 📡 Endpoints da API

### Status
```http
GET /
```
Retorna o status da aplicação.

### Chat
```http
POST /chat
Content-Type: application/json

{
  "mensagem": "Quem é você?"
}
```

## 🌐 Interface Web

A Alici vem com uma interface web moderna e responsiva que inclui:
- Chat interativo em tempo real
- Design futurístico com animações
- Layout adaptável para mobile e desktop
- Feedback visual durante o processamento

## 🚀 COMO COLOCAR NO AR (Render)

1. **Suba tudo no GitHub**
2. **Entre no Render**
3. **New → Web Service**
4. **Conecte o repositório**
5. **Build command**:
```bash
pip install -r requirements.txt
```

6. **Start command**:
```bash
gunicorn main:app
```

7. **Adicione variável de ambiente**:
```
DATABASE_URL = sua_url_neon
```

8. **Deploy 🎉**

## 🗄️ Configuração do Banco de Dados (Neon)

1. **Crie uma conta no Neon** (https://neon.tech)
2. **Crie um projeto e banco de dados**
3. **Obtenha a CONNECTION STRING**
4. **Adicione ao seu .env ou variáveis de ambiente do Render**

Exemplo de CONNECTION STRING:
```
postgresql://neondb_owner:SEU_TOKEN@ep-frosty-shape-a8fhb2m2-pooler.eastus2.azure.neon.tech/neondb?sslmode=require
```

## 🔧 Comandos Úteis

### Testar a API localmente:
```bash
# Testar status
curl http://localhost:5000/status

# Testar chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Quem é você?"}'
```

## 🔥 Próximos Upgrades (se quiser)

- 🔹 Integração com LLMs reais (OpenAI, Hugging Face)
- 🔹 Upload de imagem e áudio
- 🔹 Treinamento contínuo
- 🔹 Interface estilo WhatsApp
- 🔹 App Flutter (Android + iOS)
- 🔹 Sistema de plugins
- 🔹 Análise de sentimento avançada
- 🔹 Multi-idiomas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Contato

Projeto Alici - [@seu_usuario](https://github.com/seu_usuario/alici)

---

**Alici AI v2.0** - Inteligência Artificial com Memória | © 2026