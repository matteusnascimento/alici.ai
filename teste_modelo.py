"""
teste_modelo.py
🤖 Teste dos modelos de Machine Learning
Verifica se os modelos .h5 estão funcionando
"""

import os
import numpy as np

def verificar_tensorflow():
    """Verifica instalação do TensorFlow"""
    print("\n📦 Verificando TensorFlow...")
    
    try:
        import tensorflow as tf
        print(f"  ✅ TensorFlow {tf.__version__} instalado")
        return True
    except ImportError:
        print(f"  ❌ TensorFlow não instalado")
        print(f"     Execute: pip install tensorflow")
        return False

def listar_modelos():
    """Lista todos os modelos .h5 disponíveis"""
    print("\n📁 Buscando modelos .h5...")
    
    locais = [
        ".",
        "model",
        "Modelo",
    ]
    
    modelos_encontrados = []
    
    for local in locais:
        if os.path.exists(local):
            for arquivo in os.listdir(local):
                if arquivo.endswith(".h5"):
                    caminho = os.path.join(local, arquivo)
                    tamanho = os.path.getsize(caminho) / (1024 * 1024)  # MB
                    modelos_encontrados.append((caminho, tamanho))
                    print(f"  ✅ {caminho} ({tamanho:.2f} MB)")
    
    if not modelos_encontrados:
        print("  ⚠️  Nenhum modelo .h5 encontrado")
    
    return modelos_encontrados

def testar_carregamento(caminho_modelo):
    """Testa carregamento de um modelo"""
    print(f"\n🔄 Testando: {caminho_modelo}")
    
    try:
        import tensorflow as tf
        
        modelo = tf.keras.models.load_model(caminho_modelo)
        print(f"  ✅ Modelo carregado com sucesso")
        
        # Informações do modelo
        print(f"  📊 Informações:")
        print(f"     • Input shape: {modelo.input_shape}")
        print(f"     • Output shape: {modelo.output_shape}")
        
        # Contar parâmetros
        total_params = modelo.count_params()
        print(f"     • Parâmetros: {total_params:,}")
        
        return True, modelo
        
    except Exception as e:
        print(f"  ❌ Erro ao carregar: {e}")
        return False, None

def testar_predicao(modelo, caminho_modelo):
    """Testa predição com entrada dummy"""
    print(f"\n🧪 Testando predição...")
    
    try:
        # Criar entrada dummy baseada no input shape
        input_shape = modelo.input_shape
        
        # Remove batch dimension (None)
        shape = tuple(dim if dim is not None else 1 for dim in input_shape[1:])
        
        entrada = np.random.random((1,) + shape).astype(np.float32)
        
        print(f"  📥 Entrada shape: {entrada.shape}")
        
        # Fazer predição
        predicao = modelo.predict(entrada, verbose=0)
        
        print(f"  📤 Predição shape: {predicao.shape}")
        print(f"  ✅ Predição realizada com sucesso")
        
        # Mostrar top 3 valores
        if predicao.size <= 100:
            top_indices = np.argsort(predicao[0])[-3:][::-1]
            print(f"  📊 Top 3 valores:")
            for idx in top_indices:
                valor = predicao[0][idx]
                print(f"     • Classe {idx}: {valor:.4f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na predição: {e}")
        return False

def testar_engine_com_modelos():
    """Testa integração dos modelos com o engine"""
    print("\n🧠 Testando integração com engine...")
    
    try:
        from engine import responder_com_modelos, MODELOS_OK
        
        if not MODELOS_OK:
            print(f"  ⚠️  Engine reporta que modelos não estão carregados")
            return False
        
        print(f"  ✅ Engine tem modelos carregados")
        
        # Testar resposta
        resposta = responder_com_modelos("teste")
        
        if resposta:
            print(f"  ✅ Engine gerou resposta com modelos")
            print(f"     Preview: {resposta[:80]}...")
        else:
            print(f"  ⚠️  Engine retornou None (esperado para baixa confiança)")
        
        return True
        
    except ImportError:
        print(f"  ⚠️  Módulo engine.py não disponível")
        return False
    except Exception as e:
        print(f"  ⚠️  Erro ao testar engine: {e}")
        return False

def main():
    """Executa todos os testes de modelo"""
    print("=" * 70)
    print("🤖 ALICI™ - Teste dos Modelos de ML")
    print("=" * 70)
    
    # Verificar TensorFlow
    if not verificar_tensorflow():
        print("\n❌ TensorFlow é necessário para continuar")
        return 1
    
    # Listar modelos
    modelos = listar_modelos()
    
    if not modelos:
        print("\n⚠️  Nenhum modelo encontrado")
        print("\nPara treinar modelos:")
        print("  1. Execute: python gerar_dataset.py")
        print("  2. Use o script colab_finetuning.py no Google Colab")
        print("  3. Baixe o modelo treinado para a pasta model/")
        return 0
    
    # Testar cada modelo
    print("\n" + "=" * 70)
    print("🔬 TESTANDO MODELOS")
    print("=" * 70)
    
    resultados = {}
    
    for caminho, tamanho in modelos:
        sucesso, modelo = testar_carregamento(caminho)
        if sucesso and modelo:
            sucesso_pred = testar_predicao(modelo, caminho)
            resultados[caminho] = sucesso and sucesso_pred
        else:
            resultados[caminho] = False
    
    # Testar engine
    testar_engine_com_modelos()
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    
    for caminho, sucesso in resultados.items():
        simbolo = "✅" if sucesso else "❌"
        nome = os.path.basename(caminho)
        print(f"{simbolo} {nome}")
    
    print()
    
    if all(resultados.values()):
        print("🎉 Todos os modelos estão funcionando!")
        return 0
    elif any(resultados.values()):
        print("⚠️  Alguns modelos estão funcionando")
        return 0
    else:
        print("❌ Nenhum modelo está funcionando")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
