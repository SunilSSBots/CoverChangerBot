# Join Our Telegram Channel :- @SSBotsUpdates
# Subscribe YouTube Channel For More Bots Updates :- SunilWebTricks
# Ask Doubt Contact Me On telegram @Sunil_Sharma_2_0_Bot

"""
Admin Panel and Management Handlers for CoverChangerBot
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import (
    is_admin, is_user_banned, ban_user, unban_user,
    get_total_users, get_banned_users_count, get_stats,
    log_user_banned, log_user_unbanned, format_log_message
)

logger = logging.getLogger(__name__)


async def admin_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command /admin to open admin panel"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return await update.message.reply_text("❌ <b>𝐀ᴄᴄᴇss 𝐃ᴇɴɪᴇᴅ:</b> 𝐘ᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ.", parse_mode="HTML")
    
    total = get_total_users()
    banned = get_banned_users_count()
    active = total - banned
    
    text = (
        "🛡️ <b>𝐀ᴅᴍɪɴ 𝐂ᴏɴᴛʀᴏʟ 𝐏ᴀɴᴇʟ</b>\n\n"
        f"📊 <b>𝐓ᴏᴛᴀʟ 𝐔sᴇʀs:</b> <code>{total}</code>\n"
        f"✅ <b>𝐀ᴄᴛɪᴠᴇ 𝐔sᴇʀs:</b> <code>{active}</code>\n"
        f"🚫 <b>𝐁ᴀɴɴᴇᴅ 𝐔sᴇʀs:</b> <code>{banned}</code>\n\n"
        "<i>𝐒ᴇʟᴇᴄᴛ ᴀɴ ᴀᴄᴛɪᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴛʜᴇ ʙᴏᴛ:</i>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 𝐃ᴇᴛᴀɪʟᴇᴅ 𝐒ᴛᴀᴛs", callback_data="admin_stats")],
        [InlineKeyboardButton("⬅️ 𝐂ʟᴏsᴇ 𝐏ᴀɴᴇʟ", callback_data="menu_back")]
    ])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /ban <user_id> [reason]"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return await update.message.reply_text("❌ <b>𝐀ᴄᴄᴇss 𝐃ᴇɴɪᴇᴅ</b>", parse_mode="HTML")
    
    if not context.args:
        return await update.message.reply_text("ℹ️ <b>𝐔sᴀɢᴇ:</b> <code>/ban &lt;user_id&gt; [reason]</code>", parse_mode="HTML")
    
    try:
        target_uid = int(context.args[0])
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Banned by admin"
        ban_user(target_uid, reason)
        await update.message.reply_text(f"🚫 𝐔sᴇʀ <code>{target_uid}</code> ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ.\n<b>𝐑ᴇᴀsᴏɴ:</b> {reason}", parse_mode="HTML")
    except ValueError:
        await update.message.reply_text("❌ 𝐈ɴᴠᴀʟɪᴅ 𝐔sᴇʀ 𝐈𝐃.", parse_mode="HTML")


async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /unban <user_id>"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return await update.message.reply_text("❌ <b>𝐀ᴄᴄᴇss 𝐃ᴇɴɪᴇᴅ</b>", parse_mode="HTML")
    
    if not context.args:
        return await update.message.reply_text("ℹ️ <b>𝐔sᴀɢᴇ:</b> <code>/unban &lt;user_id&gt;</code>", parse_mode="HTML")
    
    try:
        target_uid = int(context.args[0])
        unban_user(target_uid)
        await update.message.reply_text(f"✅ 𝐔sᴇʀ <code>{target_uid}</code> ʜᴀs ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.", parse_mode="HTML")
    except ValueError:
        await update.message.reply_text("❌ 𝐈ɴᴠᴀʟɪᴅ 𝐔sᴇʀ 𝐈𝐃.", parse_mode="HTML")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /stats for bot statistics"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return await update.message.reply_text("❌ <b>𝐀ᴄᴄᴇss 𝐃ᴇɴɪᴇᴅ</b>", parse_mode="HTML")
    
    stats = get_stats()
    text = (
        "📊 <b>𝐁ᴏᴛ 𝐒ᴛᴀᴛɪsᴛɪᴄs</b>\n\n"
        f"👥 <b>𝐓ᴏᴛᴀʟ 𝐔sᴇʀs:</b> <code>{stats.get('total_users', 0)}</code>\n"
        f"🚫 <b>𝐁ᴀɴɴᴇᴅ 𝐔sᴇʀs:</b> <code>{stats.get('banned_users', 0)}</code>\n"
        f"✅ <b>𝐀ᴄᴛɪᴠᴇ 𝐔sᴇʀs:</b> <code>{stats.get('active_users', 0)}</code>\n"
        f"🖼️ <b>𝐓ᴏᴛᴀʟ 𝐓ʜᴜᴍʙɴᴀɪʟs 𝐒ᴀᴠᴇᴅ:</b> <code>{stats.get('total_thumbnails', 0)}</code>"
    )
    await update.message.reply_text(text, parse_mode="HTML")
