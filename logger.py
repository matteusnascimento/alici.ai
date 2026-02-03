"""
logger.py
Módulo centralizado de logging para ALICI
"""

import logging
import os
from datetime import datetime

# Criar diretório de logs se não existir
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configuração de logging
log_file = os.path.join(LOG_DIR, f"alici_{datetime.now().strftime('%Y%m%d')}.log")

# Formato detalhado
log_format = logging.Formatter(
    '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configurar logger raiz
logger = logging.getLogger("alici")
logger.setLevel(logging.DEBUG)

# Handler para arquivo
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# Handler para console (apenas em desenvolvimento)
console_handler = logging.StreamHandler()
console_level = logging.INFO if os.getenv("ENV") == "production" else logging.DEBUG
console_handler.setLevel(console_level)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# Criar loggers específicos por módulo
def get_logger(name: str) -> logging.Logger:
    """
    Obter logger específico para um módulo
    """
    return logging.getLogger(f"alici.{name}")
