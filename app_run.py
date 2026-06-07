"""One-file local launcher for alici.ai.

Usage:
    python app_run.py
    python app_run.py --web-only
    python app_run.py --worker-only
    python app_run.py --migrate
    python app_run.py --doctor

Default behavior starts the FastAPI web app and the default Arq worker together.
Production should still run web and worker as separate Render services.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "backend" / ".env", override=False)

from alici_api.config import get_settings  # noqa: E402


def _load_app():
    from alici_api.app import app

    return app


def _exe(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found

    scripts_dir = Path(sys.executable).resolve().parent / ("Scripts" if os.name == "nt" else "bin")
    suffix = ".exe" if os.name == "nt" else ""
    candidate = scripts_dir / f"{name}{suffix}"
    if candidate.exists():
        return str(candidate)
    return name


def _run_checked(command: list[str]) -> None:
    subprocess.check_call(command, cwd=str(ROOT))


async def _redis_ready() -> bool:
    try:
        from redis.asyncio import Redis

        redis = Redis.from_url(get_settings().resolved_redis_url, socket_connect_timeout=2, socket_timeout=2)
        try:
            await redis.ping()
            return True
        finally:
            await redis.aclose()
    except Exception:
        return False


def _start_worker(queue_settings: str) -> subprocess.Popen:
    return subprocess.Popen(
        [_exe("arq"), queue_settings],
        cwd=str(ROOT),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            process.terminate()
        process.wait(timeout=8)
    except Exception:
        process.kill()


def _run_web(host: str, port: int, reload: bool) -> None:
    uvicorn.run(
        "alici_api.app:app" if reload else _load_app(),
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(ROOT / "alici_api")] if reload else None,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


def _doctor() -> None:
    from alici_api.services.ai.manager import AIManager
    from alici_api.services.media_service import MediaProviderUnavailableError, available_media_providers
    from alici_api.services.media_storage import R2MediaStorage

    settings = get_settings()
    storage = R2MediaStorage()
    storage_status = storage.status(include_probe=False)
    redis_ready = asyncio.run(_redis_ready())
    manager = AIManager()
    ai_status = manager.provider_statuses(include_probe=False)

    print("alici.ai doctor")
    print(f"root={ROOT}")
    print(f"env={settings.env}")
    print(f"database_url={'ok' if settings.database_url else 'missing'}")
    print(f"redis_url={settings.resolved_redis_url}")
    print(f"redis_required={'yes' if settings.is_production else 'recommended'}")
    print(f"redis_ready={'yes' if redis_ready else 'no'}")
    if not redis_ready:
        print("redis_local_setup=docker run -d --name redis-alici -p 6379:6379 redis:7-alpine")
    print(f"docs_enabled={settings.api_docs_enabled}")
    print(f"openapi_enabled={settings.api_openapi_enabled}")
    print(f"r2_configured={'yes' if storage_status['configured'] else 'no'}")
    if storage_status["missing"]:
        print(f"r2_missing={','.join(storage_status['missing'])}")
    print(f"default_ai_provider={settings.default_ai_provider}")
    print(f"ai_available={','.join(manager.available_providers()) or 'none'}")
    for name, status in ai_status.items():
        print(
            "ai_provider="
            f"{name};configured={str(status.get('configured')).lower()};"
            f"enabled={str(status.get('enabled')).lower()};"
            f"model={status.get('model')};reason={status.get('reason') or 'ok'}"
        )
    for media_type in ("image", "audio", "video", "image_analysis"):
        try:
            providers = available_media_providers(media_type)
            summary = ",".join(
                f"{item.provider_name}:{item.model_name}" if hasattr(item, "provider_name") else str(item)
                for item in providers
            ) or "none"
        except MediaProviderUnavailableError as exc:
            summary = f"none;reason={exc}"
        except Exception as exc:
            summary = f"error;reason={exc}"
        print(f"media_provider_{media_type}={summary}")
    print("web_command=python app_run.py --web-only")
    print("worker_command=python app_run.py --worker-only")
    if settings.is_production and (not redis_ready or not storage_status["configured"] or not manager.available_providers()):
        raise SystemExit(1)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run alici.ai from one root file.")
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload.")
    parser.add_argument("--web-only", action="store_true", help="Run only the FastAPI web process.")
    parser.add_argument("--worker-only", action="store_true", help="Run only the default Arq worker.")
    parser.add_argument("--migrate", action="store_true", help="Run Alembic migrations then exit.")
    parser.add_argument("--migrate-first", action="store_true", help="Run migrations before starting.")
    parser.add_argument("--doctor", action="store_true", help="Print local configuration checks then exit.")
    return parser


def main() -> None:
    args = _parser().parse_args()
    settings = get_settings()

    if args.doctor:
        _doctor()
        return

    if args.migrate:
        _run_checked([_exe("alembic"), "upgrade", "head"])
        return

    if args.migrate_first:
        _run_checked([_exe("alembic"), "upgrade", "head"])

    if args.worker_only:
        _run_checked([_exe("arq"), "alici_api.jobs.queue.WorkerSettings"])
        return

    reload = bool(args.reload or settings.is_development)

    if args.web_only:
        _run_web(host=args.host, port=args.port, reload=reload)
        return

    if not asyncio.run(_redis_ready()):
        if settings.is_production:
            raise SystemExit("REDIS_URL nao esta acessivel. O worker e obrigatorio em producao.")
        print("Aviso: Redis nao respondeu. Subindo apenas a API web local.")
        print("Para jobs de midia, rode: docker run -d --name redis-alici -p 6379:6379 redis:7-alpine")
        _run_web(host=args.host, port=args.port, reload=reload)
        return

    worker = _start_worker("alici_api.jobs.queue.WorkerSettings")
    try:
        _run_web(host=args.host, port=args.port, reload=reload)
    finally:
        _stop_process(worker)


if __name__ == "__main__":
    main()
