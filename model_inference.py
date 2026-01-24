"""
model_inference.py
Módulo de inferência para o modelo CIFAR-100 treinado
Carrega o modelo e realiza previsões em imagens
"""

import os
import numpy as np
from PIL import Image
import tensorflow as tf
from keras.models import load_model

# Mapeamento de classes CIFAR-100 (apenas animais e objetos relevantes)
CIFAR100_LABELS = [
    'apple', 'aquarium_fish', 'baby', 'bear', 'beaver', 'bed', 'bee', 'beetle',
    'bicycle', 'bottle', 'bowl', 'boy', 'bridge', 'bus', 'butterfly', 'camel',
    'can', 'castle', 'caterpillar', 'cattle', 'chair', 'chimpanzee', 'clock',
    'cloud', 'cockroach', 'couch', 'crab', 'crocodile', 'cup', 'cupboard',
    'curtain', 'curve', 'cushion', 'cut', 'daisy', 'damaged', 'date', 'deer',
    'delicious', 'dentist', 'desk', 'diamond', 'diaper', 'dice', 'diesel',
    'difference', 'different', 'digital', 'dining', 'dinner', 'dinosaur',
    'direct', 'dirt', 'disc', 'disease', 'dish', 'dishwasher', 'display',
    'distance', 'distribution', 'dock', 'doctor', 'document', 'dog', 'doll',
    'dolphin', 'domain', 'dome', 'dominant', 'dominoes', 'donkey', 'donor',
    'door', 'dormitory', 'dose', 'dot', 'double', 'doubt', 'dove', 'down',
    'dozen', 'draft', 'dragon', 'dragonfly', 'drain', 'drake', 'drama',
    'drank', 'drape', 'draw', 'drawer', 'drawing', 'dread', 'dream', 'dress'
]

# Usar apenas os primeiros 100 labels CIFAR-100
CIFAR100_LABELS = CIFAR100_LABELS[:100]

# Cache para o modelo (carregado uma vez)
_model_cache = None


def carregar_modelo(caminho_modelo: str = None) -> tf.keras.Model:
    """
    Carrega o modelo CIFAR-100 treinado.
    Usa cache para evitar recarregar em cada predição.
    
    Args:
        caminho_modelo: Caminho para o arquivo .h5 (default: modelo_animais_treinado.h5)
    
    Returns:
        Modelo Keras carregado
    """
    global _model_cache
    
    if _model_cache is not None:
        return _model_cache
    
    if caminho_modelo is None:
        caminho_modelo = os.path.join(os.path.dirname(__file__), 'modelo_animais_treinado.h5')
    
    if not os.path.exists(caminho_modelo):
        raise FileNotFoundError(f"Modelo não encontrado: {caminho_modelo}")
    
    print(f"[INFO] Carregando modelo de: {caminho_modelo}")
    _model_cache = load_model(caminho_modelo)
    print(f"[INFO] Modelo carregado com sucesso!")
    
    return _model_cache


def preprocessar_imagem(imagem_path: str, tamanho: tuple = (32, 32)) -> np.ndarray:
    """
    Preprocessa uma imagem para entrada no modelo.
    CIFAR-100 espera imagens 32x32 RGB normalizadas [0, 1].
    
    Args:
        imagem_path: Caminho para a imagem
        tamanho: Tamanho da imagem (default: 32x32)
    
    Returns:
        Array numpy normalizado pronto para modelo
    """
    # Abrir imagem
    img = Image.open(imagem_path).convert('RGB')
    
    # Redimensionar para 32x32
    img = img.resize(tamanho, Image.Resampling.LANCZOS)
    
    # Converter para array numpy
    img_array = np.array(img, dtype=np.float32)
    
    # Normalizar [0, 255] -> [0, 1]
    img_array = img_array / 255.0
    
    # Adicionar dimensão de batch: (32, 32, 3) -> (1, 32, 32, 3)
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def fazer_predicao(imagem_path: str, top_k: int = 3) -> dict:
    """
    Realiza predição em uma imagem usando o modelo CIFAR-100.
    
    Args:
        imagem_path: Caminho para a imagem
        top_k: Número de top predições a retornar
    
    Returns:
        Dicionário com:
            - classe: Classe predita com maior confiança
            - confianca: Porcentagem de confiança (0-100)
            - top_k: Lista com as K melhores predições
            - erro: Mensagem de erro (se houver)
    """
    try:
        # Carregar modelo
        modelo = carregar_modelo()
        
        # Preprocessar imagem
        img_preprocessada = preprocessar_imagem(imagem_path)
        
        # Fazer predição
        predicoes = modelo.predict(img_preprocessada, verbose=0)
        
        # Extrair probabilidades e índices
        probabilidades = predicoes[0]
        indices_top_k = np.argsort(probabilidades)[::-1][:top_k]
        
        # Classe com maior confiança
        classe_idx = indices_top_k[0]
        classe_nome = CIFAR100_LABELS[classe_idx]
        confianca = float(probabilidades[classe_idx] * 100)
        
        # Top K predições
        top_predicoes = []
        for idx in indices_top_k:
            top_predicoes.append({
                'classe': CIFAR100_LABELS[idx],
                'confianca': float(probabilidades[idx] * 100)
            })
        
        return {
            'classe': classe_nome,
            'confianca': confianca,
            'top_k': top_predicoes,
            'status': 'sucesso'
        }
    
    except Exception as e:
        return {
            'erro': str(e),
            'status': 'erro'
        }


def gerar_resposta_predicao(resultado_predicao: dict) -> str:
    """
    Converte resultado de predição em resposta natural em português.
    
    Args:
        resultado_predicao: Resultado de fazer_predicao()
    
    Returns:
        String com resposta em português natural
    """
    if resultado_predicao.get('status') == 'erro':
        return f"Desculpa, tive um problema ao analisar a imagem: {resultado_predicao.get('erro', 'erro desconhecido')}"
    
    classe = resultado_predicao.get('classe', 'desconhecido')
    confianca = resultado_predicao.get('confianca', 0)
    top_k = resultado_predicao.get('top_k', [])
    
    # Resposta principal
    resposta = f"Detectei um **{classe}** com **{confianca:.1f}%** de confiança!"
    
    # Adicionar outras possibilidades se confiança não é muito alta
    if confianca < 85 and len(top_k) > 1:
        alternativas = ", ".join([f"{p['classe']} ({p['confianca']:.1f}%)" for p in top_k[1:3]])
        resposta += f"\n\nOutras possibilidades: {alternativas}"
    
    return resposta


def testar_modelo(imagem_exemplo: str = None) -> dict:
    """
    Testa o modelo carregando e fazendo uma predição de teste.
    
    Args:
        imagem_exemplo: Caminho para imagem de teste (opcional)
    
    Returns:
        Resultado do teste
    """
    try:
        print("[TEST] Carregando modelo...")
        modelo = carregar_modelo()
        print(f"[TEST] Modelo carregado! Resumo:")
        print(f"       - Camadas: {len(modelo.layers)}")
        print(f"       - Parâmetros: {modelo.count_params():,}")
        print(f"       - Input shape: {modelo.input_shape}")
        print(f"       - Output shape: {modelo.output_shape}")
        
        if imagem_exemplo and os.path.exists(imagem_exemplo):
            print(f"[TEST] Testando com imagem: {imagem_exemplo}")
            resultado = fazer_predicao(imagem_exemplo)
            print(f"[TEST] Predição: {resultado}")
            return resultado
        else:
            print("[TEST] Nenhuma imagem de teste fornecida, apenas verificação de carregamento concluída")
            return {'status': 'modelo_carregado', 'parametros': modelo.count_params()}
    
    except Exception as e:
        print(f"[ERROR] Erro ao testar modelo: {e}")
        return {'status': 'erro', 'erro': str(e)}


if __name__ == "__main__":
    # Teste rápido
    resultado_teste = testar_modelo()
    print(f"\nResultado do teste: {resultado_teste}")
