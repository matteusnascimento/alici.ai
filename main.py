"""Root entrypoint for running the Alici API project.

Common usage:
    python main.py
    python main.py web
    python main.py migrate
    python main.py worker
    python main.py all

The ASGI object remains exported as ``app`` so deployment platforms can also
run ``uvicorn main:app``.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from alici_api.app import app  # noqa: E402  (ASGI export for uvicorn/gunicorn)
from alici_api.config import get_settings  # noqa: E402


def _python() -> str:
    return sys.executable or "python"


def _alembic_executable() -> str:
    executable = shutil.which("alembic")
    if executable:
        return executable

    scripts_dir = Path(_python()).resolve().parent / ("Scripts" if os.name == "nt" else "bin")
    candidate = scripts_dir / ("alembic.exe" if os.name == "nt" else "alembic")
    if candidate.exists():
        return str(candidate)

    return "alembic"


def _arq_executable() -> str:
    executable = shutil.which("arq")
    if executable:
        return executable

    scripts_dir = Path(_python()).resolve().parent / ("Scripts" if os.name == "nt" else "bin")
    candidate = scripts_dir / ("arq.exe" if os.name == "nt" else "arq")
    if candidate.exists():
        return str(candidate)

    return "arq"


def run_web(host: str, port: int, reload: bool) -> None:
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(BASE_DIR / "alici_api")] if reload else None,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


def run_migrations() -> None:
    subprocess.check_call([_alembic_executable(), "upgrade", "head"], cwd=str(BASE_DIR))


def run_worker(worker_settings: str) -> None:
    subprocess.check_call([_arq_executable(), worker_settings], cwd=str(BASE_DIR))


def run_all(host: str, port: int, reload: bool) -> None:
    """Run API and default worker together for local development.

    Production should use separate processes/dynos/services as defined in
    ``Procfile`` so web and worker scaling stay independent.
    """

    worker = subprocess.Popen(
        [_arq_executable(), "alici_api.jobs.queue.WorkerSettings"],
        cwd=str(BASE_DIR),
    )
    try:
        run_web(host=host, port=port, reload=reload)
    finally:
        worker.terminate()
        try:
            worker.wait(timeout=10)
        except subprocess.TimeoutExpired:
            worker.kill()


def run_doctor() -> None:
    settings = get_settings()
    print(f"app={settings.app_name} version={settings.app_version}")
    print(f"env={settings.env}")
    print(f"database_url={'configured' if settings.database_url else 'missing'}")
    print(f"redis_url={settings.resolved_redis_url}")
    print(f"docs_enabled={settings.api_docs_enabled}")
    print(f"openapi_enabled={settings.api_openapi_enabled}")
    print(f"cors_origins={settings.cors_origins}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run and operate the Alici API project.")
    parser.add_argument(
        "command",
        nargs="?",
        default="web",
        choices=("web", "dev", "migrate", "worker", "worker-high", "worker-low", "worker-dlq", "all", "doctor"),
        help="Command to run. Default: web.",
    )
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_settings()

    if args.command == "migrate":
        run_migrations()
        return

    if args.command == "doctor":
        run_doctor()
        return

    if args.command == "worker":
        run_worker("alici_api.jobs.queue.WorkerSettings")
        return

    if args.command == "worker-high":
        run_worker("alici_api.jobs.queue.HighPriorityWorkerSettings")
        return

    if args.command == "worker-low":
        run_worker("alici_api.jobs.queue.LowPriorityWorkerSettings")
        return

    if args.command == "worker-dlq":
        run_worker("alici_api.jobs.queue.DeadLetterWorkerSettings")
        return

    reload = bool(args.reload or args.command == "dev" or (settings.is_development and args.command == "web"))

    if args.command == "all":
        run_all(host=args.host, port=args.port, reload=reload)
        return

    run_web(host=args.host, port=args.port, reload=reload)


if __name__ == "__main__":
    main()
