"""
User Commands Module
Contains all user-facing command handlers
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from database import (
    save_thumbnail, get_thumbnail, delete_thumbnail, has_thumbnail,
    log_new_user, log_thumbnail_set, log_thumbnail_removed, format_log_message
)
from helpers import check_force_sub, send_log, is_admin

logger = logging.getLogger(__name__)

# Module-level variables set by bot.py
OWNER_ID = None
FORCE_SUB_CHANNEL_ID = None
HOME_MENU_BANNER_URL = None
LOG_CHANNEL_ID = None
OWNER_USERNAME = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    first_name = update.effective_user.first_name or "User"
    
    # Log new user (if first time)
    user_check = get_thumbnail(user_id)
    if user_check is None:
        # New user - log it
        log_data = log_new_user(user_id, username, first_name)
        log_msg = format_log_message(user_id, username, log_data["action"], log_data.get("details", ""))
        await send_log(context, log_msg)
    
    # Check force-sub first
    if not await check_force_sub(update, context):
        logger.warning(f"❌ User {user_id} blocked by force-sub check")
        return
    
    text = (
        "<b>Welcome to Instant Cover Bot</b>\n\n"
        "🎬 <b>Professional Video Cover Tool</b>\n\n"
        "✨ <b>What you can do:</b>\n"
        "📸 Upload a <b>photo</b> as your thumbnail\n"
        "🎥 Send a <b>video</b> to apply the cover instantly\n\n"
        "⚡ Features:\n"
        "⚙️ One-click thumbnail application\n"
        "🎨 Professional video covers\n"
        "📁 Automatic thumbnail management\n\n"
        "🧭 <b>Quick Links:</b>\n"
        "/help – Learn how to use\n"
        "/settings – Manage your content\n"
        "/about – About this bot"
    )
    # Build home menu with all buttons
    kb_rows = [
        [InlineKeyboardButton("❓ Help", callback_data="menu_help"),
         InlineKeyboardButton("ℹ️ About", callback_data="menu_about")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
         InlineKeyboardButton("👨‍💻 Developer", callback_data="menu_developer")],
    ]
    
    # Add admin panel button if user is admin
    if is_admin(user_id):
        kb_rows.append([InlineKeyboardButton("🛡️ Admin Panel", callback_data="admin_back")])
    
    kb = InlineKeyboardMarkup(kb_rows)
    banner = HOME_MENU_BANNER_URL
    
    # Handle both callback_query and regular message
    if update.callback_query:
        msg = update.callback_query.message
        if banner:
            try:
                if isinstance(banner, str) and os.path.isfile(banner):
                    photo = InputFile(banner)
                else:
                    photo = banner
                if getattr(msg, "photo", None):
                    await msg.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
                else:
                    try:
                        await msg.delete()
                    except Exception:
                        pass
                    await msg.chat.send_photo(photo=photo, caption=text, reply_markup=kb, parse_mode="HTML")
            except Exception:
                await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
        else:
            await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        if banner:
            try:
                if isinstance(banner, str) and os.path.isfile(banner):
                    await update.message.reply_photo(photo=InputFile(banner), caption=text, reply_markup=kb, parse_mode="HTML")
                else:
                    await update.message.reply_photo(photo=banner, caption=text, reply_markup=kb, parse_mode="HTML")
                return
            except Exception:
                pass
        await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_sub(update, context):
        return
    text = (
        "📖 <b>How to Use Instant Cover Bot</b>\n\n"
        "🎯 <b>Step-by-Step Guide:</b>\n\n"
        "1️⃣ <b>Upload Your Thumbnail</b>\n"
        "   Send a photo that you want as your video cover\n"
        "   The photo will be saved automatically\n\n"
        "2️⃣ <b>Apply to Videos</b>\n"
        "   Send any video to the bot\n"
        "   The saved thumbnail will be applied instantly\n\n"
        "3️⃣ <b>Download & Share</b>\n"
        "   Your video with the cover is ready to download\n\n"
        "💡 <b>Pro Tips:</b>\n"
        "• High-quality photos work best\n"
        "• Update your thumbnail anytime\n"
        "• Remove old thumbnails from Settings\n\n"
        "❓ Need more help? Contact support or check /about"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_sub(update, context):
        return
    text = (
        "🤖 <b>About Instant Cover Bot</b>\n\n"
        "📝 <b>Description:</b>\n"
        "A powerful and intuitive tool for applying custom thumbnails to your videos.\n\n"
        "⭐ <b>Key Features:</b>\n"
        "✅ Lightning-fast thumbnail application\n"
        "✅ One photo per user storage\n"
        "✅ Professional video covers\n"
        "✅ Easy-to-use interface\n"
        "✅ Instant processing\n\n"
        "🛠️ <b>Technology:</b>\n"
        "Built with Python & Telegram Bot API\n"
        "Powered by FFmpeg for video processing\n\n"
        "📊 <b>Statistics:</b>\n"
        f"👥 Active Users: Check with /stats\n\n"
        "💬 <b>Support & Contact:</b>\n"
        f"👨‍💻 Developer: @{OWNER_USERNAME or 'contact_owner'}\n"
        "📧 For issues or suggestions, reach out anytime\n\n"
        "Thank you for using Instant Cover Bot! 🎬"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_sub(update, context):
        return
    user_id = update.message.from_user.id
    # Show thumbnail status
    thumb_status = "✅ Saved & Ready" if has_thumbnail(user_id) else "❌ Not Saved Yet"
    
    text = (
        "⚙️ <b>Settings & Preferences</b>\n\n"
        "👤 <b>Your Account:</b>\n"
        f"User ID: <code>{user_id}</code>\n\n"
        "🖼️ <b>Thumbnail Status:</b>\n"
        f"<b>{thumb_status}</b>\n\n"
        "📋 <b>What you can manage:</b>"
    )
    settings_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 Thumbnails", callback_data="submenu_thumbnails")],
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_back")]
    ])
    await update.message.reply_text(text, reply_markup=settings_kb, parse_mode="HTML")


async def remover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_sub(update, context):
        return
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Unknown"
    
    if delete_thumbnail(user_id):
        # Log thumbnail removal
        log_data = log_thumbnail_removed(user_id, username)
        log_msg = format_log_message(user_id, username, log_data["action"])
        await send_log(context, log_msg)
        
        return await update.message.reply_text("✅ <b>Thumbnail Removed Successfully</b>\n\nYour thumbnail has been deleted. Upload a new one anytime!", reply_to_message_id=update.message.message_id, parse_mode="HTML")
    await update.message.reply_text("⚠️ <b>No Thumbnail to Remove</b>\n\nYou haven't saved a thumbnail yet. Send a photo first!", reply_to_message_id=update.message.message_id, parse_mode="HTML")
