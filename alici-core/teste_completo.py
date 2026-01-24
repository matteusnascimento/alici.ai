"""
🧪 TESTE COMPLETO - ALICI CORE
Valida toda a arquitetura
"""

import os
import sys
import numpy as np
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Testa se todos os imports funcionam"""
    print("1️⃣ Testando imports...")
    
    try:
        from database.neon import db, NeonDB
        print("  ✅ database.neon")
    except Exception as e:
        print(f"  ❌ database.neon: {e}")
        return False
    
    try:
        from models.image_branch import image_branch, create_image_model
        print("  ✅ models.image_branch")
    except Exception as e:
        print(f"  ❌ models.image_branch: {e}")
        return False
    
    try:
        from models.text_branch import text_branch, create_text_model
        print("  ✅ models.text_branch")
    except Exception as e:
        print(f"  ❌ models.text_branch: {e}")
        return False
    
    try:
        from models.audio_branch import audio_branch, create_audio_model
        print("  ✅ models.audio_branch")
    except Exception as e:
        print(f"  ❌ models.audio_branch: {e}")
        return False
    
    try:
        from models.multimodal_model import criar_modelo_multimodal, contar_parametros
        print("  ✅ models.multimodal_model")
    except Exception as e:
        print(f"  ❌ models.multimodal_model: {e}")
        return False
    
    try:
        from training.trainer import TrainerMultimodal, gerar_dados_dummy
        print("  ✅ training.trainer")
    except Exception as e:
        print(f"  ❌ training.trainer: {e}")
        return False
    
    print("✅ Todos os imports OK\n")
    return True


def test_branches():
    """Testa os ramos separados"""
    print("2️⃣ Testando ramos separados...")
    
    try:
        from models.image_branch import create_image_model
        model = create_image_model()
        test_data = np.random.rand(1, 32, 32, 3)
        output = model.predict(test_data, verbose=0)
        assert output.shape == (1, 128), f"Shape esperado (1, 128), got {output.shape}"
        print(f"  ✅ Image Branch: {output.shape}")
    except Exception as e:
        print(f"  ❌ Image Branch: {e}")
        return False
    
    try:
        from models.text_branch import create_text_model
        model = create_text_model()
        test_data = np.random.randint(0, 5000, (1, 50))
        output = model.predict(test_data, verbose=0)
        assert output.shape == (1, 128), f"Shape esperado (1, 128), got {output.shape}"
        print(f"  ✅ Text Branch: {output.shape}")
    except Exception as e:
        print(f"  ❌ Text Branch: {e}")
        return False
    
    try:
        from models.audio_branch import create_audio_model
        model = create_audio_model()
        test_data = np.random.rand(1, 13)
        output = model.predict(test_data, verbose=0)
        assert output.shape == (1, 128), f"Shape esperado (1, 128), got {output.shape}"
        print(f"  ✅ Audio Branch: {output.shape}")
    except Exception as e:
        print(f"  ❌ Audio Branch: {e}")
        return False
    
    print("✅ Todos os ramos OK\n")
    return True


def test_multimodal():
    """Testa modelo multimodal"""
    print("3️⃣ Testando modelo multimodal...")
    
    try:
        from models.multimodal_model import criar_modelo_multimodal, contar_parametros
        
        modelo = criar_modelo_multimodal(num_classes=256)
        params = contar_parametros(modelo)
        
        print(f"  ✅ Modelo criado")
        print(f"  📊 Parâmetros: {params:,}")
        
        # Teste forward pass
        X_img = np.random.rand(1, 32, 32, 3)
        X_text = np.random.randint(0, 5000, (1, 50))
        X_audio = np.random.rand(1, 13)
        
        pred = modelo.predict([X_img, X_text, X_audio], verbose=0)
        assert pred.shape == (1, 256), f"Shape esperado (1, 256), got {pred.shape}"
        
        print(f"  ✅ Forward pass: {pred.shape}")
        
    except Exception as e:
        print(f"  ❌ Modelo multimodal: {e}")
        return False
    
    print("✅ Modelo multimodal OK\n")
    return True


def test_trainer():
    """Testa trainer"""
    print("4️⃣ Testando trainer...")
    
    try:
        from training.trainer import TrainerMultimodal, gerar_dados_dummy
        
        # Criar trainer
        trainer = TrainerMultimodal(model_name="test_alici", learning_rate=1e-4)
        print("  ✅ Trainer instanciado")
        
        # Compilar
        trainer.compilar_modelo(num_classes=256)
        print("  ✅ Modelo compilado")
        
        # Gerar dados
        X_train, y_train = gerar_dados_dummy(n_samples=10)
        X_val, y_val = gerar_dados_dummy(n_samples=5)
        print("  ✅ Dados gerados")
        
        # Treinar (1 época rápida)
        print("  🚀 Treinando 1 época...")
        trainer.treinar(
            X_train, y_train,
            X_val=X_val, y_val=y_val,
            epochs=1,
            batch_size=4,
            verbose=0
        )
        print("  ✅ Treinamento completo")
        
    except Exception as e:
        print(f"  ❌ Trainer: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ Trainer OK\n")
    return True


def test_database():
    """Testa conexão com banco de dados"""
    print("5️⃣ Testando banco de dados...")
    
    try:
        from database.neon import db
        
        # Testar conexão
        conn = db.conectar()
        if conn:
            print("  ✅ Conexão com Neon")
            conn.close()
        else:
            print("  ⚠️ Não conseguiu conectar ao Neon (verifique DATABASE_URL)")
            
    except Exception as e:
        print(f"  ⚠️ Banco de dados: {e}")
        print("  💡 Isso é normal se DATABASE_URL não estiver configurado")
    
    print()


def test_api():
    """Testa API FastAPI"""
    print("6️⃣ Testando API...")
    
    try:
        from api.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root
        response = client.get("/")
        assert response.status_code == 200
        print("  ✅ GET /")
        
        # Test health
        response = client.get("/health")
        assert response.status_code == 200
        print("  ✅ GET /health")
        
        # Test docs
        response = client.get("/docs")
        assert response.status_code == 200
        print("  ✅ GET /docs")
        
    except Exception as e:
        print(f"  ⚠️ API: {e}")
        print("  💡 Verifique se FastAPI está instalado")
    
    print()


def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🤖 ALICI CORE - TESTE COMPLETO")
    print("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Ramos", test_branches),
        ("Multimodal", test_multimodal),
        ("Trainer", test_trainer),
        ("Database", test_database),
        ("API", test_api),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {name} falhou: {e}\n")
            failed += 1
    
    # Resumo
    print("="*60)
    print(f"📊 RESULTADO: {passed} OK, {failed} FALHAS")
    print("="*60)
    
    if failed == 0:
        print("\n✅ TUDO FUNCIONANDO! Arquitetura está pronta para produção.\n")
    else:
        print(f"\n⚠️ {failed} teste(s) falharam. Verifique os logs acima.\n")


if __name__ == "__main__":
    # Configurar .env se existir
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    main()
