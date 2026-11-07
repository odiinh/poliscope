"""Read a variable from the environment, falling back to the repo's .env.local."""

import os
from pathlib import Path

ENV_LOCAL = Path(__file__).resolve().parents[2] / ".env.local"


def env(name):
    if name in os.environ:
        return os.environ[name]
    if ENV_LOCAL.exists():
        for line in ENV_LOCAL.read_text().splitlines():
            k, sep, v = line.partition("=")
            if sep and k.strip() == name:
                return v.strip().strip("\"'")
    return None
