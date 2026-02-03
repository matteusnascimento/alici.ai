"""
train_llm.py
Script profissional para treinar um modelo LLM com seus datasets

Usa PyTorch + Hugging Face Transformers
Otimizado para GPU (CUDA)
"""

import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TextDataset,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
from logger import get_logger

logger = get_logger("train")

# Configurações
MODEL_NAME = "gpt2"  # Modelo base (gpt2, distilgpt2, etc)
DATASET_PATH = "datasets_processado/dataset_final.txt"
OUTPUT_DIR = "modelo_treinado"
BATCH_SIZE = 8
EPOCHS = 3
LEARNING_RATE = 5e-5

os.makedirs(OUTPUT_DIR, exist_ok=True)


def verificar_gpu():
    """Verifica se GPU está disponível"""
    logger.info("🔍 Verificando hardware...")
    
    if torch.cuda.is_available():
        logger.info(f"✅ GPU disponível: {torch.cuda.get_device_name(0)}")
        logger.info(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        return True
    else:
        logger.warning("⚠️ GPU não disponível, usando CPU (MUITO mais lento)")
        return False


def carregar_dataset():
    """Carrega dataset para treino"""
    logger.info(f"📂 Carregando dataset: {DATASET_PATH}")
    
    if not os.path.exists(DATASET_PATH):
        logger.error(f"❌ Arquivo não encontrado: {DATASET_PATH}")
        logger.error("   Execute primeiro: python download_datasets.py")
        return None
    
    # Verificar tamanho
    tamanho_mb = os.path.getsize(DATASET_PATH) / (1024 * 1024)
    logger.info(f"   Tamanho: {tamanho_mb:.2f} MB")
    
    return DATASET_PATH


def main():
    """Pipeline completo de treino"""
    
    logger.info("\n" + "=" * 70)
    logger.info("🚀 INICIANDO TREINO DE LLM")
    logger.info("=" * 70 + "\n")
    
    try:
        # 1. Verificar GPU
        gpu_disponivel = verificar_gpu()
        device = "cuda" if gpu_disponivel else "cpu"
        
        # 2. Carregar dataset
        dataset_path = carregar_dataset()
        if not dataset_path:
            return False
        
        # 3. Carregar tokenizer e modelo
        logger.info(f"\n🔤 Carregando tokenizer e modelo: {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        
        logger.info(f"   Tamanho do modelo: {sum(p.numel() for p in model.parameters())/1e6:.1f}M parâmetros")
        
        # 4. Preparar dataset
        logger.info(f"\n📊 Preparando dataset para treino...")
        train_dataset = TextDataset(
            tokenizer=tokenizer,
            file_path=dataset_path,
            block_size=128  # Contexto de 128 tokens
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False  # Causal LM, não MLM
        )
        
        logger.info(f"   Exemplos de treino: {len(train_dataset):,}")
        
        # 5. Configurar treino
        logger.info(f"\n⚙️  Configurando treino...")
        training_args = TrainingArguments(
            output_dir=OUTPUT_DIR,
            overwrite_output_dir=True,
            num_train_epochs=EPOCHS,
            per_device_train_batch_size=BATCH_SIZE,
            save_steps=500,
            save_total_limit=3,
            logging_steps=100,
            learning_rate=LEARNING_RATE,
            warmup_steps=500,
            weight_decay=0.01,
            fp16=gpu_disponivel,  # Mixed precision em GPU
            dataloader_pin_memory=True,
            optim="adamw_torch",
            max_grad_norm=1.0,
        )
        
        logger.info(f"   Batch size: {BATCH_SIZE}")
        logger.info(f"   Epochs: {EPOCHS}")
        logger.info(f"   Learning rate: {LEARNING_RATE}")
        logger.info(f"   Checkpoint dir: {OUTPUT_DIR}")
        
        # 6. Iniciar treino
        logger.info(f"\n🧠 Iniciando treino (isto pode levar horas/dias)...\n")
        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=train_dataset,
        )
        
        trainer.train()
        
        # 7. Salvar modelo final
        logger.info(f"\n💾 Salvando modelo treinado...")
        model.save_pretrained(os.path.join(OUTPUT_DIR, "final_model"))
        tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "final_model"))
        
        logger.info("=" * 70)
        logger.info("✅ TREINO CONCLUÍDO!")
        logger.info("=" * 70)
        logger.info(f"\n📁 Modelo salvo em: {os.path.join(OUTPUT_DIR, 'final_model')}")
        logger.info(f"\n🚀 Para usar seu modelo:\n")
        logger.info(f"   from transformers import AutoModelForCausalLM, AutoTokenizer")
        logger.info(f"   model = AutoModelForCausalLM.from_pretrained('{os.path.join(OUTPUT_DIR, 'final_model')}')")
        logger.info(f"   tokenizer = AutoTokenizer.from_pretrained('{os.path.join(OUTPUT_DIR, 'final_model')}')")
        logger.info(f"\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante treino: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
