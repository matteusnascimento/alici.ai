"""
Development mode flag.

Set DEV_MODE=true in the environment to bypass authentication and go straight
to the dashboard.  This module is intentionally kept separate from
``app.core.config`` so that lightweight helpers (e.g. scripts, CLI tools) can
import it without pulling in the full Pydantic settings stack.

For application code that already has access to the settings object, prefer
``settings.dev_mode`` from ``app.core.config`` instead of importing this
module directly, to avoid having two independent reads of the environment.

WARNING: Never enable DEV_MODE in production.
"""
import os

DEV_MODE: bool = os.getenv("DEV_MODE", "false").lower() == "true"
