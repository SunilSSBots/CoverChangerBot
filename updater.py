import os
import subprocess
import logging

logger = logging.getLogger(__name__)

UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO")
UPSTREAM_BRANCH = os.environ.get("UPSTREAM_BRANCH", "")


def run_cmd(cmd: str) -> int:
    return subprocess.call(cmd, shell=True)


def update_from_upstream() -> bool:
    if not UPSTREAM_REPO:
        logger.error("UPSTREAM_REPO not set")
        return False

    logger.info("Starting upstream update...")

    cmds = [
        "git init",
        "git config user.name 'bot-updater'",
        "git config user.email 'bot@localhost'",
        "git add .",
        "git commit -m 'local changes' || true",
        f"git remote remove origin || true",
        f"git remote add origin {UPSTREAM_REPO}",
        "git fetch origin",
        f"git reset --hard origin/{UPSTREAM_BRANCH}",
    ]

    for cmd in cmds:
        if run_cmd(cmd) != 0:
            logger.error(f"Command failed: {cmd}")
            return False

    logger.info("Upstream update successful")
    return True


def restart_bot():
    logger.info("Restarting bot process...")
    os.execv(sys.executable, [sys.executable] + sys.argv)
