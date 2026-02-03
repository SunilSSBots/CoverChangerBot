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
        "<b>Welcome to SS Instant Cover Changer Bot</b>\n\n"
        "✨ <b>What You Can Do</b>\n"
        "📸 Upload A <b>Photo</b> As Your Thumbnail\n"
        "🎥 Send A <b>Video</b> To Apply The Cover Instantly\n\n"
        "⚡ Features \n"
        "⚙️ One-Click Thumbnail Bot\n"
        "🎨 Professional Video Covers\n"
        "📁 Automatic Thumbnail Management\n\n"
        "🧭 <b>Quick Links </b>\n"
        "/help – Learn How To Use\n"
        "/settings – Manage Your Content\n"
        "/about – About This Bot"
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
        "📖 <b>How To Use SS Instant Cover Changer Bot</b>\n\n"
        "🎯 <b>Step-By-Step Guide:</b>\n\n"
        "1️⃣ <b>Upload Your Thumbnail</b>\n"
        "   Send A Photo That You Want As Your Video Cover\n"
        "   The Photo Will Be Saved Automatically\n\n"
        "2️⃣ <b>Apply To Videos</b>\n"
        "   Send Any Video To The Bot\n"
        "   The Saved Thumbnail Will Be Applied Instantly\n\n"
        "3️⃣ <b>Download & Share</b>\n"
        "   Your Video With The Cover Is Ready To Share\n\n"
        "💡 <b>Pro Tips </b>\n"
        "• High-Quality Photos Work Best\n"
        "• Update Your Thumbnail Anytime\n"
        "• Remove Old Thumbnails From Settings\n\n"
        "❓ Need More Help? Contact Spport @Sunil_Sharma_2_0_Bot"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_sub(update, context):
        return
    text = (
        "🤖 <b>About SS Instant Cover Changer Bot</b>\n\n"
        "📝 <b>Description </b>\n"
        "A Powerful And Intuitive Tool For Applying Custom Thumbnails To Your Videos.\n\n"
        "⭐ <b>Key Features</b>\n"
        "✅ Lightning-Fast Thumbnail Application\n"
        "✅ One Photo Per User Storage\n"
        "✅ Professional Video Covers\n"
        "✅ Easy-To-Use Interface\n"
        "✅ Instant Processing\n\n"
        "🛠️ <b>Technology </b>\n"
        "Built With Python & Telegram Bot API\n"
        "Powered By @SSBotsUpdates\n\n"
        "📊 <b>Statistics </b>\n"
        f"👥 Active Users : Check With /stats\n\n"
        "💬 <b>Support & Contact :</b>\n"
        f"👨‍💻 Developer : @{OWNER_USERNAME or 'contact_owner'}\n"
        "📧 For Issues Or Suggestions, Reach Out Anytime\n\n"
        "Thank You For Using Instant Cover Bot! 🎬"
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
        "👤 <b>Your Account </b>\n"
        f"User ID : <code>{user_id}</code>\n\n"
        "🖼️ <b>Thumbnail Status </b>\n"
        f"<b>{thumb_status}</b>\n\n"
        "📋 <b>What You Can Manage </b>"
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
    await update.message.reply_text("⚠️ <b>No Thumbnail To Remove</b>\n\nYou Haven't Saved Any Thumbnail Yet. Send A Photo First!", reply_to_message_id=update.message.message_id, parse_mode="HTML")
