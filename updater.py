import os
import subprocess
import logging

logger = logging.getLogger(__name__)

UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO")
UPSTREAM_BRANCH = os.environ.get("UPSTREAM_BRANCH", "main")


def run_cmd(cmd: str):
    """Run command and return (return_code, output)"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return 1, "Command timeout"
    except Exception as e:
        return 1, str(e)


def update_from_upstream() -> bool:
    """Update bot from upstream repository"""
    if not UPSTREAM_REPO:
        logger.error("❌ UPSTREAM_REPO not configured in config.env")
        return False
    
    if not UPSTREAM_BRANCH:
        logger.error("❌ UPSTREAM_BRANCH not configured in config.env")
        return False

    logger.info(f"🔄 Starting upstream update from {UPSTREAM_REPO} (branch: {UPSTREAM_BRANCH})...")

    cmds = [
        ("git init", "Initialize git repository"),
        ("git config user.name 'bot-updater'", "Set git user"),
        ("git config user.email 'bot@localhost'", "Set git email"),
        ("git add .", "Stage local changes"),
        ("git commit -m 'local changes' || true", "Commit local changes (ignore if none)"),
        (f"git remote remove origin || true", "Remove old remote (ignore if not exists)"),
        (f"git remote add origin {UPSTREAM_REPO}", "Add upstream repository"),
        (f"git fetch origin {UPSTREAM_BRANCH}", "Fetch latest code from upstream"),
        (f"git reset --hard origin/{UPSTREAM_BRANCH}", "Apply upstream changes"),
    ]

    for cmd, desc in cmds:
        logger.info(f"  Running: {desc}")
        return_code, output = run_cmd(cmd)
        
        if return_code != 0:
            logger.error(f"  ❌ Failed: {desc}")
            logger.error(f"  Error output: {output}")
            return False
        else:
            logger.info(f"  ✅ Success: {desc}")

    logger.info("✅ Upstream update completed successfully!")
    return True


def restart_bot():
    logger.info("Restarting bot process...")
    os.execv(sys.executable, [sys.executable] + sys.argv)