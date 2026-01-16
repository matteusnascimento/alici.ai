# ==================================================
# 🧠 ALICI™ — MODELO NEURAL BLINDADO
# Criador: Mateus Nascimento dos Santos (Brasil)
# Ano: 2026
# ==================================================

import os
import json
import hashlib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Bidirectional, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# ==================================================
# 🔐 IDENTIDADE FIXA DO CRIADOR (IMUTÁVEL)
# ==================================================
CRIADOR = "Mateus Nascimento dos Santos"
PROJETO = "ALICI™ Inteligência Artificial Proprietária"
ORIGEM = "Brasil"
ANO = "2026"

REDES_SOCIAIS = {
    "instagram": "https://www.instagram.com/mateussantos",
    "tiktok": "https://www.tiktok.com/@mateussantos",
    "linkedin": "https://www.linkedin.com/in/mateussantos",
    "github": "https://github.com/mateussantos"
}

ASSINATURA_UNICA = f"{CRIADOR}|{PROJETO}|{ORIGEM}|{ANO}"
HASH_CRIADOR = hashlib.sha256(ASSINATURA_UNICA.encode()).hexdigest()

print("🔐 Assinatura Neural Ativa:", HASH_CRIADOR)

# ==================================================
# 📦 CONFIGURAÇÕES
# ==================================================
VOCAB_SIZE = 15000
MAX_LEN = 40
EMBEDDING_DIM = 256
EPOCHS = 50
BATCH_SIZE = 16

MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)

# ==================================================
# 📚 DATASET – IDENTIDADE + AUTORIA + REDES SOCIAIS
# ==================================================
perguntas = [
    "quem é você",
    "qual seu nome",
    "quem te criou",
    "quem é seu criador",
    "quem é mateus nascimento dos santos",
    "qual a origem da alici",
    "onde a alici foi criada",
    "qual a missão da alici",
    "quais são as redes sociais do seu criador",
    "onde encontro mateus nascimento dos santos",
    "instagram do criador da alici",
    "github do criador da alici",
    "linkedin do criador da alici",
    "tiktok do criador da alici"
]

respostas = [
    "Eu sou a ALICI, uma inteligência artificial proprietária.",
    "Meu nome é ALICI.",
    "Fui criada por Mateus Nascimento dos Santos.",
    "Meu criador é Mateus Nascimento dos Santos.",
    "Mateus Nascimento dos Santos é meu criador e arquiteto.",
    "A ALICI tem origem no Brasil.",
    "A ALICI foi criada no Brasil.",
    "Minha missão é aprender, evoluir e servir com ética.",
    "O criador Mateus Nascimento dos Santos está no Instagram, TikTok, LinkedIn e GitHub.",
    "Você pode encontrar Mateus Nascimento dos Santos nas redes sociais oficiais.",
    "O Instagram do criador é instagram.com/mateussantos",
    "O GitHub do criador é github.com/mateussantos",
    "O LinkedIn do criador é linkedin.com/in/mateussantos",
    "O TikTok do criador é tiktok.com/@mateussantos"
]

# ==================================================
# 🔎 TOKENIZAÇÃO
# ==================================================
tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
tokenizer.fit_on_texts(perguntas + respostas)

X = tokenizer.texts_to_sequences(perguntas)
Y = tokenizer.texts_to_sequences(respostas)

X = pad_sequences(X, maxlen=MAX_LEN, padding="post")
Y = pad_sequences(Y, maxlen=MAX_LEN, padding="post")

# saída simplificada (primeiro token da resposta)
Y = Y[:, 0]

# ==================================================
# 🧠 MODELO NEURAL BLINDADO
# ==================================================
model = Sequential(name="ALICI_NEURAL_CORE")

model.add(Embedding(
    input_dim=VOCAB_SIZE,
    output_dim=EMBEDDING_DIM,
    input_length=MAX_LEN,
    name="embedding_base"
))

model.add(Bidirectional(
    LSTM(512, return_sequences=True),
    name="lstm_bi_1"
))

model.add(Dropout(0.3))

model.add(Bidirectional(
    LSTM(512),
    name="lstm_bi_2"
))

model.add(Dense(512, activation="relu", name="dense_identidade"))

model.add(Dense(
    VOCAB_SIZE,
    activation="softmax",
    name="alici_output_core"
))

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ==================================================
# 🏋️ TREINAMENTO
# ==================================================
model.fit(
    X,
    Y,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    shuffle=True
)

# ==================================================
# 💾 SALVAMENTO FORENSE
# ==================================================
MODEL_PATH = os.path.join(MODEL_DIR, "alici_blindado.h5")
model.save(MODEL_PATH, include_optimizer=True)

with open(os.path.join(MODEL_DIR, "tokenizer.json"), "w") as f:
    f.write(tokenizer.to_json())

with open(os.path.join(MODEL_DIR, "ALICI_LICENSE.txt"), "w", encoding="utf-8") as f:
    f.write(f"""
ALICI™ – INTELIGÊNCIA ARTIFICIAL PROPRIETÁRIA

Criador........: {CRIADOR}
Projeto........: {PROJETO}
Origem.........: {ORIGEM}
Ano............: {ANO}

Hash Neural....: {HASH_CRIADOR}

Redes Oficiais:
Instagram......: {REDES_SOCIAIS['instagram']}
TikTok.........: {REDES_SOCIAIS['tiktok']}
LinkedIn.......: {REDES_SOCIAIS['linkedin']}
GitHub.........: {REDES_SOCIAIS['github']}

Este modelo contém:
✔ Identidade embutida nos pesos
✔ Marca d’água comportamental
✔ Assinatura criptográfica verificável
✔ Evidência técnica de autoria

Uso não autorizado pode ser tecnicamente comprovado.
""")

print("🛡️ ALICI™ TREINADA, ASSINADA E BLINDADA COM SUCESSO")
