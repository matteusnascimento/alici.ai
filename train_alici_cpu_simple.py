"""
ALICI - Treinamento simples para CPU

Objetivo:
- Classificação de intenção com baixo consumo de RAM
- Execução estável em CPU (local ou Colab sem GPU)
"""

from __future__ import annotations

import argparse
import json
import os
import pickle
import random
import re
from pathlib import Path

import boto3
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Bidirectional, Dense, Dropout, Embedding, LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

try:
    from datasets import load_dataset

    HF_DATASETS_AVAILABLE = True
except Exception:
    HF_DATASETS_AVAILABLE = False

try:
    from langdetect import detect

    LANGDETECT_AVAILABLE = True
except Exception:
    LANGDETECT_AVAILABLE = False


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def load_intents(dataset_path: Path) -> tuple[list[str], list[str]]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    sentences: list[str] = []
    labels: list[str] = []

    for intent in data.get("intents", []):
        tag = intent.get("tag")
        patterns = intent.get("patterns", [])
        if not tag:
            continue
        for pattern in patterns:
            text = " ".join(str(pattern).strip().lower().split())
            if text:
                sentences.append(text)
                labels.append(tag)

    if len(sentences) < 10:
        raise ValueError("Poucos dados para treinar. Use pelo menos 10 frases.")
    if len(set(labels)) < 2:
        raise ValueError("É necessário pelo menos 2 intenções diferentes.")

    return sentences, labels


def load_intents_with_tags(dataset_path: Path) -> tuple[dict[str, list[str]], list[str], list[str]]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    tag_to_patterns: dict[str, list[str]] = {}
    sentences: list[str] = []
    labels: list[str] = []

    for intent in data.get("intents", []):
        tag = intent.get("tag")
        patterns = intent.get("patterns", [])
        if not tag:
            continue

        cleaned_patterns: list[str] = []
        for pattern in patterns:
            text = " ".join(str(pattern).strip().lower().split())
            if text:
                cleaned_patterns.append(text)
                sentences.append(text)
                labels.append(tag)

        if cleaned_patterns:
            tag_to_patterns[tag] = cleaned_patterns

    if len(sentences) < 10:
        raise ValueError("Poucos dados para treinar. Use pelo menos 10 frases.")
    if len(set(labels)) < 2:
        raise ValueError("É necessário pelo menos 2 intenções diferentes.")

    return tag_to_patterns, sentences, labels


def _extract_keywords(patterns: list[str], min_len: int = 4) -> set[str]:
    keywords: set[str] = set()
    for pattern in patterns:
        tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", pattern.lower())
        for token in tokens:
            if len(token) >= min_len:
                keywords.add(token)
    return keywords


def looks_like_portuguese(text: str) -> bool:
    text_l = text.lower()

    if LANGDETECT_AVAILABLE:
        try:
            return detect(text_l) == "pt"
        except Exception:
            pass

    markers = {
        " você ",
        " para ",
        " com ",
        " não ",
        " que ",
        " uma ",
        " como ",
        " isso ",
        " estou ",
        " obrigado ",
        " olá ",
    }
    padded = f" {text_l} "
    score = sum(1 for marker in markers if marker in padded)
    has_pt_chars = any(ch in text_l for ch in "ãáàâéêíóôõúç")
    return score >= 2 or (score >= 1 and has_pt_chars)


def augment_with_fineweb(
    tag_to_patterns: dict[str, list[str]],
    base_sentences: list[str],
    base_labels: list[str],
    fineweb_repo: str,
    fineweb_split: str,
    fineweb_text_column: str,
    fineweb_max_samples: int,
    fineweb_max_per_tag: int,
    pt_only: bool,
    seed: int,
) -> tuple[list[str], list[str]]:
    if not HF_DATASETS_AVAILABLE:
        raise RuntimeError(
            "A biblioteca 'datasets' não está disponível. Instale com: pip install datasets"
        )

    print("🌐 Carregando FineWeb para augmentação...")
    ds = load_dataset(fineweb_repo, split=fineweb_split)
    ds = ds.shuffle(seed=seed)

    max_items = min(fineweb_max_samples, len(ds))
    counts = {tag: 0 for tag in tag_to_patterns}
    keywords_by_tag = {tag: _extract_keywords(patterns) for tag, patterns in tag_to_patterns.items()}

    sentences = list(base_sentences)
    labels = list(base_labels)

    for item in ds.select(range(max_items)):
        text = str(item.get(fineweb_text_column, "")).strip().lower()
        if len(text) < 15:
            continue

        if pt_only and not looks_like_portuguese(text):
            continue

        text_norm = " ".join(text.split())
        assigned_tag = None

        for tag, keywords in keywords_by_tag.items():
            if counts[tag] >= fineweb_max_per_tag:
                continue
            if not keywords:
                continue
            if any(keyword in text_norm for keyword in keywords):
                assigned_tag = tag
                break

        if assigned_tag is None:
            continue

        if len(text_norm) > 220:
            text_norm = text_norm[:220].rsplit(" ", 1)[0]

        sentences.append(text_norm)
        labels.append(assigned_tag)
        counts[assigned_tag] += 1

        if all(v >= fineweb_max_per_tag for v in counts.values()):
            break

    added = len(sentences) - len(base_sentences)
    print(f"✅ FineWeb adicionou {added} exemplos fracos ao treino")
    print("Distribuição FineWeb por tag:", counts)
    return sentences, labels


def build_cpu_model(vocab_size: int, max_len: int, num_classes: int, learning_rate: float) -> Sequential:
    model = Sequential(
        [
            Embedding(input_dim=vocab_size, output_dim=128, input_length=max_len),
            Bidirectional(LSTM(64)),
            Dropout(0.3),
            Dense(256, activation="relu"),
            Dropout(0.3),
            Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def save_training_data(
    output_dir: Path,
    sentences: list[str],
    labels: list[str],
    x_train: np.ndarray,
    x_val: np.ndarray,
    y_train: np.ndarray,
    y_val: np.ndarray,
) -> None:
    with (output_dir / "training_dataset_full.json").open("w", encoding="utf-8") as file:
        json.dump(
            {
                "samples": [{"text": text, "label": label} for text, label in zip(sentences, labels)],
                "total": len(sentences),
            },
            file,
            ensure_ascii=False,
            indent=2,
        )

    np.savez_compressed(
        output_dir / "train_val_arrays.npz",
        x_train=x_train,
        x_val=x_val,
        y_train=y_train,
        y_val=y_val,
    )


def upload_directory_to_r2(local_dir: Path, prefix: str) -> None:
    account_id = os.getenv("ALICI_R2_ACCOUNT_ID")
    access_key = os.getenv("ALICI_R2_ACCESS_KEY")
    secret_key = os.getenv("ALICI_R2_SECRET_KEY")
    bucket = os.getenv("ALICI_R2_BUCKET", "alici-lake")
    endpoint_url = os.getenv("ALICI_R2_ENDPOINT", f"https://{account_id}.r2.cloudflarestorage.com" if account_id else None)

    if not account_id or not access_key or not secret_key:
        raise RuntimeError(
            "Credenciais R2 ausentes. Defina ALICI_R2_ACCOUNT_ID, ALICI_R2_ACCESS_KEY e ALICI_R2_SECRET_KEY"
        )

    if not endpoint_url:
        raise RuntimeError("Endpoint R2 inválido. Defina ALICI_R2_ENDPOINT ou ALICI_R2_ACCOUNT_ID")

    s3 = boto3.client(
        service_name="s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )

    print(s3.list_objects_v2(Bucket=bucket))

    uploaded = 0
    for file_path in local_dir.rglob("*"):
        if file_path.is_file():
            key = f"{prefix}/{file_path.relative_to(local_dir).as_posix()}"
            s3.upload_file(str(file_path), bucket, key)
            uploaded += 1

    print(f"☁️ Upload Cloudflare R2 concluído: {uploaded} arquivos enviados")


def main() -> None:
    parser = argparse.ArgumentParser(description="Treino simples ALICI para CPU")
    parser.add_argument("--dataset", type=str, default="intents.json", help="Caminho para intents.json")
    parser.add_argument("--output-dir", type=str, default="artifacts/alici_cpu_simple", help="Pasta de saída")
    parser.add_argument("--epochs", type=int, default=30, help="Épocas")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size para CPU")
    parser.add_argument("--vocab-size", type=int, default=10000, help="Tamanho máximo do vocabulário")
    parser.add_argument("--max-len", type=int, default=40, help="Comprimento máximo da sequência")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--test-size", type=float, default=0.2, help="Percentual de validação")
    parser.add_argument("--seed", type=int, default=42, help="Semente global")
    parser.add_argument("--use-fineweb", action="store_true", help="Usa FineWeb para augmentação fraca")
    parser.add_argument("--fineweb-repo", type=str, default="HuggingFaceFW/fineweb", help="Repo FineWeb no Hugging Face")
    parser.add_argument("--fineweb-split", type=str, default="train", help="Split do FineWeb")
    parser.add_argument("--fineweb-text-column", type=str, default="text", help="Coluna de texto no FineWeb")
    parser.add_argument("--fineweb-max-samples", type=int, default=20000, help="Máximo de registros FineWeb a varrer")
    parser.add_argument("--fineweb-max-per-tag", type=int, default=300, help="Máximo de exemplos FineWeb por intenção")
    parser.add_argument("--fineweb-pt-only", action="store_true", help="Filtra apenas textos em português")
    parser.add_argument("--upload-r2", action="store_true", help="Faz upload dos artefatos e dados de treino para Cloudflare R2")
    parser.add_argument("--r2-prefix", type=str, default="models/alici_cpu_simple", help="Caminho/prefixo no bucket alici-lake")
    args = parser.parse_args()

    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")

    print("🚀 Iniciando treino CPU simples da ALICI")
    set_seed(args.seed)

    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tag_to_patterns, sentences, labels = load_intents_with_tags(dataset_path)

    if args.use_fineweb:
        sentences, labels = augment_with_fineweb(
            tag_to_patterns=tag_to_patterns,
            base_sentences=sentences,
            base_labels=labels,
            fineweb_repo=args.fineweb_repo,
            fineweb_split=args.fineweb_split,
            fineweb_text_column=args.fineweb_text_column,
            fineweb_max_samples=args.fineweb_max_samples,
            fineweb_max_per_tag=args.fineweb_max_per_tag,
            pt_only=args.fineweb_pt_only,
            seed=args.seed,
        )

    print(f"📊 Amostras: {len(sentences)} | Classes: {len(set(labels))}")

    tokenizer = Tokenizer(num_words=args.vocab_size, oov_token="<OOV>")
    tokenizer.fit_on_texts(sentences)

    sequences = tokenizer.texts_to_sequences(sentences)
    x = pad_sequences(sequences, maxlen=args.max_len, padding="post", truncating="post")

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)

    stratify = y if len(np.unique(y)) > 1 else None
    x_train, x_val, y_train, y_val = train_test_split(
        x,
        y,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=stratify,
    )

    model = build_cpu_model(
        vocab_size=args.vocab_size,
        max_len=args.max_len,
        num_classes=len(label_encoder.classes_),
        learning_rate=args.learning_rate,
    )
    model.summary()

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
    ]

    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    val_loss, val_acc = model.evaluate(x_val, y_val, verbose=0)
    print(f"✅ Validação final -> loss: {val_loss:.4f} | acc: {val_acc:.4f}")

    model.save(str(output_dir / "alici_cpu_simple.keras"))

    with (output_dir / "tokenizer.pkl").open("wb") as file:
        pickle.dump(tokenizer, file)

    with (output_dir / "label_encoder.pkl").open("wb") as file:
        pickle.dump(label_encoder, file)

    save_training_data(
        output_dir=output_dir,
        sentences=sentences,
        labels=labels,
        x_train=x_train,
        x_val=x_val,
        y_train=y_train,
        y_val=y_val,
    )

    metadata = {
        "model_name": "ALICI CPU Simple",
        "dataset": str(dataset_path),
        "num_samples": int(len(sentences)),
        "num_classes": int(len(label_encoder.classes_)),
        "classes": label_encoder.classes_.tolist(),
        "epochs_requested": int(args.epochs),
        "epochs_trained": int(len(history.history.get("loss", []))),
        "batch_size": int(args.batch_size),
        "vocab_size": int(args.vocab_size),
        "max_len": int(args.max_len),
        "learning_rate": float(args.learning_rate),
        "val_loss": float(val_loss),
        "val_accuracy": float(val_acc),
    }

    with (output_dir / "metadata.json").open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)

    if args.upload_r2:
        upload_directory_to_r2(local_dir=output_dir, prefix=args.r2_prefix)

    print(f"💾 Artefatos salvos em: {output_dir.resolve()}")
    print("🎯 Treinamento CPU concluído.")


if __name__ == "__main__":
    main()
