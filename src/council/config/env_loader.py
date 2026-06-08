from __future__ import annotations

import os
from pathlib import Path


def load_dotenv_file(path: Path) -> None:
    """Load KEY=VALUE pairs from a dotenv file without overriding existing env vars."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key or key in os.environ:
            continue
        cleaned = value.strip()
        if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in "\"'":
            cleaned = cleaned[1:-1]
        os.environ[key] = cleaned


def load_dotenv_from_cwd() -> None:
    """Load ``.env`` from the current working directory if present."""
    load_dotenv_file(Path.cwd() / ".env")
