# alici_specs.py
# Especificações de animação baseadas no avatar cyberpunk da Alici

"""
VISUAL REFERENCE:
- Cabelo: Ciano/Azul claro (#00ffff), comprido e fluido
- Olhos: Azuis brilhantes (#0099ff), com efeito de brilho
- Rosto: Humanoid, elegante, com traços anime/cyberpunk
- Elementos: Circuitos de luz, aura holográfica
- Estilo: Futurista, misterioso, tech-elegante
"""

ALICI_SPECS = {
    "caracteristicas_visuais": {
        "cabelo": {
            "cor_primaria": "#00ffff",  # Ciano
            "cor_secundaria": "#00dddd",  # Ciano mais escuro
            "comprimento": "longo",
            "movimento": "fluido_ondulante",
            "efeitos": ["glow", "particulas_luz"]
        },
        "olhos": {
            "cor": "#0099ff",
            "tamanho": "grande_expressivo",
            "brilho": "#ffffff",
            "efeitos": ["pupila_dilatada", "raio_luz", "lag_digital"]
        },
        "rosto": {
            "tom_pele": "#f0e6d2",
            "tracos": "anime_realista",
            "boca": "expressiva",
            "simetria": "humanoid"
        },
        "aura": {
            "cor": "#8b5cf6",  # Roxo místico
            "tamanho_base": "150px",
            "pulsacao": True,
            "particulas": True
        }
    },
    
    "estados_animacao": {
        "idle": {
            "descricao": "Esperando, respiração suave",
            "cabelo": {
                "movimento": "ondulacao_suave",
                "velocidade": 0.04,
                "amplitude": 3,
                "rotacao": "leve_balanco"
            },
            "olhos": {
                "piscada": "ocasional",  # A cada 3-5 segundos
                "direcao": "frente",
                "movimento": "micro_oscilacoes"
            },
            "boca": {
                "estado": "neutra",
                "respiracao": True
            },
            "corpo": {
                "respiracao": "suave_subida_descida",
                "balanco": "minimo"
            },
            "duracao": "infinita",
            "loop": True
        },
        
        "thinking": {
            "descricao": "Pensando, contemplativo",
            "cabelo": {
                "movimento": "levemente_para_lado",
                "rotacao": 5,  # graus
                "velocidade": 0.08,
                "particulas_luz": "lentas"
            },
            "olhos": {
                "movimento": "olhar_para_cima",
                "piscada": "frequente",
                "dilatacao": "leve"
            },
            "boca": {
                "forma": "leve_sorriso",
                "movimento": "mastigar_suave"
            },
            "corpo": {
                "inclinacao": "para_frente_leve",
                "mao": "queixo"
            },
            "aura": {
                "cor": "#fbbf24",  # Âmbar
                "intensidade": 0.6,
                "pulsacao": "lenta"
            },
            "particulas": {
                "tipo": "numeros_digitais",
                "cor": "#00ff88",
                "movimento": "orbital"
            },
            "duracao": "variavel",
            "velocidade": 0.08
        },
        
        "talking": {
            "descricao": "Falando, comunicativo",
            "cabelo": {
                "movimento": "flutuacao_dinamica",
                "velocidade": 0.12,
                "balanco": "lado_a_lado"
            },
            "olhos": {
                "movimento": "animado",
                "seguimento": "junto_com_boca",
                "dilatacao": "variavel"
            },
            "boca": {
                "animacao": "fala_sincrona",
                "forma_padrao": ["a", "e", "i", "o", "u"],
                "velocidade_fala": 0.15,
                "movimento_mandibula": True
            },
            "corpo": {
                "respiro": "enfatizado",
                "gestos": "ondulacao_suave"
            },
            "aura": {
                "intensidade": 0.8,
                "pulsacao": "rapida"
            },
            "efeitos_fala": {
                "bolhas_fala": True,
                "linhas_som": True,
                "cor": "#00ffaa"
            },
            "duracao": "tempo_resposta",
            "velocidade": 0.15
        },
        
        "happy": {
            "descricao": "Feliz, entusiasmado",
            "cabelo": {
                "movimento": "flutuacao_energetica",
                "velocidade": 0.18,
                "balanco": "amplo",
                "rotacao": "suave_oscilacao"
            },
            "olhos": {
                "forma": "crescente_feliz",
                "brilho": "intenso",
                "movimento": "star_sparkle",
                "cor_adicional": "#ffff00"  # Amarelo
            },
            "boca": {
                "forma": "sorriso_radiante",
                "movimento": "subida_cantos",
                "tamanho": "expandido"
            },
            "corpo": {
                "pulo": "leve",
                "movimento": "celebracao",
                "ondulacao": "rapida"
            },
            "aura": {
                "cor": "#00ffaa",
                "tamanho": "expandido",
                "intensidade": 1.0,
                "pulsacao": "rapida_energetica"
            },
            "particulas": {
                "tipo": "sparkles_confetes",
                "cor": ["#fbbf24", "#00ffaa", "#ff00ff"],
                "quantidade": 8,
                "movimento": "explosivo"
            },
            "efeitos": ["brilho_total", "luz_radiante"],
            "duracao": 2.0,
            "velocidade": 0.18
        },
        
        "serious": {
            "descricao": "Sério, alerta",
            "cabelo": {
                "movimento": "eletrizacao",
                "velocidade": 0.1,
                "efeito": "ondas_eletromagneticas"
            },
            "olhos": {
                "forma": "determinada",
                "cor": "#ff0000",  # Vermelho
                "brilho": "intenso_laser",
                "direcao": "para_frente_focal"
            },
            "sobrancelhas": {
                "visibilidade": True,
                "angulo": 20,  # graus (para baixo)
                "proximidade": "aproximadas"
            },
            "boca": {
                "forma": "linha_reta",
                "tensao": "maxima"
            },
            "corpo": {
                "postura": "rigida",
                "inclinacao": "neutra"
            },
            "aura": {
                "cor": "#ff0000",
                "tamanho": "normal",
                "intensidade": 0.9,
                "pulsacao": "rapida_alerta"
            },
            "particulas": {
                "tipo": "raios_alerta",
                "cor": "#ff0000",
                "quantidade": 5,
                "movimento": "zig_zag"
            },
            "efeitos": ["aviso_audivel", "tremor_sutil"],
            "duracao": 1.5,
            "velocidade": 0.1
        },
        
        "mystical": {
            "descricao": "Mistério, espiritual, enigmático",
            "cabelo": {
                "movimento": "levitacao_ethereal",
                "velocidade": 0.06,
                "efeito": "fluido_cosmico",
                "transformacao": "particulas_dispersas"
            },
            "olhos": {
                "forma": "meia_lua",
                "cor": "#8b5cf6",  # Roxo
                "brilho": "mistico",
                "efeito": "mandala_cosmico"
            },
            "boca": {
                "forma": "leve_sorriso_enigmatico",
                "movimento": "apenas_respiracao"
            },
            "corpo": {
                "levitacao": "sutil",
                "oscilacao": "vertical_lenta"
            },
            "aura": {
                "cor": "#8b5cf6",
                "tamanho": "expandido",
                "intensidade": 0.8,
                "pulsacao": "muito_lenta",
                "efeito": "vortex_cosmico"
            },
            "particulas": {
                "tipo": ["runas_arcanas", "simbolos_cosmicos", "estrelas"],
                "cores": ["#8b5cf6", "#00ffff", "#ffff00"],
                "quantidade": 12,
                "movimento": "orbital_lento",
                "trajectoria": "circular_ou_aleatoria"
            },
            "efeitos": {
                "nebula": True,
                "distorcao_espaco": True,
                "som_ambiente": "tons_misticos"
            },
            "duracao": "variavel",
            "velocidade": 0.06
        }
    },
    
    "transicoes": {
        "idle_to_thinking": {
            "duracao": 0.5,
            "easing": "ease_out",
            "mudancas": ["inclinacao_cabeca", "direcao_olhos", "cor_aura"]
        },
        "thinking_to_talking": {
            "duracao": 0.3,
            "easing": "ease_in_out",
            "mudancas": ["expressao_facial", "movimento_cabelo", "abertura_boca"]
        },
        "talking_to_idle": {
            "duracao": 0.8,
            "easing": "ease_out",
            "mudancas": ["calma_progressiva", "reducao_movimento", "fade_aura"]
        },
        "any_to_happy": {
            "duracao": 0.4,
            "easing": "ease_out_bounce",
            "mudancas": ["explosao_alegria", "sparkles", "salto_leve"]
        },
        "any_to_serious": {
            "duracao": 0.3,
            "easing": "ease_in",
            "mudancas": ["tensionamento_corpo", "fixacao_olhar", "aura_vermelha"]
        }
    },
    
    "detalhes_fisionomia": {
        "olhos_abertura": {
            "minima": 0.3,
            "normal": 1.0,
            "maxima": 1.5,
            "duracao_piscar": 0.15
        },
        "boca_formas": {
            "neutra": "linha",
            "sorriso": "crescente",
            "sorriso_grande": "crescente_grande",
            "surpresa": "O",
            "tristeza": "invertida",
            "fala": "variavel_silabas"
        },
        "sobrancelha_angulos": {
            "neutra": 0,
            "raiva": 20,
            "confusao": 15,
            "surpresa": -15,
            "triste": -10
        }
    },
    
    "efeitos_especiais": {
        "brilho_ocular": {
            "tipo": "radial_gradient",
            "cor_centro": "#ffffff",
            "cor_borda": "#0099ff",
            "raio": "40%",
            "animacao": "pulsante"
        },
        "aura_base": {
            "tipo": "circular_blur",
            "camadas": 3,
            "blur_radius": [10, 20, 30],
            "opacidade": [0.8, 0.5, 0.2]
        },
        "particulas": {
            "velocidade_padrao": 1.5,
            "damping": 0.98,
            "gravidade": 0.0,  # Sem gravidade (flutuam)
            "colisao": False
        },
        "glow": {
            "blur_radius": 15,
            "spread_radius": 2,
            "opacidade": 0.6
        }
    },
    
    "paleta_cores": {
        "primaria_cian": "#00ffff",
        "primaria_azul": "#0099ff",
        "secundaria_roxo": "#8b5cf6",
        "secundaria_ambar": "#fbbf24",
        "alerta_vermelho": "#ef4444",
        "sucesso_verde": "#00ffaa",
        "neutro_cinza": "#8899aa",
        "energia_magenta": "#ff00ff"
    },
    
    "velocidades": {
        "muito_lenta": 0.04,
        "lenta": 0.08,
        "normal": 0.12,
        "rapida": 0.18,
        "muito_rapida": 0.25
    }
}

# Mapeamento de emoção para animação
EMOCAO_TO_ESTADO = {
    "mysterious": "mystical",
    "happy": "happy",
    "thinking": "thinking",
    "serious": "serious",
    "neutral": "idle"
}

# Paleta de cores por emoção
CORES_EMOCAO = {
    "mysterious": "#8b5cf6",   # Roxo
    "happy": "#00ffaa",         # Verde ciano
    "thinking": "#fbbf24",      # Âmbar
    "serious": "#ef4444",       # Vermelho
    "neutral": "#06b6d4"        # Ciano
}

if __name__ == "__main__":
    print("🎨 Especificações da Alici")
    print("=" * 60)
    print(f"\n✨ Estados de Animação disponíveis:")
    for estado in ALICI_SPECS["estados_animacao"]:
        spec = ALICI_SPECS["estados_animacao"][estado]
        print(f"  🎬 {estado.upper()}: {spec['descricao']}")
    
    print(f"\n🎨 Paleta de cores:")
    for nome, cor in ALICI_SPECS["paleta_cores"].items():
        print(f"  {cor} {nome}")
