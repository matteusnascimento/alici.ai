#!/bin/bash
# Script para commit e push das alterações

echo "🔄 Adicionando arquivos ao Git..."
git add database.py
git add .gitignore
git add .env.example
git add requirements.txt
git add TROUBLESHOOTING.md
git add test_db.py
git add CHANGELOG_SQLITE.md
git add NEON_SETUP.md
git add OPTIONAL_ML.md
git add README.md

echo "📝 Criando commit..."
git commit -m "feat: Suporte a SQLite + Neon PostgreSQL + Hugging Face

🎯 Arquitetura completa:
- Neon PostgreSQL: Storage (memória, usuários, histórico)
- Hugging Face: ML/NLP (transformers, modelos)
- SQLite: Alternativa local para desenvolvimento

✨ Novidades:
- Suporte dual: SQLite (dev) e PostgreSQL (prod)
- Neon como banco principal recomendado
- Hugging Face mantido para NLP
- Detecção automática de tipo de banco pela URL
- Banco de dados opcional (app inicia sem DB)

📝 Arquivos modificados:
- database.py: Compatibilidade SQLite + PostgreSQL
- requirements.txt: Todas as dependências necessárias
- .env.example: Configuração para Neon
- .gitignore: Ignorar *.db e .env
- README.md: Documentação atualizada

➕ Arquivos novos:
- NEON_SETUP.md: Guia completo de configuração Neon
- OPTIONAL_ML.md: Arquitetura Neon (storage) + HF (ML)
- TROUBLESHOOTING.md: Guia de solução de problemas
- test_db.py: Script de teste do banco
- CHANGELOG_SQLITE.md: Documentação das mudanças

🔧 Como usar:
1. Instale: pip install -r requirements.txt
2. Configure Neon: https://neon.tech
3. Edite .env com DATABASE_URL
4. Crie tabelas: python init_db.py
5. Execute: python main.py

✅ Testado e funcionando!"

echo "⬆️  Enviando para GitHub..."
git push origin main

echo "✅ Pronto! Alterações enviadas para o GitHub"
