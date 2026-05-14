"""
logger.py
Módulo centralizado de logging para ALICI
"""

import json
import logging
import os
from datetime import datetime

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, f"alici_{datetime.now().strftime('%Y%m%d')}.log")


class JsonLogFormatter(logging.Formatter):
    _reserved = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key not in self._reserved and not key.startswith("_"):
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


log_format = JsonLogFormatter()

logger = logging.getLogger("alici")
logger.setLevel(logging.DEBUG)

if logger.handlers:
    logger.handlers.clear()

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_level = logging.INFO if os.getenv("ENV") == "production" else logging.DEBUG
console_handler.setLevel(console_level)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"alici.{name}")
