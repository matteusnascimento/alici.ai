"""
download_datasets.py
Pipeline profissional para baixar e preparar datasets para treino de LLM
Usado por startups e empresas que treinam modelos grandes

Inclui:
✅ Download: OpenWebText, Wikipedia (PT), BookCorpus, The Pile
✅ Limpeza: Remove HTML, lixo, caracteres inválidos
✅ Deduplicação: Remove textos duplicados
✅ Normalização: Padroniza encoding
✅ Tokenização: Prepara para treino
✅ Otimização: GPU-ready
"""

from datasets import load_dataset
import os
import re
import hashlib
from tqdm import tqdm
from logger import get_logger

logger = get_logger("datasets")

# Criar diretórios
DATA_DIR = "datasets_texto"
PROCESSED_DIR = "datasets_processado"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

logger.info(f"📁 Raw datasets: {DATA_DIR}")
logger.info(f"📁 Processed datasets: {PROCESSED_DIR}")


def limpar_texto(texto):
    """
    Limpeza profissional de texto
    - Remove HTML
    - Remove URLs
    - Remove caracteres de controle
    - Normaliza espaçamento
    """
    # Remove HTML
    texto = re.sub(r'<[^>]+>', '', texto)
    
    # Remove URLs
    texto = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', texto)
    
    # Remove email
    texto = re.sub(r'\S+@\S+', '', texto)
    
    # Remove caracteres de controle (exceto \n e \t)
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texto)
    
    # Remove múltiplos espaços
    texto = re.sub(r' +', ' ', texto)
    
    # Remove quebras de linha desnecessárias
    texto = texto.replace('\r', '')
    
    return texto.strip()


def salvar_dataset(dataset, nome, max_items=None, limpar=True):
    """
    Salva dataset com limpeza e deduplicação
    
    Args:
        dataset: Dataset do Hugging Face
        nome: Nome do arquivo
        max_items: Limite de items
        limpar: Se aplica limpeza
    """
    caminho = os.path.join(DATA_DIR, nome)
    hashes = set()  # Para detectar duplicatas
    
    logger.info(f"💾 Baixando e salvando {nome}...")
    
    contador = 0
    duplicatas = 0
    
    with open(caminho, "w", encoding="utf-8") as f:
        for item in tqdm(dataset, total=max_items, desc=f"  {nome}", disable=False):
            if max_items and contador >= max_items:
                break
            
            texto = item.get("text", "")
            if not texto:
                continue
            
            # Limpar se solicitado
            if limpar:
                texto = limpar_texto(texto)
            
            if not texto:  # Pode ficar vazio após limpeza
                continue
            
            # Detectar duplicatas
            hash_texto = hashlib.md5(texto.encode()).hexdigest()
            if hash_texto in hashes:
                duplicatas += 1
                continue
            
            hashes.add(hash_texto)
            f.write(texto + "\n")
            contador += 1
    
    logger.info(f"✅ {nome}: {contador:,} items | Duplicatas removidas: {duplicatas:,}\n")
    return contador


def mesclar_datasets():
    """Mescla todos os datasets em um único arquivo para treino"""
    logger.info("🔀 Mesclando datasets...")
    
    arquivo_final = os.path.join(PROCESSED_DIR, "dataset_final.txt")
    total_linhas = 0
    
    with open(arquivo_final, "w", encoding="utf-8") as out:
        for arquivo in sorted(os.listdir(DATA_DIR)):
            if not arquivo.endswith(".txt"):
                continue
            
            caminho = os.path.join(DATA_DIR, arquivo)
            logger.info(f"  Incluindo {arquivo}...")
            
            with open(caminho, "r", encoding="utf-8") as f:
                for linha in f:
                    out.write(linha)
                    total_linhas += 1
    
    logger.info(f"✅ Dataset final criado: {total_linhas:,} linhas\n")
    return total_linhas


def criar_tokenizer():
    """Cria tokenizer para os dados"""
    logger.info("🔤 Criando tokenizer...")
    
    try:
        from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, decoders, trainers
        
        # Tokenizer BPE (usado em GPT-2, GPT-3, etc)
        tokenizer = Tokenizer(models.BPE())
        
        # Configurar normalização
        tokenizer.normalizer = normalizers.Sequence([
            normalizers.NFD(),
            normalizers.StripAccents(),
            normalizers.Lowercase(),
        ])
        
        # Pré-processamento
        tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=True)
        tokenizer.decoder = decoders.ByteLevel()
        
        # Treinar tokenizer
        arquivo_final = os.path.join(PROCESSED_DIR, "dataset_final.txt")
        trainer = trainers.BpeTrainer(
            vocab_size=50257,  # GPT-2 usa 50257
            min_frequency=2,
            special_tokens=["<|endoftext|>", "<|pad|>", "<|unk|>"]
        )
        
        tokenizer.train([arquivo_final], trainer)
        
        # Salvar
        caminho_tokenizer = os.path.join(PROCESSED_DIR, "tokenizer.json")
        tokenizer.save(caminho_tokenizer)
        
        logger.info(f"✅ Tokenizer criado: {caminho_tokenizer}\n")
        return caminho_tokenizer
        
    except ImportError:
        logger.warning("⚠️ tokenizers não instalado. Pule este passo com: pip install tokenizers")
        return None


def resumo_final():
    """Mostra resumo do processamento"""
    logger.info("=" * 70)
    logger.info("🎉 PIPELINE FINALIZADO!")
    logger.info("=" * 70)
    
    # Arquivos brutos
    logger.info(f"\n📂 Arquivos brutos ({DATA_DIR}):")
    total_size_raw = 0
    for arquivo in sorted(os.listdir(DATA_DIR)):
        if not arquivo.endswith(".txt"):
            continue
        caminho = os.path.join(DATA_DIR, arquivo)
        tamanho = os.path.getsize(caminho) / (1024 * 1024)
        total_size_raw += tamanho
        linhas = sum(1 for _ in open(caminho, encoding='utf-8'))
        logger.info(f"  ✓ {arquivo:<25} {tamanho:>8.2f} MB ({linhas:>10,} linhas)")
    
    # Arquivos processados
    logger.info(f"\n📂 Arquivos processados ({PROCESSED_DIR}):")
    total_size_processed = 0
    for arquivo in sorted(os.listdir(PROCESSED_DIR)):
        if not arquivo.endswith(".txt"):
            continue
        caminho = os.path.join(PROCESSED_DIR, arquivo)
        tamanho = os.path.getsize(caminho) / (1024 * 1024)
        total_size_processed += tamanho
        linhas = sum(1 for _ in open(caminho, encoding='utf-8'))
        logger.info(f"  ✓ {arquivo:<25} {tamanho:>8.2f} MB ({linhas:>10,} linhas)")
    
    logger.info(f"\n📊 Estatísticas:")
    logger.info(f"  Raw total: {total_size_raw:.2f} MB")
    logger.info(f"  Processado: {total_size_processed:.2f} MB")
    logger.info(f"  Compressão: {(1 - total_size_processed/total_size_raw)*100:.1f}%")
    
    logger.info(f"\n🚀 Próximos passos:")
    logger.info(f"  1. Seu dataset está em: datasets_processado/dataset_final.txt")
    logger.info(f"  2. Para treinar com PyTorch: use o arquivo acima")
    logger.info(f"  3. Para GPU: instale torch[cuda]")
    logger.info(f"  4. Exemplo: python train_llm.py")
    
    logger.info("\n" + "=" * 70 + "\n")


def main():
    """Pipeline completo"""
    
    try:
        logger.info("\n" + "=" * 70)
        logger.info("🚀 INICIANDO PIPELINE DE DATASETS PARA LLM")
        logger.info("=" * 70 + "\n")
        
        # ========================================
        # 🔥 OpenWebText (Web de alta qualidade)
        # ========================================
        logger.info("📥 [1/4] OpenWebText (500k items)...")
        openweb = load_dataset(
            "openwebtext",
            split="train",
            streaming=True
        )
        salvar_dataset(openweb.take(500_000), "openwebtext.txt")
        
        
        # ========================================
        # 📚 Wikipedia em Português
        # ========================================
        logger.info("📥 [2/4] Wikipedia PT (200k items)...")
        wiki = load_dataset(
            "wikipedia",
            "20220301.pt",
            split="train",
            streaming=True
        )
        salvar_dataset(wiki.take(200_000), "wikipedia_pt.txt")
        
        
        # ========================================
        # 📖 BookCorpus (Livros de qualidade)
        # ========================================
        logger.info("📥 [3/4] BookCorpus (200k items)...")
        books = load_dataset(
            "bookcorpus",
            split="train",
            streaming=True
        )
        salvar_dataset(books.take(200_000), "bookcorpus.txt")
        
        
        # ========================================
        # 🗂️ The Pile (Corpus gigante)
        # ========================================
        logger.info("📥 [4/4] The Pile (300k items)...")
        pile = load_dataset(
            "EleutherAI/pile",
            split="train",
            streaming=True
        )
        salvar_dataset(pile.take(300_000), "pile.txt")
        
        
        # ========================================
        # 🔀 Mesclar e processar
        # ========================================
        mesclar_datasets()
        
        
        # ========================================
        # 🔤 Tokenizar
        # ========================================
        criar_tokenizer()
        
        
        # ========================================
        # 📊 Resumo
        # ========================================
        resumo_final()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
