# Join Our Telegram Channel :- @SSBotsUpdates
# Subscribe YouTube Channel For More Bots Updates :- SunilWebTricks
# Ask Doubt Contact Me On telegram @Sunil_Sharma_2_0_Bot

"""
Telegram Instant Video Cover Bot
Clean, Modular Main Entrypoint
"""

import logging
import sys
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from telegram import BotCommand

from config import BOT_TOKEN, LOG_CHANNEL_ID
from helpers.forcesub import check_force_sub
from helpers.callbacks import handle_callback_query
from helpers.admin import admin_panel_cmd, ban_cmd, unban_cmd, stats_cmd
from helpers.handlers import (
    start_cmd, help_cmd, about_cmd, settings_cmd, fonts_cmd,
    channel_cmd, remove_thumbnail_cmd, photo_handler, video_handler,
    text_and_channel_handler
)

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Middleware wrapper for commands to enforce force-sub & ban check
def wrap_sub(handler_fn):
    async def wrapper(update, context):
        if not await check_force_sub(update, context):
            return
        return await handler_fn(update, context)
    return wrapper


async def post_init(application):
    """Set up Telegram bot command menu list and send startup log"""
    try:
        commands = [
            BotCommand("start", "🏠 Start Bot & Main Menu"),
            BotCommand("help", "ℹ️ Complete Guide & Commands"),
            BotCommand("settings", "⚙️ Bot Preferences & Status"),
            BotCommand("fonts", "✍️ Change Caption Font Style"),
            BotCommand("channel", "📢 Destination Channel Setup"),
            BotCommand("remove", "🗑️ Remove Saved Cover"),
            BotCommand("about", "🤖 About & Credits"),
            BotCommand("admin", "🛡️ Admin Control Panel"),
            BotCommand("stats", "📊 Bot User Stats"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("✅ Bot commands registered successfully")
        
        # Send startup deploy log to configured LOG_CHANNEL_ID
        if LOG_CHANNEL_ID:
            try:
                startup_msg = (
                    "🚀 <b>CoverChangerBot Started Successfully!</b>\n\n"
                    "⚡ <b>Status:</b> Online & Running\n"
                    "📢 <b>Updates:</b> @SSBotsUpdates\n"
                    "📺 <b>YouTube:</b> SunilWebTricks\n"
                    "💬 <b>Support:</b> @Sunil_Sharma_2_0_Bot"
                )
                await application.bot.send_message(chat_id=LOG_CHANNEL_ID, text=startup_msg, parse_mode="HTML")
            except Exception as log_err:
                logger.debug(f"Startup log notice: {log_err}")
                
    except Exception as e:
        logger.warning(f"Post init error: {e}")


def main():
    """Start the bot instance"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is missing in config/environment!")
        sys.exit(1)

    print("=" * 60)
    print("🚀 CoverChangerBot Starting...")
    print("📢 Updates Telegram Channel : @SSBotsUpdates")
    print("📺 YouTube Channel          : SunilWebTricks")
    print("💬 Support / Contact        : @Sunil_Sharma_2_0_Bot")
    print("=" * 60)

    logger.info("🚀 Starting CoverChangerBot...")
    logger.info("📢 Channel: @SSBotsUpdates | 📺 YouTube: SunilWebTricks | 💬 Support: @Sunil_Sharma_2_0_Bot")
    
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # User Commands
    app.add_handler(CommandHandler("start", wrap_sub(start_cmd), filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("help", wrap_sub(help_cmd), filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("about", wrap_sub(about_cmd), filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("settings", wrap_sub(settings_cmd), filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler(["fonts", "font"], wrap_sub(fonts_cmd), filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler(["channel", "channels"], wrap_sub(channel_cmd), filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler(["remove", "delete"], wrap_sub(remove_thumbnail_cmd), filters=filters.ChatType.PRIVATE))

    # Admin Commands
    app.add_handler(CommandHandler("admin", admin_panel_cmd, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("ban", ban_cmd, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("unban", unban_cmd, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("stats", stats_cmd, filters=filters.ChatType.PRIVATE))

    # Media Handlers
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, wrap_sub(photo_handler)))
    app.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.PRIVATE, wrap_sub(video_handler)))
    app.add_handler(MessageHandler(filters.Document.VIDEO & filters.ChatType.PRIVATE, wrap_sub(video_handler)))

    # Channel ID Link & Forward Handlers
    app.add_handler(MessageHandler(filters.FORWARDED & filters.ChatType.PRIVATE, wrap_sub(text_and_channel_handler)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, wrap_sub(text_and_channel_handler)))

    # Callback Query Router
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    logger.info("✅ All handlers registered. Bot is listening...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
