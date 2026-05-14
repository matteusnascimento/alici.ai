# Ficha Técnica — Modelo ALICI CPU Simple

## 1) Identificação
- **Nome do modelo:** ALICI CPU Simple
- **Tipo:** Classificação de intenção textual (NLP)
- **Framework:** TensorFlow / Keras
- **Formato do artefato principal:** `.keras`
- **Objetivo:** Identificar intenção de mensagens curtas em português para resposta conversacional.

## 2) Versão e Origem
- **Dataset base:** `intents.json`
- **Amostras de treino:** `22`
- **Número de classes:** `5`
- **Classes:** `agradecimento`, `ajuda`, `criador`, `despedida`, `saudacao`
- **Data de referência:** 2026-02-22

## 3) Arquitetura do Modelo
Arquitetura sequencial (Keras):
1. `Embedding(input_dim=10000, output_dim=128, input_length=40)`
2. `Bidirectional(LSTM(64))`
3. `Dropout(0.3)`
4. `Dense(256, activation="relu")`
5. `Dropout(0.3)`
6. `Dense(num_classes=5, activation="softmax")`

## 4) Pré-processamento de Entrada
- Normalização: `lowercase` + trim de espaços.
- Tokenização: `Tokenizer(num_words=10000, oov_token="<OOV>")`
- Padding/truncamento: comprimento fixo `max_len=40` (`post`).
- Codificação de rótulos: `LabelEncoder`.

## 5) Hiperparâmetros de Treino
- **Épocas solicitadas:** `30`
- **Épocas treinadas:** `10` (parada antecipada)
- **Batch size:** `16`
- **Learning rate:** `0.001`
- **Loss:** `sparse_categorical_crossentropy`
- **Otimizador:** `Adam`
- **Métrica:** `accuracy`
- **Early stopping:** monitor `val_loss`, `patience=5`, `restore_best_weights=True`

## 6) Detalhamento dos Dados de Treinamento
- **Total de amostras:** `22`
- **Split treino/validação:** `80/20`
- **Amostras de treino:** `17`
- **Amostras de validação:** `5`
- **Shape de entrada (treino):** `x_train = (17, 40)`
- **Shape de entrada (validação):** `x_val = (5, 40)`
- **Shape de rótulos (treino):** `y_train = (17,)`
- **Shape de rótulos (validação):** `y_val = (5,)`

Distribuição de classes no dataset (`intents.json`):
- `saudacao`: 6 padrões
- `despedida`: 5 padrões
- `criador`: 3 padrões
- `agradecimento`: 4 padrões
- `ajuda`: 4 padrões

## 7) Parâmetros do Modelo
Contagem de parâmetros treináveis por camada:
- `Embedding(10000 x 128)`: `1.280.000`
- `Bidirectional(LSTM(64))`: `98.816`
- `Dense(128 -> 256)`: `33.024`
- `Dense(256 -> 5)`: `1.285`

**Total de parâmetros treináveis:** `1.413.125`

## 8) Métricas de Validação
- **Val loss:** `1.6031`
- **Val accuracy:** `0.2000`

> Observação: com dataset pequeno (22 amostras), a acurácia de validação tende a oscilar e não representa desempenho robusto em produção sem expansão de dados.

## 9) Artefatos Gerados
Diretório local de saída:
- `artifacts/alici_cpu_simple/alici_cpu_simple.keras`
- `artifacts/alici_cpu_simple/tokenizer.pkl`
- `artifacts/alici_cpu_simple/label_encoder.pkl`
- `artifacts/alici_cpu_simple/metadata.json`
- `artifacts/alici_cpu_simple/train_val_arrays.npz`
- `artifacts/alici_cpu_simple/training_dataset_full.json`

## 10) Armazenamento em Nuvem (Cloudflare R2)
Prefixo padrão no bucket:
- `models/alici_cpu_simple/`

Objetos esperados no R2:
- `models/alici_cpu_simple/alici_cpu_simple.keras`
- `models/alici_cpu_simple/tokenizer.pkl`
- `models/alici_cpu_simple/label_encoder.pkl`
- `models/alici_cpu_simple/metadata.json`
- `models/alici_cpu_simple/train_val_arrays.npz`
- `models/alici_cpu_simple/training_dataset_full.json`

## 11) Uso na API (Execução em Nuvem)
A API utiliza o serviço `alici_api/services/text_model_r2.py`, com fluxo:
1. Baixa artefatos do R2 para cache local temporário.
2. Carrega modelo/tokenizer/label encoder.
3. Faz inferência por intenção e retorna `tag`, `confidence` e resposta associada.

Variáveis de ambiente obrigatórias para carga do modelo via R2:
- `ALICI_R2_ACCOUNT_ID`
- `ALICI_R2_ACCESS_KEY`
- `ALICI_R2_SECRET_KEY`
- `ALICI_R2_BUCKET`
- `ALICI_R2_MODEL_PREFIX`

Variáveis úteis:
- `ALICI_R2_ENDPOINT` (opcional, default via account id)
- `ALICI_MODEL_CACHE_DIR` (default: `/tmp/alici_cpu_simple_r2_cache`)
- `ALICI_INTENT_MIN_CONFIDENCE` (default: `0.55`)

## 12) Limitações e Recomendações
- Modelo treinado com base muito pequena; recomendado ampliar dataset para melhorar generalização.
- Incluir avaliação com matriz de confusão e F1 por classe em próximos ciclos.
- Versionar modelo por tag de release (ex.: `models/alici_cpu_simple/v1/`).
- Evitar credenciais hardcoded; usar apenas variáveis de ambiente em produção.

## 13) Status Atual
- Upload no R2: **confirmado**.
- Carregamento pela API via R2: **implementado**.
- Pronto para deploy cloud com variáveis de ambiente configuradas.

## 14) Comparativo de Versões

| Métrica | v1 (atual) | v2 (próxima) |
|---|---:|---:|
| Data | 2026-02-22 | - |
| Dataset | intents.json | - |
| Amostras totais | 22 | - |
| Classes | 5 | - |
| Épocas treinadas | 10 | - |
| Batch size | 16 | - |
| Learning rate | 0.001 | - |
| Parâmetros treináveis | 1.413.125 | - |
| Val loss | 1.6031 | - |
| Val accuracy | 0.2000 | - |
| Prefixo no R2 | models/alici_cpu_simple/ | - |

Critério sugerido para promover v2:
- `val_accuracy` superior à v1 e estável.
- Avaliação por classe (F1 e recall) sem regressão crítica.
- Teste funcional no endpoint de chat aprovado em ambiente cloud.
