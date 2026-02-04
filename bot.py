import os
import logging
import random
from telegram import Update, MessageEntity, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from config import config
import sys
from updater import update_from_upstream
from telegram.error import BadRequest, RetryAfter

# Import from modular files
from helpers import (
    is_admin, check_admin, check_force_sub, send_log, get_invite_link
)
from admin_commands import (
    admin_menu, ban_cmd, unban_cmd, stats_cmd, status_cmd, broadcast_cmd
)
from user_commands import (
    start, help_cmd, about, settings, remover
)
from handlers import (
    callback_handler, photo_handler, video_handler, text_handler, open_home
)
from database import log_new_user

# ========== LOGGING SETUP ==========
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ========== CONFIG SETUP ==========
TOKEN = getattr(config, "BOT_TOKEN", None) or os.environ.get("BOT_TOKEN")
if not TOKEN:
    logger.error("BOT_TOKEN not set in config or environment (config.env).")
    raise SystemExit("BOT_TOKEN not set")

OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
FORCE_SUB_CHANNEL_ID = os.environ.get("FORCE_SUB_CHANNEL_ID")
FORCE_SUB_BANNER_URL = os.environ.get("FORCE_SUB_BANNER_URL")
HOME_MENU_BANNER_URL = os.environ.get("HOME_MENU_BANNER_URL")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "")
LOG_CHANNEL_ID = os.environ.get("LOG_CHANNEL_ID")

# Fallback: collect images from ./ui/ and pick randomly when showing banner
FALLBACK_BANNER = None
UI_BANNERS = []
try:
    ui_dir = os.path.join(os.path.dirname(__file__), "ui")
    if os.path.isdir(ui_dir):
        UI_BANNERS = [os.path.join(ui_dir, f) for f in os.listdir(ui_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
        if UI_BANNERS:
            FALLBACK_BANNER = UI_BANNERS[0]
except Exception:
    UI_BANNERS = []
    FALLBACK_BANNER = None

# ========== SHARED STATE ==========
# In-memory set of users who completed the verify step
verified_users = set()

# ========== HELPER FUNCTIONS ==========
def bold_entities(text: str):
    """Return entities list to make full caption bold"""
    if not text:
        return None
    return [MessageEntity(type="bold", offset=0, length=len(text))]


def get_force_banner():
    """Return a banner URL or local file path. Prefer env URL; else pick random local image."""
    if FORCE_SUB_BANNER_URL:
        return FORCE_SUB_BANNER_URL
    try:
        if UI_BANNERS:
            return random.choice(UI_BANNERS)
    except Exception:
        pass
    return FALLBACK_BANNER


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        return await update.message.reply_text("❌ You are not authorized.")

    msg = await update.message.reply_text("🔄 Checking for updates from upstream...")

    try:
        success = update_from_upstream()

        if not success:
            await msg.edit_text(
                "❌ <b>Update Failed</b>\n\n"
                "Could not fetch updates from upstream.\n"
                "Please check:\n"
                "• UPSTREAM_REPO is correct\n"
                "• UPSTREAM_BRANCH is correct\n"
                "• Internet connection is active\n\n"
                "Check logs for details.",
                parse_mode="HTML"
            )
            logger.error(f"Update failed - bot not restarting")
            return

        # Update successful - now restart
        await msg.edit_text(
            "✅ <b>Update Successful!</b>\n\n"
            "🔄 Restarting bot with new changes...\n"
            "<i>Please wait...</i>",
            parse_mode="HTML"
        )
        
        logger.info("✅ Update completed successfully. Restarting bot...")
        # Give time for message to be sent
        await asyncio.sleep(1)
        
        # Restart the bot
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    except Exception as e:
        logger.error(f"❌ Error during restart/update: {e}")
        await msg.edit_text(
            f"❌ <b>Error During Update</b>\n\n"
            f"An unexpected error occurred:\n"
            f"<code>{str(e)[:100]}</code>\n\n"
            f"Check logs for full details.",
            parse_mode="HTML"
        )


async def post_init(app: Application) -> None:
    """Post-initialization callback"""
    logger.info("🤖 Bot initialized and ready!")


def main() -> None:
    """Start the bot"""
    # Set module-level variables for imported modules
    import helpers
    import admin_commands
    import user_commands
    import handlers
    
    helpers.OWNER_ID = OWNER_ID
    helpers.FORCE_SUB_CHANNEL_ID = FORCE_SUB_CHANNEL_ID
    helpers.FORCE_SUB_BANNER_URL = FORCE_SUB_BANNER_URL
    helpers.LOG_CHANNEL_ID = LOG_CHANNEL_ID
    
    admin_commands.OWNER_ID = OWNER_ID
    admin_commands.HOME_MENU_BANNER_URL = HOME_MENU_BANNER_URL
    admin_commands.LOG_CHANNEL_ID = LOG_CHANNEL_ID
    
    user_commands.OWNER_ID = OWNER_ID
    user_commands.FORCE_SUB_CHANNEL_ID = FORCE_SUB_CHANNEL_ID
    user_commands.HOME_MENU_BANNER_URL = HOME_MENU_BANNER_URL
    user_commands.LOG_CHANNEL_ID = LOG_CHANNEL_ID
    
    handlers.OWNER_ID = OWNER_ID
    handlers.FORCE_SUB_CHANNEL_ID = FORCE_SUB_CHANNEL_ID
    handlers.FORCE_SUB_BANNER_URL = FORCE_SUB_BANNER_URL
    handlers.HOME_MENU_BANNER_URL = HOME_MENU_BANNER_URL
    
    # Create the Application
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # ========== COMMAND HANDLERS ==========
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CommandHandler("remove", remover))
    app.add_handler(CommandHandler("restart", restart))

    # ========== MESSAGE HANDLERS ==========
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.VIDEO, video_handler))
    app.add_handler(MessageHandler(filters.TEXT, text_handler))

    # ========== CALLBACK HANDLERS ==========
    app.add_handler(CallbackQueryHandler(callback_handler))

    # ========== START BOT ==========
    logger.info("🚀 Starting bot...")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
