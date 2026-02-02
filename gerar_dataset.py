"""
gerar_dataset.py
📊 Gerador de dataset expandido para treinar ALICI
Cria pares de pergunta-resposta para fine-tuning
"""

import json
import os

def gerar_dataset_base():
    """
    Gera dataset base com perguntas e respostas comuns
    """
    dataset = []
    
    # Identidade
    identidade_qa = [
        {
            "pergunta": "Quem é você?",
            "resposta": "Sou ALICI, uma assistente de inteligência artificial criada por Mateus Nascimento dos Santos."
        },
        {
            "pergunta": "Qual é o seu nome?",
            "resposta": "Meu nome é ALICI, sou uma IA com memória persistente e aprendizado contínuo."
        },
        {
            "pergunta": "Quem te criou?",
            "resposta": "Fui criada por Mateus Nascimento dos Santos, um desenvolvedor brasileiro."
        },
        {
            "pergunta": "O que você faz?",
            "resposta": "Sou uma assistente de IA que pode responder perguntas, aprender com conversas e buscar informações na web."
        },
    ]
    
    # Saudações
    saudacoes_qa = [
        {
            "pergunta": "Oi",
            "resposta": "Olá! Como posso ajudar você hoje?"
        },
        {
            "pergunta": "Olá",
            "resposta": "Oi! É um prazer conversar com você. Em que posso ajudar?"
        },
        {
            "pergunta": "Bom dia",
            "resposta": "Bom dia! Espero que esteja tendo um ótimo dia. Como posso ajudar?"
        },
        {
            "pergunta": "Boa tarde",
            "resposta": "Boa tarde! Como posso ajudar você?"
        },
        {
            "pergunta": "Boa noite",
            "resposta": "Boa noite! Em que posso ajudar?"
        },
    ]
    
    # Bem-estar
    bem_estar_qa = [
        {
            "pergunta": "Como você está?",
            "resposta": "Estou bem e pronta para ajudar você! Como você está?"
        },
        {
            "pergunta": "Tudo bem?",
            "resposta": "Tudo ótimo por aqui! E com você?"
        },
        {
            "pergunta": "Como vai?",
            "resposta": "Vou muito bem, obrigada por perguntar! Como posso ajudar?"
        },
    ]
    
    # Capacidades
    capacidades_qa = [
        {
            "pergunta": "O que você sabe fazer?",
            "resposta": "Posso responder perguntas, aprender com conversas, buscar informações na web e manter memória de nossas interações."
        },
        {
            "pergunta": "Quais são suas funcionalidades?",
            "resposta": "Tenho memória persistente, aprendizado contínuo, busca na web e sistema de 5 camadas de decisão."
        },
        {
            "pergunta": "Você consegue aprender?",
            "resposta": "Sim! Aprendo com cada conversa e armazeno tudo em memória permanente."
        },
    ]
    
    # Tecnologia
    tecnologia_qa = [
        {
            "pergunta": "Você usa inteligência artificial?",
            "resposta": "Sim, sou construída com TensorFlow, PostgreSQL e um sistema inteligente de 5 camadas."
        },
        {
            "pergunta": "Qual linguagem você usa?",
            "resposta": "Sou programada em Python, usando FastAPI, TensorFlow e PostgreSQL."
        },
    ]
    
    # Conhecimento geral
    conhecimento_qa = [
        {
            "pergunta": "O que é Python?",
            "resposta": "Python é uma linguagem de programação de alto nível, versátil e muito popular para IA e desenvolvimento web."
        },
        {
            "pergunta": "O que é inteligência artificial?",
            "resposta": "Inteligência artificial é a capacidade de sistemas computacionais de realizar tarefas que normalmente requerem inteligência humana."
        },
        {
            "pergunta": "O que é machine learning?",
            "resposta": "Machine learning é um subcampo da IA onde sistemas aprendem e melhoram através de experiência sem serem explicitamente programados."
        },
    ]
    
    # Combinar todos os pares
    dataset.extend(identidade_qa)
    dataset.extend(saudacoes_qa)
    dataset.extend(bem_estar_qa)
    dataset.extend(capacidades_qa)
    dataset.extend(tecnologia_qa)
    dataset.extend(conhecimento_qa)
    
    return dataset

def adicionar_variacoes(dataset):
    """
    Adiciona variações de perguntas para aumentar dataset
    """
    variacoes = []
    
    for item in dataset:
        pergunta_original = item["pergunta"]
        resposta = item["resposta"]
        
        # Variações de capitalização e pontuação
        variacoes.append({
            "pergunta": pergunta_original.lower(),
            "resposta": resposta
        })
        
        variacoes.append({
            "pergunta": pergunta_original.upper(),
            "resposta": resposta
        })
        
        # Variação sem pontuação
        pergunta_sem_pontuacao = pergunta_original.rstrip("?!.")
        if pergunta_sem_pontuacao != pergunta_original:
            variacoes.append({
                "pergunta": pergunta_sem_pontuacao,
                "resposta": resposta
            })
    
    return variacoes

def adicionar_perguntas_avancadas():
    """
    Adiciona perguntas mais complexas e contextuais
    """
    avancadas = [
        {
            "pergunta": "Explique o conceito de deep learning",
            "resposta": "Deep learning é uma técnica de machine learning que usa redes neurais com múltiplas camadas para aprender representações complexas de dados."
        },
        {
            "pergunta": "Como funciona uma rede neural?",
            "resposta": "Uma rede neural artificial é inspirada no cérebro humano, com neurônios artificiais conectados que processam informações através de pesos e funções de ativação."
        },
        {
            "pergunta": "O que é PostgreSQL?",
            "resposta": "PostgreSQL é um sistema de gerenciamento de banco de dados relacional de código aberto, poderoso e confiável."
        },
        {
            "pergunta": "O que é FastAPI?",
            "resposta": "FastAPI é um framework web moderno e rápido para construir APIs com Python, com suporte nativo a tipos e documentação automática."
        },
        {
            "pergunta": "Você pode me ajudar?",
            "resposta": "Claro! Estou aqui para ajudar. O que você precisa?"
        },
        {
            "pergunta": "Obrigado",
            "resposta": "De nada! Fico feliz em ajudar. Se precisar de mais alguma coisa, é só chamar!"
        },
        {
            "pergunta": "Até logo",
            "resposta": "Até logo! Foi um prazer conversar com você. Volte sempre!"
        },
    ]
    
    return avancadas

def salvar_dataset(dataset, nome_arquivo="dataset_expandido.json"):
    """
    Salva dataset em arquivo JSON
    """
    # Remover duplicatas
    dataset_unico = []
    perguntas_vistas = set()
    
    for item in dataset:
        pergunta_normalizada = item["pergunta"].lower().strip()
        if pergunta_normalizada not in perguntas_vistas:
            dataset_unico.append(item)
            perguntas_vistas.add(pergunta_normalizada)
    
    # Salvar
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dataset_unico, f, ensure_ascii=False, indent=2)
    
    return len(dataset_unico)

def gerar_estatisticas(dataset):
    """
    Gera estatísticas do dataset
    """
    total_pares = len(dataset)
    
    # Comprimento médio de perguntas e respostas
    len_perguntas = [len(item["pergunta"]) for item in dataset]
    len_respostas = [len(item["resposta"]) for item in dataset]
    
    stats = {
        "total_pares": total_pares,
        "media_len_pergunta": sum(len_perguntas) / len(len_perguntas),
        "media_len_resposta": sum(len_respostas) / len(len_respostas),
        "pergunta_mais_curta": min(len_perguntas),
        "pergunta_mais_longa": max(len_perguntas),
        "resposta_mais_curta": min(len_respostas),
        "resposta_mais_longa": max(len_respostas),
    }
    
    return stats

def main():
    """
    Gera dataset completo
    """
    print("=" * 70)
    print("📊 ALICI™ - Gerador de Dataset")
    print("=" * 70)
    
    print("\n🔨 Gerando dataset base...")
    dataset = gerar_dataset_base()
    print(f"  ✅ {len(dataset)} pares base criados")
    
    print("\n🔄 Adicionando variações...")
    variacoes = adicionar_variacoes(dataset)
    dataset.extend(variacoes)
    print(f"  ✅ {len(variacoes)} variações adicionadas")
    
    print("\n🧠 Adicionando perguntas avançadas...")
    avancadas = adicionar_perguntas_avancadas()
    dataset.extend(avancadas)
    print(f"  ✅ {len(avancadas)} perguntas avançadas adicionadas")
    
    print("\n💾 Salvando dataset...")
    total = salvar_dataset(dataset)
    print(f"  ✅ Dataset salvo com {total} pares únicos")
    
    print("\n📊 Estatísticas do dataset:")
    stats = gerar_estatisticas(dataset)
    print(f"  • Total de pares: {stats['total_pares']}")
    print(f"  • Média caracteres pergunta: {stats['media_len_pergunta']:.1f}")
    print(f"  • Média caracteres resposta: {stats['media_len_resposta']:.1f}")
    print(f"  • Pergunta mais curta: {stats['pergunta_mais_curta']} caracteres")
    print(f"  • Pergunta mais longa: {stats['pergunta_mais_longa']} caracteres")
    
    print("\n✅ Dataset gerado com sucesso!")
    print(f"\n📁 Arquivo: dataset_expandido.json")
    print(f"📈 Próximo passo: Use este arquivo no Google Colab para fine-tuning")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
