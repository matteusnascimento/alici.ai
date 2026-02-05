#!/bin/bash
# Script para salvar alterações no GitHub

echo "📦 Preparando commit..."

git add -A

git commit -m "feat: Database Neon + AI Hugging Face

Arquitetura completa ALICI:
- 🗄️ Neon PostgreSQL: Armazenamento persistente (memória, usuários, histórico)
- 🤖 Hugging Face: Modelos de IA (transformers, datasets, tokenizers)
- 🧠 TensorFlow + PyTorch: Machine Learning
- 🔍 Web Search: DuckDuckGo
- 📝 260+ Regras locais

Novos arquivos:
- ARCHITECTURE.md: Explica como Neon + Hugging Face trabalham juntos
- NEON_SETUP.md: Setup do banco Neon
- test_db.py: Teste de conexão
- TROUBLESHOOTING.md: Solução de problemas

Tecnologias:
- Database: Neon PostgreSQL (serverless)
- AI/NLP: Hugging Face (transformers)
- Backend: FastAPI + Uvicorn
- Auth: JWT + bcrypt"

echo "⬆️ Enviando para GitHub..."
git push origin main

echo "✅ Concluído!"
