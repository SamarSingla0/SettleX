#!/usr/bin/env python
"""Run Django from the repo root without cd into backend/."""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Activate the project venv first "
        "(venv\\Scripts\\activate)."
    ) from exc

execute_from_command_line(sys.argv)
