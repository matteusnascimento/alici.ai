#!/usr/bin/env python3
"""
gerar_dataset.py - Gerador de Dataset para Treinamento
Expande o dataset base para treinar modelos de ML
"""

import json
import os
from datetime import datetime

print("=" * 70)
print("📊 GERADOR DE DATASET EXPANDIDO")
print("=" * 70)

# Dataset base (pode ser expandido conforme necessário)
dataset_base = {
    "metadata": {
        "total_pares": 100,
        "criador": "Mateus Nascimento dos Santos",
        "projeto": "ALICI™",
        "data": datetime.now().strftime("%Y-%m-%d"),
        "versao": "2.0",
        "descricao": "Dataset expandido para treinamento de modelos de IA"
    },
    "perguntas": [
        "quem é você",
        "qual seu nome",
        "qual é o seu nome",
        "como você se chama",
        "qual seu verdadeiro nome",
        "como devo chamar você",
        "você tem nome",
        "qual é a sua identidade",
        "quem é a alici",
        "o que é a alici",
        "alici é um robô",
        "você é humano",
        "você é inteligência artificial",
        "você é uma IA",
        "é verdade que você é IA",
        "você é programada",
        "quem programou você",
        "quem te criou",
        "quem é seu criador",
        "quem desenvolveu você",
    ],
    "respostas": [
        "Sou ALICI, uma inteligência artificial criada por Mateus Nascimento dos Santos.",
        "Meu nome é ALICI, e fui desenvolvida para ajudar e aprender continuamente.",
        "Sou ALICI, uma IA com memória persistente e capacidade de aprendizado.",
        "Você pode me chamar de ALICI, sua assistente de inteligência artificial.",
        "ALICI é meu nome, derivado de 'Artificial Learning and Interactive Computational Intelligence'.",
    ],
    "pares_qa": []
}

# Gerar pares Q&A
print("\n📝 Gerando pares de perguntas e respostas...")

pares = []
for i, pergunta in enumerate(dataset_base["perguntas"]):
    # Selecionar resposta (round-robin para variedade)
    resposta = dataset_base["respostas"][i % len(dataset_base["respostas"])]
    
    par = {
        "id": i + 1,
        "pergunta": pergunta,
        "resposta": resposta,
        "categoria": "identidade",
        "confianca": 1.0
    }
    pares.append(par)

dataset_base["pares_qa"] = pares
dataset_base["metadata"]["total_pares"] = len(pares)

# Adicionar categorias expandidas
categorias = {
    "saudacoes": [
        {"pergunta": "olá", "resposta": "Olá! Como posso ajudar você hoje?"},
        {"pergunta": "oi", "resposta": "Oi! Estou aqui para ajudar!"},
        {"pergunta": "bom dia", "resposta": "Bom dia! Como posso ser útil?"},
        {"pergunta": "boa tarde", "resposta": "Boa tarde! Em que posso ajudar?"},
        {"pergunta": "boa noite", "resposta": "Boa noite! Estou aqui para você!"},
    ],
    "capacidades": [
        {
            "pergunta": "o que você sabe fazer",
            "resposta": "Posso conversar, responder perguntas, aprender com você e buscar informações na web quando necessário."
        },
        {
            "pergunta": "quais são suas capacidades",
            "resposta": "Tenho memória persistente, posso aprender continuamente, buscar informações na internet e conversar naturalmente."
        },
        {
            "pergunta": "você pode me ajudar",
            "resposta": "Sim, posso ajudar com perguntas, conversas e buscas de informação. O que você precisa?"
        },
    ],
    "estado": [
        {"pergunta": "como você está", "resposta": "Estou bem e pronta para ajudar você!"},
        {"pergunta": "tudo bem", "resposta": "Sim, tudo bem! E com você?"},
        {"pergunta": "você está funcionando", "resposta": "Sim, estou funcionando perfeitamente!"},
    ]
}

# Adicionar categorias ao dataset
for categoria, items in categorias.items():
    for item in items:
        par = {
            "id": len(pares) + 1,
            "pergunta": item["pergunta"],
            "resposta": item["resposta"],
            "categoria": categoria,
            "confianca": 1.0
        }
        pares.append(par)

# Atualizar contagem
dataset_base["pares_qa"] = pares
dataset_base["metadata"]["total_pares"] = len(pares)

print(f"   ✅ {len(pares)} pares gerados")

# Salvar dataset
output_file = "dataset_expandido.json"
print(f"\n💾 Salvando dataset em: {output_file}")

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset_base, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Dataset salvo com sucesso")
    
    # Estatísticas
    file_size = os.path.getsize(output_file)
    print(f"\n📊 Estatísticas:")
    print(f"   • Total de pares: {len(pares)}")
    print(f"   • Tamanho do arquivo: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"   • Categorias: {len(categorias) + 1}")
    
    # Mostrar distribuição por categoria
    categorias_count = {}
    for par in pares:
        cat = par.get("categoria", "outros")
        categorias_count[cat] = categorias_count.get(cat, 0) + 1
    
    print(f"\n📋 Distribuição por categoria:")
    for cat, count in sorted(categorias_count.items()):
        print(f"   • {cat}: {count} pares")
    
    print("\n" + "=" * 70)
    print("✅ DATASET GERADO COM SUCESSO")
    print("=" * 70)
    
    print("\n🚀 Próximos passos:")
    print("   1. Upload dataset_expandido.json para Google Colab")
    print("   2. Execute colab_finetuning.py no Colab (GPU grátis)")
    print("   3. Baixe o modelo treinado (.h5)")
    print("   4. Coloque na pasta model/")
    
    print("\n💡 O dataset já existe e está pronto!")
    print("   Você pode editá-lo manualmente para adicionar mais pares.")
    
except Exception as e:
    print(f"   ❌ Erro ao salvar: {e}")
    exit(1)

print("\n" + "=" * 70)
