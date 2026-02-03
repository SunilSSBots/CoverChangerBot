"""
Admin Commands Module
Contains all admin-only command handlers
"""

import logging
import psutil
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from database import (
    get_stats, ban_user, unban_user, get_total_users,
    log_user_banned, log_user_unbanned, format_log_message, get_banned_users_count
)
from helpers import check_admin, is_admin, send_log

logger = logging.getLogger(__name__)

# Module-level variables set by bot.py
OWNER_ID = None
HOME_MENU_BANNER_URL = None
LOG_CHANNEL_ID = None


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin control panel"""
    if not await check_admin(update):
        return
    
    text = (
        "🛡️ <b>Admin Control Panel</b>\n\n"
        "👑 <b>Welcome Admin!</b>\n\n"
        "You have full access to all bot management tools:\n\n"
        "📊 View detailed statistics\n"
        "⏱️ Monitor bot performance\n"
        "🚫 Ban/Unban users\n"
        "📢 Send announcements to all users\n\n"
        "Choose an option below:"
    )
    admin_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
         InlineKeyboardButton("⏱️ Status", callback_data="admin_status")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users"),
         InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban")],
        [InlineKeyboardButton("✅ Unban User", callback_data="admin_unban"),
         InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_back")],
    ])
    
    # Get home menu banner
    banner = HOME_MENU_BANNER_URL
    
    if banner:
        try:
            import os
            from telegram import InputFile
            if isinstance(banner, str) and os.path.isfile(banner):
                await update.message.reply_photo(
                    photo=InputFile(banner),
                    caption=text,
                    reply_markup=admin_kb,
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_photo(
                    photo=banner,
                    caption=text,
                    reply_markup=admin_kb,
                    parse_mode="HTML"
                )
            return
        except Exception as e:
            logger.warning(f"Could not send admin menu banner: {e}")
    
    await update.message.reply_text(text, reply_markup=admin_kb, parse_mode="HTML")


async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user - usage: /ban user_id reason"""
    if not await check_admin(update):
        return
    
    args = update.message.text.split(None, 2)
    if len(args) < 2:
        return await update.message.reply_text(
            "❌ Usage: /ban <user_id> [reason]\n"
            "Example: /ban 123456789 Spam"
        )
    
    try:
        user_id = int(args[1])
        reason = args[2] if len(args) > 2 else "No reason"
        
        if ban_user(user_id, reason):
            await update.message.reply_text(
                f"✅ <b>User {user_id} Banned</b>\n"
                f"Reason: {reason}",
                parse_mode="HTML"
            )
            
            # Log ban action
            log_data = log_user_banned(user_id, "User", reason)
            log_msg = format_log_message(user_id, "User", log_data["action"], log_data.get("details", ""))
            await send_log(context, log_msg)
        else:
            await update.message.reply_text("❌ Failed to ban user")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user - usage: /unban user_id"""
    if not await check_admin(update):
        return
    
    args = update.message.text.split()
    if len(args) < 2:
        return await update.message.reply_text(
            "❌ Usage: /unban <user_id>\n"
            "Example: /unban 123456789"
        )
    
    try:
        user_id = int(args[1])
        if unban_user(user_id):
            await update.message.reply_text(f"✅ User {user_id} Unbanned")
            
            # Log unban action
            log_data = log_user_unbanned(user_id, "User")
            log_msg = format_log_message(user_id, "User", log_data["action"])
            await send_log(context, log_msg)
        else:
            await update.message.reply_text("❌ Failed to unban user")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    if not await check_admin(update):
        return
    
    stats = get_stats()
    text = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: <b>{stats['total_users']}</b>\n"
        f"🚫 Banned Users: <b>{stats['banned_users']}</b>\n"
        f"🖼 Users with Thumbnail: <b>{stats['users_with_thumbnail']}</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status (uptime, CPU, RAM)"""
    if not await check_admin(update):
        return
    
    import psutil
    import time
    
    try:
        # Bot uptime (from when bot.py started)
        uptime_seconds = time.time() - context.bot_data.get('start_time', time.time())
        uptime_hours = int(uptime_seconds // 3600)
        uptime_mins = int((uptime_seconds % 3600) // 60)
        
        # System stats
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        
        text = (
            "⏱️ <b>Bot Status</b>\n\n"
            f"🟢 Status: <b>Online</b>\n"
            f"⏰ Uptime: <b>{uptime_hours}h {uptime_mins}m</b>\n\n"
            f"🖥 <b>System Resources:</b>\n"
            f"CPU: <b>{cpu_percent}%</b>\n"
            f"RAM: <b>{ram_percent}%</b> ({ram.used // (1024**2)} MB / {ram.total // (1024**2)} MB)"
        )
        await update.message.reply_text(text, parse_mode="HTML")
    except ImportError:
        text = (
            "⏱️ <b>Bot Status</b>\n\n"
            f"🟢 Status: <b>Online</b>\n\n"
            "⚠️ <b>Note:</b> Install <code>psutil</code> for system stats\n"
            "Run: <code>pip install psutil</code>"
        )
        await update.message.reply_text(text, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users - usage: /broadcast <message>"""
    if not await check_admin(update):
        return
    
    args = update.message.text.split(None, 1)
    if len(args) < 2:
        return await update.message.reply_text(
            "❌ <b>Usage:</b> /broadcast <message>\n\n"
            "<b>Example:</b> /broadcast Hello everyone! Check out new features!\n\n"
            "💡 <b>Tips:</b>\n"
            "• Message will be sent to all active users\n"
            "• HTML formatting is supported\n"
            "• Emojis work great too! 🎉",
            parse_mode="HTML"
        )
    
    message_text = args[1]
    
    # Show confirmation
    confirm_text = (
        "📢 <b>Broadcast Confirmation</b>\n\n"
        f"<b>Message to send:</b>\n"
        f"{message_text}\n\n"
        f"👥 Total Users: <b>{get_total_users()}</b>\n\n"
        "⚠️ This action cannot be undone!\n"
        "Proceeding... Messages will be sent now."
    )
    msg = await update.message.reply_text(confirm_text, parse_mode="HTML")
    
    try:
        # Get all user IDs from database
        from database import db
        users_collection = db.get_collection("users")
        all_users = users_collection.find({}, {"user_id": 1})
        
        user_ids = [user["user_id"] for user in all_users if "user_id" in user]
        
        if not user_ids:
            await msg.edit_text(
                "❌ <b>No Users Found</b>\n\n"
                "There are no users in the database to broadcast to.",
                parse_mode="HTML"
            )
            return
        
        # Send message to all users
        sent = 0
        failed = 0
        
        for user_id in user_ids:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 <b>Announcement from Admin</b>\n\n{message_text}",
                    parse_mode="HTML"
                )
                sent += 1
            except Exception as e:
                logger.warning(f"Could not send broadcast to user {user_id}: {e}")
                failed += 1
        
        # Show final status
        result_text = (
            "✅ <b>Broadcast Completed!</b>\n\n"
            f"📤 <b>Messages Sent:</b> {sent}\n"
            f"❌ <b>Failed:</b> {failed}\n"
            f"👥 <b>Total Users:</b> {sent + failed}\n\n"
            f"Success Rate: <b>{(sent/(sent+failed)*100):.1f}%</b>"
        )
        
        await msg.edit_text(result_text, parse_mode="HTML")
        
        # Log broadcast
        import os
        LOG_CHANNEL_ID = os.environ.get("LOG_CHANNEL_ID")
        if LOG_CHANNEL_ID:
            log_text = (
                f"📢 <b>Broadcast Sent</b>\n\n"
                f"👤 Admin: @{update.message.from_user.username or update.message.from_user.id}\n"
                f"📤 Messages Sent: {sent}\n"
                f"❌ Failed: {failed}\n"
                f"📝 Message:\n{message_text}"
            )
            await send_log(context, log_text)
        
    except Exception as e:
        await msg.edit_text(
            f"❌ <b>Broadcast Failed</b>\n\n"
            f"Error: {str(e)[:100]}\n\n"
            "Check logs for details.",
            parse_mode="HTML"
        )
        logger.error(f"Broadcast error: {e}", exc_info=True)
