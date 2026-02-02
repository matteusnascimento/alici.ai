"""
model_inference.py
🤖 Módulo de inferência para modelos de ML
Usado para predições de imagem (CIFAR-100)
"""

import os
import numpy as np
from PIL import Image

# Tentar importar TensorFlow
try:
    import tensorflow as tf
    TENSORFLOW_DISPONIVEL = True
except ImportError:
    TENSORFLOW_DISPONIVEL = False
    print("[WARNING] TensorFlow não disponível")

# ============================================================================
# CLASSES CIFAR-100 (ANIMAIS)
# ============================================================================

CIFAR100_CLASSES = [
    "apple", "aquarium_fish", "baby", "bear", "beaver", "bed", "bee", "beetle",
    "bicycle", "bottle", "bowl", "boy", "bridge", "bus", "butterfly", "camel",
    "can", "castle", "caterpillar", "cattle", "chair", "chimpanzee", "clock",
    "cloud", "cockroach", "couch", "crab", "crocodile", "cup", "dinosaur",
    "dolphin", "elephant", "flatfish", "forest", "fox", "girl", "hamster",
    "house", "kangaroo", "keyboard", "lamp", "lawn_mower", "leopard", "lion",
    "lizard", "lobster", "man", "maple_tree", "motorcycle", "mountain", "mouse",
    "mushroom", "oak_tree", "orange", "orchid", "otter", "palm_tree", "pear",
    "pickup_truck", "pine_tree", "plain", "plate", "poppy", "porcupine",
    "possum", "rabbit", "raccoon", "ray", "road", "rocket", "rose", "sea",
    "seal", "shark", "shrew", "skunk", "skyscraper", "snail", "snake", "spider",
    "squirrel", "streetcar", "sunflower", "sweet_pepper", "table", "tank",
    "telephone", "television", "tiger", "tractor", "train", "trout", "tulip",
    "turtle", "wardrobe", "whale", "willow_tree", "wolf", "woman", "worm"
]

# Tradução para português (animais apenas)
TRADUCAO_PT = {
    "bear": "urso",
    "beaver": "castor",
    "bee": "abelha",
    "beetle": "besouro",
    "butterfly": "borboleta",
    "camel": "camelo",
    "caterpillar": "lagarta",
    "cattle": "gado",
    "chimpanzee": "chimpanzé",
    "cockroach": "barata",
    "crab": "caranguejo",
    "crocodile": "crocodilo",
    "dinosaur": "dinossauro",
    "dolphin": "golfinho",
    "elephant": "elefante",
    "flatfish": "linguado",
    "fox": "raposa",
    "hamster": "hamster",
    "kangaroo": "canguru",
    "leopard": "leopardo",
    "lion": "leão",
    "lizard": "lagarto",
    "lobster": "lagosta",
    "mouse": "rato",
    "otter": "lontra",
    "porcupine": "porco-espinho",
    "possum": "gambá",
    "rabbit": "coelho",
    "raccoon": "guaxinim",
    "ray": "arraia",
    "seal": "foca",
    "shark": "tubarão",
    "shrew": "musaranho",
    "skunk": "cangambá",
    "snail": "caracol",
    "snake": "cobra",
    "spider": "aranha",
    "squirrel": "esquilo",
    "tiger": "tigre",
    "trout": "truta",
    "turtle": "tartaruga",
    "whale": "baleia",
    "wolf": "lobo",
    "worm": "verme"
}

# ============================================================================
# CARREGAR MODELO
# ============================================================================

_modelo_cache = None

def carregar_modelo():
    """
    Carrega modelo de forma lazy (apenas quando necessário)
    """
    global _modelo_cache
    
    if not TENSORFLOW_DISPONIVEL:
        return None
    
    if _modelo_cache is not None:
        return _modelo_cache
    
    # Procurar modelo em vários locais
    caminhos_possiveis = [
        "modelo_animais.h5",
        "model/modelo_animais_cifar100.h5",
        "model/modelo_animais_treinado.h5",
        "Modelo/modelo_animais_cifar100.h5",
    ]
    
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            try:
                print(f"[INFO] Carregando modelo: {caminho}")
                _modelo_cache = tf.keras.models.load_model(caminho)
                print(f"[INFO] Modelo carregado com sucesso")
                return _modelo_cache
            except Exception as e:
                print(f"[WARNING] Erro ao carregar {caminho}: {e}")
    
    print("[WARNING] Nenhum modelo encontrado")
    return None

# ============================================================================
# PREPROCESSAMENTO
# ============================================================================

def preprocessar_imagem(caminho_imagem, target_size=(32, 32)):
    """
    Preprocessa imagem para o formato esperado pelo modelo
    """
    try:
        # Carregar imagem
        img = Image.open(caminho_imagem)
        
        # Converter para RGB (se necessário)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Converter para array numpy
        img_array = np.array(img, dtype=np.float32)
        
        # Normalizar para [0, 1]
        img_array = img_array / 255.0
        
        # Adicionar dimensão de batch
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
        
    except Exception as e:
        raise Exception(f"Erro ao preprocessar imagem: {e}")

# ============================================================================
# PREDIÇÃO
# ============================================================================

def fazer_predicao(caminho_imagem, top_k=5):
    """
    Faz predição em uma imagem
    
    Args:
        caminho_imagem: Caminho para arquivo de imagem
        top_k: Número de top predições a retornar
    
    Returns:
        dict com resultado da predição
    """
    if not TENSORFLOW_DISPONIVEL:
        return {
            "status": "erro",
            "erro": "TensorFlow não disponível"
        }
    
    # Carregar modelo
    modelo = carregar_modelo()
    
    if modelo is None:
        return {
            "status": "erro",
            "erro": "Modelo não encontrado"
        }
    
    try:
        # Preprocessar imagem
        img_array = preprocessar_imagem(caminho_imagem)
        
        # Fazer predição
        predicoes = modelo.predict(img_array, verbose=0)
        
        # Obter índices das top K predições
        top_indices = np.argsort(predicoes[0])[-top_k:][::-1]
        
        # Montar resultado
        classe_principal = CIFAR100_CLASSES[top_indices[0]]
        confianca = float(predicoes[0][top_indices[0]])
        
        # Top K predições
        top_k_predicoes = []
        for idx in top_indices:
            classe = CIFAR100_CLASSES[idx]
            conf = float(predicoes[0][idx])
            
            # Traduzir se for animal
            classe_pt = TRADUCAO_PT.get(classe, classe)
            
            top_k_predicoes.append({
                "classe": classe,
                "classe_pt": classe_pt,
                "confianca": conf,
                "porcentagem": f"{conf * 100:.2f}%"
            })
        
        return {
            "status": "sucesso",
            "classe": classe_principal,
            "classe_pt": TRADUCAO_PT.get(classe_principal, classe_principal),
            "confianca": confianca,
            "porcentagem": f"{confianca * 100:.2f}%",
            "top_k": top_k_predicoes
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "erro": str(e)
        }

# ============================================================================
# GERAÇÃO DE RESPOSTA
# ============================================================================

def gerar_resposta_predicao(resultado):
    """
    Gera resposta em linguagem natural baseada na predição
    
    Args:
        resultado: Dict retornado por fazer_predicao()
    
    Returns:
        str: Resposta em linguagem natural
    """
    if resultado.get("status") == "erro":
        return f"Desculpe, ocorreu um erro ao analisar a imagem: {resultado.get('erro')}"
    
    classe = resultado.get("classe_pt", resultado.get("classe"))
    confianca = resultado.get("confianca", 0)
    porcentagem = resultado.get("porcentagem", "0%")
    
    # Resposta baseada em confiança
    if confianca >= 0.8:
        nivel = "muito confiante"
    elif confianca >= 0.6:
        nivel = "confiante"
    elif confianca >= 0.4:
        nivel = "razoavelmente confiante"
    else:
        nivel = "não muito confiante"
    
    resposta = f"Analisando sua imagem, estou {nivel} ({porcentagem}) de que se trata de: **{classe}**.\n\n"
    
    # Adicionar alternativas
    top_k = resultado.get("top_k", [])
    if len(top_k) > 1:
        resposta += "Outras possibilidades:\n"
        for i, pred in enumerate(top_k[1:4], 1):  # Top 3 alternativas
            resposta += f"{i}. {pred['classe_pt']} ({pred['porcentagem']})\n"
    
    return resposta

# ============================================================================
# TESTE
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 Teste do Módulo de Inferência")
    print("=" * 70)
    
    # Verificar TensorFlow
    if not TENSORFLOW_DISPONIVEL:
        print("❌ TensorFlow não disponível")
        exit(1)
    
    # Carregar modelo
    print("\n📦 Carregando modelo...")
    modelo = carregar_modelo()
    
    if modelo is None:
        print("❌ Nenhum modelo encontrado")
        print("\nPara treinar um modelo:")
        print("  1. python gerar_dataset.py")
        print("  2. Use colab_finetuning.py no Google Colab")
        exit(1)
    
    print("✅ Modelo carregado com sucesso")
    print(f"   Input shape: {modelo.input_shape}")
    print(f"   Output shape: {modelo.output_shape}")
    
    print("\n🎉 Módulo de inferência pronto!")
    print("\nUso:")
    print(">>> from model_inference import fazer_predicao")
    print(">>> resultado = fazer_predicao('imagem.jpg')")
    print(">>> print(resultado)")
