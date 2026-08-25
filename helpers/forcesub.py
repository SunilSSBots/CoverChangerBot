# Join Our Telegram Channel :- @SSBotsUpdates
# Subscribe YouTube Channel For More Bots Updates :- SunilWebTricks
# Ask Doubt Contact Me On telegram @Sunil_Sharma_2_0_Bot

"""
Force Subscribe Middleware & Verification for CoverChangerBot
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import FORCE_SUB_CHANNEL_ID, FORCE_SUB_CHANNEL_INVITE_LINK
from database import is_admin, is_user_banned

logger = logging.getLogger(__name__)


async def check_force_sub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is banned or needs to join force-sub channel"""
    user = update.effective_user
    if not user:
        return False
        
    user_id = user.id
    
    # Check if user is banned
    if is_user_banned(user_id):
        if update.message:
            await update.message.reply_text("🚫 <b>𝐘ᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.</b>", parse_mode="HTML")
        elif update.callback_query:
            await update.callback_query.answer("🚫 𝐘ᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.", show_alert=True)
        return False
        
    # Admins bypass force-sub
    if is_admin(user_id):
        return True
        
    # Check force sub if configured
    if not FORCE_SUB_CHANNEL_ID:
        return True
        
    try:
        member = await context.bot.get_chat_member(chat_id=FORCE_SUB_CHANNEL_ID, user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            return True
    except Exception as e:
        logger.debug(f"Force-sub check failed: {e}")
        return True
        
    # User hasn't joined yet — show prompt
    join_url = FORCE_SUB_CHANNEL_INVITE_LINK or "https://t.me/"
    text = (
        "🔒 <b>𝐉ᴏɪɴ 𝐎ᴜʀ 𝐂ʜᴀɴɴᴇʟ 𝐓ᴏ 𝐔sᴇ 𝐓ʜɪs 𝐁ᴏᴛ</b>\n\n"
        "𝐏ʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ's ꜰᴇᴀᴛᴜʀᴇs, ᴛʜᴇɴ ᴄʟɪᴄᴋ <b>'𝐈 ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ'</b> ʙᴇʟᴏᴡ."
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝐉ᴏɪɴ 𝐂ʜᴀɴɴᴇʟ", url=join_url)],
        [InlineKeyboardButton("🔄 𝐈 𝐇ᴀᴠᴇ 𝐉ᴏɪɴᴇᴅ", callback_data="menu_home")]
    ])
    
    if update.message:
        await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.answer("🔒 Please join our channel first!", show_alert=True)
        try:
            await update.callback_query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
    return False
