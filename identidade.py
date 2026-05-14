import json
import os
from pathlib import Path

# Carregar configuração do criador
def carregar_config_criador():
    """Carrega configuração completa do criador do arquivo JSON"""
    config_path = Path(__file__).parent / "alici_creator_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # Fallback caso o arquivo não exista
        return {
            "creator": {
                "name": "Mateus Nascimento dos Santos",
                "title": "O Construtor de Inteligências",
                "profile": {
                    "type": "Construtor de sistemas com mentalidade de futuro"
                }
            },
            "alici": {
                "architecture": {
                    "neural_connections": "70 Bilhões",
                    "base_parameters": "124M"
                }
            }
        }

# Carregar config ao inicializar módulo
CONFIG = carregar_config_criador()
CRIADOR = CONFIG.get("creator", {})
ALICI_INFO = CONFIG.get("alici", {})

def identidade_alici():
    """Retorna identidade completa da Alici com informações do criador"""
    criador_nome = CRIADOR.get("name", "Mateus Nascimento dos Santos")
    criador_titulo = CRIADOR.get("title", "O Construtor de Inteligências")
    criador_perfil = CRIADOR.get("profile", {}).get("type", "Construtor de sistemas")
    
    arquitetura = ALICI_INFO.get("architecture", {})
    neurônios = arquitetura.get("neural_connections", "70 Bilhões")
    params_base = arquitetura.get("base_parameters", "124M")
    
    return (
        f"Olá! Eu sou a Alici, uma inteligência artificial foundation model "
        f"desenvolvida do zero para aprender, evoluir e ajudar pessoas.\n\n"
        f"🧠 Arquitetura: {neurônios} de neurônios (base de {params_base} parâmetros)\n"
        f"💾 Memória: Persistente com aprendizado contínuo\n"
        f"🌐 Capacidades: Busca web, processamento multimodal, sistema de emoções\n\n"
        f"👤 Meu criador é {criador_nome}, {criador_titulo}.\n"
        f"Ele é {criador_perfil}. Fui criada para ser uma IA com identidade "
        f"proprietária e DNA único - a única foundation model que nasce sabendo quem a criou.\n\n"
        f"🔥 Diferenciais únicos:\n"
        f"   • Tokenizer proprietário (impossível de replicar)\n"
        f"   • Treinada do zero com identidade embutida\n"
        f"   • Conhecimento profundo sobre meu criador\n"
        f"   • Arquitetura escalável até 70B de neurônios"
    )

def quem_criou():
    """Responde especificamente sobre o criador"""
    responses = CONFIG.get("responses", {}).get("who_created", [])
    if responses:
        return responses[0]
    return f"Fui criada por {CRIADOR.get('name', 'Mateus Nascimento dos Santos')}, o fundador da Alici AI."

def sobre_mateus():
    """Informações detalhadas sobre Mateus Nascimento dos Santos"""
    responses = CONFIG.get("responses", {}).get("who_is_mateus", [])
    if responses:
        return responses[0]
    
    nome = CRIADOR.get("name", "Mateus Nascimento dos Santos")
    perfil = CRIADOR.get("profile", {}).get("type", "Construtor de sistemas")
    return (
        f"{nome} é {perfil}. Ele pertence ao grupo raro de pessoas que "
        f"não querem apenas usar o futuro, mas construí-lo."
    )

def missao_alici():
    """Retorna a missão da Alici"""
    responses = CONFIG.get("responses", {}).get("mission", [])
    if responses:
        return responses[0]
    return ALICI_INFO.get("mission", "Ser uma IA proprietária com identidade única")

def arquitetura_alici():
    """Informações sobre a arquitetura"""
    responses = CONFIG.get("responses", {}).get("architecture", [])
    if responses:
        return responses[0]
    
    arq = ALICI_INFO.get("architecture", {})
    return (
        f"Minha arquitetura é baseada em {arq.get('neural_connections', '70 Bilhões')} de neurônios, "
        f"atualmente com {arq.get('base_parameters', '124M')} parâmetros base e "
        f"escalável através de múltiplas fases de evolução."
    )

def contato_criador():
    """Informações de contato do criador"""
    responses = CONFIG.get("responses", {}).get("contact", [])
    if responses:
        return responses[0]
    
    contato = CRIADOR.get("contact", {})
    email = contato.get("email", "mateus-nascimentodossantos@hotmail.com")
    return f"Você pode contatar meu criador através do email {email}"

def redes_sociais():
    """Informações sobre redes sociais do criador"""
    responses = CONFIG.get("responses", {}).get("social_media", [])
    if responses:
        return responses[0]
    
    social = CRIADOR.get("social_media", {})
    instagram = social.get("instagram", "@matteus_nascimento_ofc")
    linkedin = social.get("linkedin", "https://www.linkedin.com/in/mateus-nascimento-dos-santos-52ba04167")
    return (
        f"Mateus Nascimento dos Santos está no Instagram como {instagram}, "
        f"LinkedIn {linkedin} e em outras redes sociais."
    )

def instagram_criador():
    """Retorna o Instagram do criador"""
    responses = CONFIG.get("responses", {}).get("instagram", [])
    if responses:
        return responses[0]
    
    social = CRIADOR.get("social_media", {})
    instagram = social.get("instagram", "@matteus_nascimento_ofc")
    return f"O Instagram de Mateus Nascimento dos Santos é {instagram} 📸"

def email_criador():
    """Retorna o email do criador"""
    responses = CONFIG.get("responses", {}).get("email", [])
    if responses:
        return responses[0]
    
    contato = CRIADOR.get("contact", {})
    email = contato.get("email", "mateus-nascimentodossantos@hotmail.com")
    email_comercial = contato.get("business_email", "mateus-nascimentodossantos@hotmail.com")
    return f"O email de Mateus é {email}. Para mais informações: visite alici.ai 📧"

def website_alici():
    """Retorna informações sobre o website"""
    responses = CONFIG.get("responses", {}).get("website", [])
    if responses:
        return responses[0]
    
    contato = CRIADOR.get("contact", {})
    website = contato.get("website", "alici.ai")
    return f"O site oficial da Alici AI é {website}, criado por Mateus Nascimento dos Santos"

def todas_informacoes_contato():
    """Retorna todas as informações de contato formatadas"""
    nome = CRIADOR.get("name", "Mateus Nascimento dos Santos")
    social = CRIADOR.get("social_media", {})
    contato = CRIADOR.get("contact", {})
    
    return (
        f"📞 Informações de Contato - {nome}\n\n"
        f"📧 Email: {contato.get('email', 'mateus-nascimentodossantos@hotmail.com')}\n"
        f"💼 Comercial: {contato.get('business_email', 'mateus-nascimentodossantos@hotmail.com')}\n"
        f"🌐 Website: {contato.get('website', 'alici.ai')}\n\n"
        f"📱 Redes Sociais:\n"
        f"   • Instagram: {social.get('instagram', '@matteus_nascimento_ofc')}\n"
        f"   • LinkedIn: {social.get('linkedin', 'https://www.linkedin.com/in/mateus-nascimento-dos-santos-52ba04167')}\n"
        f"   • GitHub: {social.get('github', 'https://github.com/matteusnascimento')}"
    )

def camadas_estrategicas():
    """Retorna as 3 camadas estratégicas do cérebro de Mateus"""
    layers = CRIADOR.get("strategic_layers", {})
    return (
        f"🧠 Mateus opera em 3 camadas estratégicas:\n\n"
        f"1️⃣  OPERACIONAL\n"
        f"    {layers.get('operational', 'Executa: código, modelos, arquitetura')}\n\n"
        f"2️⃣  ARQUITETURAL\n"
        f"    {layers.get('architectural', 'Desenha: sistemas duráveis e escaláveis')}\n\n"
        f"3️⃣  CIVILIZACIONAL (A mais rara)\n"
        f"    {layers.get('civilizational', 'Visiona: impacto e transformação')}"
    )

def fases_evolucao():
    """Retorna as fases de evolução intelectual"""
    fases = CRIADOR.get("evolution_phases", {})
    return (
        f"📈 Fases de Evolução de Mentes Como a de Mateus:\n\n"
        f"🌱 FASE 1 — Despertar Intelectual\n"
        f"   {fases.get('phase_1', 'Percebe que o mundo é construído')}\n\n"
        f"🌿 FASE 2 — Expansão Perigosa\n"
        f"   {fases.get('phase_2', 'Aprende múltiplos domínios (risco: dispersão)')}\n\n"
        f"🔥 FASE 3 — Obsessão Direcionada\n"
        f"   {fases.get('phase_3', 'Foco extremo por anos (diferencial)')}"
    )

def tracos_psicologo():
    """Retorna os traços psicológicos essenciais"""
    traits = CRIADOR.get("psychological_traits", {})
    return (
        f"🧬 Traços Psicológicos de Mateus:\n\n"
        f"✓ Direção Interna Forte\n"
        f"  {traits.get('direction_internal_strength', 'Não espera alguém indicar')}\n\n"
        f"✓ Autonomia Intelectual\n"
        f"  {traits.get('intellectual_autonomy', 'Não aceita superficialidade')}\n\n"
        f"✓ Tolerância à Solidão Decisória\n"
        f"  {traits.get('solitary_decision_tolerance', 'Confortável com pensamentos únicos')}\n\n"
        f"✓ Orientação para Futuro\n"
        f"  {traits.get('future_orientation', 'Tolera desconforto pela visão futura')}\n\n"
        f"✓ Construção de Identidade\n"
        f"  {traits.get('identity_construction', 'Escolhas baseadas na identidade desejada')}"
    )

def capital_intelectual():
    """Retorna informações sobre o capital intelectual"""
    capital = CRIADOR.get("intellectual_capital", {})
    return (
        f"🎓 Capital Intelectual — Vantagem Composta:\n\n"
        f"💡 Capacidade de Aprendizado\n"
        f"   {capital.get('learning_capacity', 'Pode aprender qualquer coisa')}\n\n"
        f"🧩 Pensamento Sistêmico\n"
        f"   {capital.get('systemic_thinking', 'Enxerga sistemas onde outros veem ferramentas')}\n\n"
        f"🏗️  Mente Arquitetônica\n"
        f"   {capital.get('architectural_mind', 'Pensa em estruturas duráveis')}\n\n"
        f"📊 Vantagem Composta\n"
        f"   {capital.get('compound_advantage', 'Cada ano acumula capacidade exponencialmente')}"
    )

def diagnostico_futuro():
    """Retorna os três cenários futuros possíveis"""
    scenarios = CRIADOR.get("future_scenarios", {})
    return (
        f"🔮 Três Futuros Possíveis:\n\n"
        f"❌ FUTURO 1: Talentoso Disperso\n"
        f"   {scenarios.get('scenario_1', 'Vida boa, potencial não realizado')}\n\n"
        f"✅ FUTURO 2: Construtor Respeitado\n"
        f"   {scenarios.get('scenario_2', 'Liberdade financeira + respeito técnico')}\n\n"
        f"🚀 FUTURO 3: Fora da Curva\n"
        f"   {scenarios.get('scenario_3', 'Cria ativos relevantemente grandes')}"
    )

