# 🚀 ALICI™ - Guia de Deploy

## Status: ✅ PRONTO PARA PRODUÇÃO

Interface v4.0 com melhorias:
- ✨ Novos efeitos visuais (glow dinâmico, transições suaves)
- ⚡ Performance otimizada (100 partículas neurais, animações reduzidas)
- 🔧 Novas funcionalidades (copiar, limpar chat, histórico)
- 📱 Responsividade melhorada para mobile (3 breakpoints)
- 🎯 Pronto para Render.com, Vercel, Heroku

---

## 🏃 Execução Local

### Desenvolvimento
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python main.py

# Acesse: http://localhost:8000
```

### Teste de Produção Local
```bash
# Usar uvicorn diretamente
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🌐 Deploy em Render.com (Recomendado)

### 1. Preparar o Projeto
```bash
# Certifique-se que você tem:
# - Procfile ✓
# - runtime.txt ✓
# - requirements.txt ✓
# - .env configurado ✓
```

### 2. Configurar em Render.com

**A. Criar novo Web Service:**
- Conecte seu repositório GitHub
- Selecione Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**B. Variáveis de Ambiente:**
```
PORT=8000
ENV=production
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sua-url-neon-aqui (opcional)
```

**C. Deploy:**
- Clique em "Deploy"
- Aguarde 5-10 minutos
- Seu app estará em: https://seu-app.onrender.com

---

## 🔐 Segurança em Produção

### Checklist:
- [ ] Alterar `SECRET_KEY` em `.env`
- [ ] Configurar `ENV=production`
- [ ] Adicionar `DATABASE_URL` se usar banco de dados
- [ ] Ativar HTTPS (Render ativa automaticamente)
- [ ] Revisar CORS em `alici_api/app.py`

### Atualizar CORS se necessário:
```python
# Em alici_api/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-dominio.com"],  # Especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoramento

### Logs em Render:
- Dashboard → Seu App → Logs
- Monitore erros em tempo real

### Health Check:
```bash
curl https://seu-app.onrender.com/api/status
# Resposta esperada: {"status": "ALICI™ Interface Neural Futurística Online"}
```

---

## 🔄 Atualizar Após Deploy

### 1. Fazer mudanças localmente
```bash
git add .
git commit -m "Update interface"
git push origin main
```

### 2. Deploy automático
- Render.com redeploya automaticamente após push
- Aguarde 5 minutos para ver mudanças

---

## ⚙️ Troubleshooting

### Problema: "Module not found"
```bash
# Solução: Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Problema: Porta já em uso
```bash
# Encontrar processo usando porta 8000
netstat -ano | findstr :8000

# Matar processo (Windows)
taskkill /PID <PID> /F
```

### Problema: CORS error
```bash
# Verificar se CORS está configurado em alici_api/app.py
# allow_origins=["*"] libera para todos (apenas desenvolvimento)
```

### Problema: Lentidão nas animações
```bash
# Já otimizado para 100 partículas neurais
# Se ainda lento, reduzir em script JavaScript para 60 partículas
```

---

## 📦 Arquivos Importantes

| Arquivo | Propósito |
|---------|-----------|
| `main.py` | Entrypoint (Uvicorn) |
| `alici_api/app.py` | API FastAPI |
| `templates/quantum.html` | Interface v4.0 |
| `engine.py` | Lógica de respostas (6 camadas) |
| `requirements.txt` | Dependências Python |
| `.env` | Configuração (não commitar) |
| `Procfile` | Instruções para Render |

---

## 🎯 Próximos Passos

1. **Database Persistência** (opcional)
   - Configurar PostgreSQL no Neon.tech
   - Atualizar DATABASE_URL no .env

2. **Autenticação** (opcional)
   - Endpoints `/auth/login` e `/auth/register` já implementados
   - Ativar em `alici_api/app.py`

3. **Modelos TensorFlow** (opcional)
   - Carregar modelos de `model/` pasta
   - Engine.py tem suporte com fallback gracioso

---

## 📞 Suporte

**Sistema operacional:** Windows 10/11
**Python:** 3.9+
**Framework:** FastAPI 0.104.1
**Status:** ✅ Testado e Pronto para Produção

---

**ALICI™ v4.0 - Interface Neural Futurística**
**Última atualização:** 2026-02-02
