"""
🗄️ CONEXÃO NEON - LOGS DE TREINO
Persistência em banco de dados para monitorar treinamento
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import json

class NeonDB:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if not self.connection_string:
            raise ValueError("DATABASE_URL não configurada no .env")
    
    def conectar(self):
        """Conecta ao banco Neon"""
        try:
            conn = psycopg2.connect(self.connection_string)
            return conn
        except Exception as e:
            print(f"❌ Erro ao conectar Neon: {e}")
            return None
    
    def criar_tabelas(self):
        """Cria tabelas se não existirem"""
        conn = self.conectar()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        try:
            # Tabela de logs de treino
            cur.execute("""
                CREATE TABLE IF NOT EXISTS treino_logs (
                    id SERIAL PRIMARY KEY,
                    modelo TEXT NOT NULL,
                    tipo_dado TEXT NOT NULL,
                    epoch INT,
                    loss FLOAT,
                    accuracy FLOAT,
                    val_loss FLOAT,
                    val_accuracy FLOAT,
                    tempo_epoch INT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Tabela de modelos
            cur.execute("""
                CREATE TABLE IF NOT EXISTS modelos (
                    id SERIAL PRIMARY KEY,
                    nome TEXT UNIQUE NOT NULL,
                    versao TEXT,
                    tipo TEXT,
                    tamanho_mb FLOAT,
                    accuracy FLOAT,
                    parameters INT,
                    data_treino TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Tabela de predições
            cur.execute("""
                CREATE TABLE IF NOT EXISTS predicoes (
                    id SERIAL PRIMARY KEY,
                    modelo_id INT REFERENCES modelos(id),
                    input_type TEXT,
                    output JSONB,
                    tempo_ms INT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Tabela de usuários (futuro)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nome TEXT,
                    email TEXT UNIQUE,
                    plano TEXT DEFAULT 'free',
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Índices
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_treino_modelo 
                ON treino_logs(modelo);
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_treino_tipo 
                ON treino_logs(tipo_dado);
            """)
            
            conn.commit()
            print("✅ Tabelas criadas com sucesso!")
            return True
        
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            return False
        
        finally:
            cur.close()
            conn.close()
    
    def log_treino(self, modelo, tipo_dado, epoch, loss, accuracy, 
                   val_loss=None, val_accuracy=None, tempo_epoch=None):
        """Log de uma época de treinamento"""
        conn = self.conectar()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO treino_logs 
                (modelo, tipo_dado, epoch, loss, accuracy, val_loss, val_accuracy, tempo_epoch)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (modelo, tipo_dado, epoch, loss, accuracy, val_loss, val_accuracy, tempo_epoch))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"❌ Erro ao fazer log: {e}")
            return False
        
        finally:
            cur.close()
            conn.close()
    
    def registrar_modelo(self, nome, versao, tipo, tamanho_mb, accuracy, parameters):
        """Registra um modelo no banco"""
        conn = self.conectar()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO modelos 
                (nome, versao, tipo, tamanho_mb, accuracy, parameters, data_treino)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (nome) DO UPDATE SET
                    versao = %s,
                    tamanho_mb = %s,
                    accuracy = %s,
                    parameters = %s,
                    data_treino = %s
            """, (
                nome, versao, tipo, tamanho_mb, accuracy, parameters, datetime.now(),
                versao, tamanho_mb, accuracy, parameters, datetime.now()
            ))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"❌ Erro ao registrar modelo: {e}")
            return False
        
        finally:
            cur.close()
            conn.close()
    
    def obter_modelos(self):
        """Retorna todos os modelos registrados"""
        conn = self.conectar()
        if not conn:
            return []
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute("SELECT * FROM modelos ORDER BY created_at DESC;")
            modelos = cur.fetchall()
            return modelos
        
        except Exception as e:
            print(f"❌ Erro ao obter modelos: {e}")
            return []
        
        finally:
            cur.close()
            conn.close()
    
    def obter_logs_treino(self, modelo=None, limit=100):
        """Retorna logs de treino"""
        conn = self.conectar()
        if not conn:
            return []
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if modelo:
                cur.execute(
                    "SELECT * FROM treino_logs WHERE modelo = %s ORDER BY created_at DESC LIMIT %s;",
                    (modelo, limit)
                )
            else:
                cur.execute("SELECT * FROM treino_logs ORDER BY created_at DESC LIMIT %s;", (limit,))
            
            logs = cur.fetchall()
            return logs
        
        except Exception as e:
            print(f"❌ Erro ao obter logs: {e}")
            return []
        
        finally:
            cur.close()
            conn.close()
    
    def log_predicao(self, modelo_id, input_type, output, tempo_ms):
        """Log de uma predição"""
        conn = self.conectar()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        try:
            output_json = json.dumps(output)
            
            cur.execute("""
                INSERT INTO predicoes 
                (modelo_id, input_type, output, tempo_ms)
                VALUES (%s, %s, %s, %s)
            """, (modelo_id, input_type, output_json, tempo_ms))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"❌ Erro ao logar predição: {e}")
            return False
        
        finally:
            cur.close()
            conn.close()


# Instância global
db = NeonDB()


if __name__ == "__main__":
    # Teste de conexão
    print("🔌 Testando conexão Neon...")
    
    if db.conectar():
        print("✅ Conexão OK")
        db.criar_tabelas()
    else:
        print("❌ Falha na conexão")
