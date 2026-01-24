"""
🔧 TROUBLESHOOTING - ALICI CORE
Soluções para problemas comuns
"""

# ═══════════════════════════════════════════════════════════════
# PROBLEMAS E SOLUÇÕES
# ═══════════════════════════════════════════════════════════════


## 1. ERRO: ModuleNotFoundError: No module named 'tensorflow'

Solução:
```bash
pip install tensorflow==2.13.1
# ou
pip install -r requirements.txt
```

Verificar:
```bash
python -c "import tensorflow; print(tensorflow.__version__)"
# Output: 2.13.1
```


## 2. ERRO: ImportError: No module named 'database'

Problema: Path incorreto

Solução:
```bash
# Certifique-se de estar no diretório alici-core/
cd alici-core

# E execute scripts com python (não python3 diretamente)
python teste_completo.py

# OU adicione o path manualmente no script:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```


## 3. ERRO: psycopg2.OperationalError: could not connect to server

Problema: DATABASE_URL não configurado

Solução:
```bash
# Crie arquivo .env
cp .env.example .env

# Edite .env com sua URL do Neon:
# DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/alici?sslmode=require

# Verificar conexão:
python -c "from database.neon import db; print(db.conectar())"
```

Obter DATABASE_URL:
1. Vá para https://console.neon.tech/
2. Crie novo projeto
3. Copie a connection string
4. Cole em .env


## 4. ERRO: RuntimeError: Could not load dynamic library 'cudart64_110.dll'

Problema: CUDA não instalado (normal, não é obrigatório)

Solução:
```bash
# Funciona normalmente com CPU
# Para usar GPU:
pip install tensorflow[and-cuda]==2.13.1

# Ou ignore o aviso - TensorFlow funciona com CPU também
```


## 5. ERRO: No module named 'fastapi'

Solução:
```bash
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
```


## 6. ERRO: API não inicia - Port já em uso

Problema: Porta 8000 ocupada

Solução:
```bash
# Opção 1: Use outra porta
uvicorn api.main:app --port 8001

# Opção 2: Mate o processo na porta 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID {PID} /F

# Linux/Mac:
lsof -i :8000
kill -9 {PID}
```


## 7. ERRO: Model shape mismatch na predição

Problema: Dados de entrada com shape incorreto

Solução:
```python
# Verificar shapes esperados:
# Image:  (batch, 32, 32, 3)     - RGB 32x32
# Text:   (batch, 50)             - Sequência de 50 tokens
# Audio:  (batch, 13)             - MFCC com 13 coeficientes

# Garantir que os dados estão corretos:
import numpy as np
X_img = np.random.rand(1, 32, 32, 3)   # ✅ Correto
X_txt = np.random.randint(0, 5000, (1, 50))  # ✅ Correto
X_aud = np.random.rand(1, 13)  # ✅ Correto
```


## 8. ERRO: Neon logging não funciona mas modelo treina

Problema: DATABASE_URL não configurado, mas modelo treina com CPU

Isso é OK! O sistema não quebra se Neon não está disponível.

Verificar logs:
```python
from database.neon import db

# Verificar se logou
logs = db.obter_logs_treino(modelo="alici_core_v1", limit=5)
for log in logs:
    print(f"Epoch {log['epoch']}: Loss={log['loss']:.4f}")
```


## 9. ERRO: Google Colab - librosa não instala

Solução:
```python
# No Colab
!pip install librosa
!pip install soundfile

# Depois import normalmente
import librosa
```


## 10. ERRO: Arquivos .h5 muito grandes (> 150MB)

Problema: Modelo grande demais para Render (limite 500MB)

Solução:
```bash
# Use git LFS para arquivos grandes
git lfs install
git lfs track "*.h5"
git add .gitattributes
git add modelo.h5
git commit -m "Add large model file"
git push

# OU comprima o arquivo
gzip alici_core.h5
# Depois descomprima no servidor
```


## 11. ERRO: Render - Build falha com "requirements not found"

Verificação:
```bash
# Certifique-se que requirements.txt existe na raiz
ls -la requirements.txt

# E contém FastAPI, uvicorn, tensorflow, etc
grep fastapi requirements.txt
grep uvicorn requirements.txt
```

Solução:
```bash
# Atualize Procfile:
web: gunicorn alici_core.api.main:app --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:$PORT
```


## 12. ERRO: Modelo não carrega na API

Problema: Arquivo alici_core.h5 não encontrado

Solução:
```bash
# 1. Verifique se o arquivo existe
ls -la alici_core.h5

# 2. Se não existe, treine localmente
python training/trainer.py
# Salva como alici_core_test.h5
# Renomeie para alici_core.h5

# 3. Ou a API cria automaticamente (modelo novo)
uvicorn api.main:app
# Verá: "⚠️ Arquivo alici_core.h5 não encontrado. Usando modelo novo."
```


## 13. ERRO: API status 503 "Modelo não carregado"

Causa: Modelo não foi inicializado na startup

Verificação:
```bash
# Acesse /health (não precisa do modelo)
curl http://localhost:8000/health

# Se /health retorna 200 mas /status retorna 503
# O problema é no carregamento do modelo

# Check logs:
# Procure por: ❌ Erro ao carregar modelo
```

Solução:
```bash
# Treinar um modelo:
python training/trainer.py

# Ou usar modelo dummy no dev:
# Edite api/main.py, comentar o check do modelo
```


## 14. ERRO: Predição muito lenta (>1s)

Problema: Modelo rodando em CPU

Solução:
```bash
# 1. Verifique se TensorFlow vê GPU:
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# 2. Se vazio, está em CPU (normal)
# 3. Para acelerar:
#    - Use Colab com GPU
#    - Deploy em servidor com GPU
#    - Reduza tamanho do modelo
#    - Use quantização

# Teste de velocidade:
import time
start = time.time()
pred = modelo.predict(X)
print(f"Tempo: {(time.time() - start)*1000:.1f}ms")
```


## 15. ERRO: CORS - Frontend não consegue acessar API

Problema: CORS headers não configurados

Solução (já está em api/main.py):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Mude para lista específica em prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Mais seguro em produção:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-frontend.com",
        "https://www.seu-frontend.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```


## 16. ERRO: "ValueError: Cannot reshape array"

Problema: Shape dos dados incorreto

Debug:
```python
import numpy as np

# Verificar shapes
print(f"X_img shape: {X_img.shape}")  # Deve ser (batch, 32, 32, 3)
print(f"X_txt shape: {X_txt.shape}")  # Deve ser (batch, 50)
print(f"X_aud shape: {X_aud.shape}")  # Deve ser (batch, 13)

# Corrigir se necessário
if X_img.ndim == 3:
    X_img = np.expand_dims(X_img, 0)  # Add batch dimension
```


## 17. ERRO: "Connection refused" ao conectar Neon

Problema: Firewall ou URL incorreta

Verificação:
```python
# Teste conexão manual
import psycopg2

try:
    conn = psycopg2.connect("postgresql://user:pass@ep-xxx.neon.tech/alici?sslmode=require")
    print("✅ Conexão OK")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
```

Solução:
```bash
# 1. Verifique URL do Neon
# 2. Adicione seu IP ao Neon firewall
# 3. Use sslmode=require
# 4. Tente de outro local (Colab funciona sempre)
```


## 18. ERRO: Memory overflow durante treinamento

Problema: Batch size muito grande

Solução:
```python
# Reduz batch size
trainer.treinar(
    X_train, y_train,
    batch_size=8,  # Reduz de 32 para 8
    epochs=50
)

# Ou use generator para dados grandes
# Ver exemplo em GUIA_USO.md
```


## 19. ERRO: "version GLIBCXX_3.4.30 not found"

Problema: Versão de biblioteca incompatível

Solução:
```bash
# Reconstruir com glibc correto
pip install --upgrade tensorflow

# Ou usar Docker/Container
```


## 20. ERRO: Git LFS quota excedida

Problema: Limite de storage em git LFS

Solução:
```bash
# 1. Remove arquivo do LFS
git lfs untrack "*.h5"

# 2. Comprime primeiro
gzip alici_core.h5
# alici_core.h5.gz (~50-60MB)

# 3. Commit comprimido
git add alici_core.h5.gz
git commit -m "Add compressed model"

# 4. No servidor, descomprimir
gzip -d alici_core.h5.gz
```


═══════════════════════════════════════════════════════════════

## 🆘 COMO REPORTAR BUGS

Se encontrar um problema não listado acima:

1. Execute teste_completo.py
   ```bash
   python teste_completo.py
   ```

2. Capture a mensagem de erro completa

3. Abra uma issue no GitHub com:
   - Output do teste_completo.py
   - Python version: python --version
   - OS: Windows/Linux/Mac
   - Traceback completo

4. Email: [seu email]

═══════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
