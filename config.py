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

# Common variables for easy direct import
BOT_TOKEN = getattr(config, "BOT_TOKEN", None) or os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
ADMIN_ID = OWNER_ID
FORCE_SUB_CHANNEL_ID = os.environ.get("FORCE_SUB_CHANNEL_ID")
FORCE_SUB_BANNER_URL = os.environ.get("FORCE_SUB_BANNER_URL")
FORCE_SUB_CHANNEL_INVITE_LINK = os.environ.get("FORCE_SUB_CHANNEL_INVITE_LINK", "")
HOME_MENU_BANNER_URL = os.environ.get("HOME_MENU_BANNER_URL")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "")
LOG_CHANNEL_ID = os.environ.get("LOG_CHANNEL_ID")

__all__ = [
    "config", "BOT_TOKEN", "OWNER_ID", "ADMIN_ID",
    "FORCE_SUB_CHANNEL_ID", "FORCE_SUB_BANNER_URL", "FORCE_SUB_CHANNEL_INVITE_LINK",
    "HOME_MENU_BANNER_URL", "OWNER_USERNAME", "LOG_CHANNEL_ID"
]
