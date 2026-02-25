"""Entrypoint principal da ALICI (ASGI)."""

import os
import sys

import uvicorn
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv()

from alici_api.app import app


def run() -> None:
    port = int(os.getenv("PORT", 8000))
    env = os.getenv("ENV", "development")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=(env == "development"))


if __name__ == "__main__":
    run()
