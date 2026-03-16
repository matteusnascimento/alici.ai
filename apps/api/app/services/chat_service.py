from pathlib import Path
import sys


AI_ENGINE_PATH = Path(__file__).resolve().parents[3] / "ai-engine"
if str(AI_ENGINE_PATH) not in sys.path:
    sys.path.append(str(AI_ENGINE_PATH))

from llm.llm_router import generate_response


def generate(message: str) -> str:
    return generate_response(message)