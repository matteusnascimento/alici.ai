"""
⚡ API FASTAPI - PRODUÇÃO RENDER
Servidor de inferência e status da ALICI™
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
import sys
from datetime import datetime
import uvicorn
from typing import List, Dict, Optional
import json
import time
from io import BytesIO
from PIL import Image
import librosa

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.neon import db


# ⚙️ CONFIGURAÇÃO
app = FastAPI(
    title="🤖 ALICI™ Core API",
    description="API de inferência multimodal para ALICI",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Cache do modelo
modelo = None
tempo_carregamento = None


def carregar_modelo():
    """Carrega o modelo na inicialização"""
    global modelo, tempo_carregamento
    
    print("📦 Carregando modelo ALICI...")
    inicio = time.time()
    
    try:
        # Tentar carregar do arquivo
        if os.path.exists("alici_core.h5"):
            modelo = keras.models.load_model("alici_core.h5")
            print("✅ Modelo carregado de alici_core.h5")
        else:
            print("⚠️ Arquivo alici_core.h5 não encontrado. Usando modelo novo.")
            from models.multimodal_model import criar_modelo_multimodal
            modelo = criar_modelo_multimodal()
            modelo.compile(
                optimizer=keras.optimizers.Adam(learning_rate=1e-4),
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
        
        tempo_carregamento = time.time() - inicio
        print(f"✅ Modelo pronto em {tempo_carregamento:.2f}s")
        return True
    
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    carregar_modelo()
    
    # Criar tabelas no Neon
    if db.conectar():
        print("✅ Conexão com Neon estabelecida")
        db.criar_tabelas()
    else:
        print("⚠️ Não foi possível conectar ao Neon")


# 📊 ROTAS

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint - Status da API"""
    return {
        "status": "🟢 Online",
        "app": "🤖 ALICI™ Core API",
        "versao": "1.0.0",
        "modelo_carregado": modelo is not None,
        "tempo_carregamento_ms": tempo_carregamento * 1000 if tempo_carregamento else None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Status"])
async def health():
    """Health check para Render"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status", tags=["Status"])
async def status():
    """Status detalhado da API"""
    if modelo is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado")
    
    return {
        "status": "🟢 Online",
        "modelo": {
            "nome": "AliciMultimodal",
            "parametros": int(modelo.count_params()),
            "input_shapes": {
                "imagem": [32, 32, 3],
                "texto": [50],
                "audio": [13]
            },
            "output_classes": 256
        },
        "banco_dados": {
            "conectado": db.conectar() is not None,
            "tabelas": ["treino_logs", "modelos", "predicoes", "usuarios"]
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict", tags=["Inferência"])
async def predict(
    image: Optional[UploadFile] = File(None),
    text: Optional[str] = None,
    audio: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None
):
    """
    Faz predição multimodal
    
    Aceita:
    - image: arquivo PNG/JPG (32x32)
    - text: string (será tokenizada)
    - audio: arquivo WAV (será extraído MFCC)
    """
    
    if modelo is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado")
    
    try:
        inicio = time.time()
        
        # 1️⃣ Processar imagem
        img_array = np.zeros((1, 32, 32, 3))
        if image:
            img_data = await image.read()
            img = Image.open(BytesIO(img_data))
            img = img.resize((32, 32))
            img_array = np.array(img) / 255.0
            if len(img_array.shape) == 2:  # Grayscale
                img_array = np.stack([img_array] * 3, axis=-1)
            img_array = np.expand_dims(img_array, 0)
        
        # 2️⃣ Processar texto
        text_array = np.zeros((1, 50), dtype=np.int32)
        if text:
            # Tokenização simples (usar tokenizer real em produção)
            tokens = [hash(c) % 5000 for c in text[:50]]
            tokens += [0] * (50 - len(tokens))
            text_array = np.array([tokens[:50]], dtype=np.int32)
        
        # 3️⃣ Processar áudio
        audio_array = np.zeros((1, 13))
        if audio:
            audio_data = await audio.read()
            audio_path = "/tmp/temp_audio.wav"
            with open(audio_path, "wb") as f:
                f.write(audio_data)
            
            y, sr = librosa.load(audio_path, sr=None)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1)
            audio_array = np.expand_dims(mfcc_mean, 0)
            
            os.remove(audio_path)
        
        # 4️⃣ Fazer predição
        prediction = modelo.predict([img_array, text_array, audio_array], verbose=0)
        
        tempo_ms = int((time.time() - inicio) * 1000)
        
        # 5️⃣ Log no Neon
        if background_tasks:
            background_tasks.add_task(
                db.log_predicao,
                modelo_id=1,
                input_type="multimodal",
                output={"prediction": prediction[0].tolist()},
                tempo_ms=tempo_ms
            )
        
        return {
            "predication": {
                "class": int(np.argmax(prediction[0])),
                "confidence": float(np.max(prediction[0])),
                "probabilities": prediction[0].tolist()
            },
            "tempo_ms": tempo_ms,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na predição: {str(e)}")


@app.get("/logs/treino", tags=["Logs"])
async def get_training_logs(modelo: Optional[str] = None, limit: int = 100):
    """Retorna logs de treinamento do Neon"""
    try:
        logs = db.obter_logs_treino(modelo=modelo, limit=limit)
        return {
            "logs": logs,
            "total": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter logs: {str(e)}")


@app.get("/modelos", tags=["Modelos"])
async def get_modelos():
    """Retorna lista de modelos registrados"""
    try:
        modelos = db.obter_modelos()
        return {
            "modelos": modelos,
            "total": len(modelos),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter modelos: {str(e)}")


@app.post("/treinar", tags=["Treino"])
async def iniciar_treinamento(background_tasks: BackgroundTasks):
    """
    Inicia treinamento em background
    
    ⚠️ Apenas para ambiente de desenvolvimento
    Em produção, usar Colab ou notebook separado
    """
    
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(
            status_code=403,
            detail="Treinamento desabilitado em produção"
        )
    
    background_tasks.add_task(executar_treinamento)
    
    return {
        "status": "Treinamento iniciado em background",
        "timestamp": datetime.now().isoformat()
    }


async def executar_treinamento():
    """Executa treinamento (chamado em background)"""
    print("🚀 Iniciando treinamento em background...")
    # Aqui você chamaria o trainer
    # from training.trainer import TrainerMultimodal


@app.post("/reload-model", tags=["Admin"])
async def reload_model():
    """Recarrega o modelo (útil após novo treinamento)"""
    global modelo
    
    try:
        modelo = keras.models.load_model("alici_core.h5")
        return {
            "status": "✅ Modelo recarregado",
            "parametros": int(modelo.count_params()),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recarregar: {str(e)}")


@app.get("/docs", tags=["Info"])
async def docs():
    """Documentação da API"""
    return {
        "titulo": "🤖 ALICI™ Core API",
        "versao": "1.0.0",
        "endpoints": {
            "GET /": "Status da API",
            "GET /health": "Health check",
            "GET /status": "Status detalhado",
            "POST /predict": "Fazer predição multimodal",
            "GET /logs/treino": "Obter logs de treinamento",
            "GET /modelos": "Listar modelos",
            "POST /treinar": "Iniciar treinamento (dev only)",
            "POST /reload-model": "Recarregar modelo"
        },
        "documentacao_interativa": "/docs"
    }


# ❌ Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print(f"\n🚀 Iniciando ALICI™ Core API na porta {port}...\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
