import os
from types import SimpleNamespace
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

# Load `config.env` from repository root if present, else fallback to default .env behavior
base = Path(__file__).parent
dotenv_path = base / "config.env"
if load_dotenv:
    if dotenv_path.exists():
        load_dotenv(dotenv_path=str(dotenv_path))
    else:
        load_dotenv()

# Expose all environment variables as attributes on `config`
_config = {k: v for k, v in os.environ.items()}
config = SimpleNamespace(**_config)

__all__ = ["config"]
