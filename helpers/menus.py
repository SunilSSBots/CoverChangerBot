"""
Menu and UI Layout Handlers for CoverChangerBot
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from config import HOME_MENU_BANNER_URL, OWNER_USERNAME
from database import (
    has_thumbnail, get_font_style, get_destination_channel,
    get_send_mode, is_admin
)
from fonts import get_font_name, format_caption, FONT_STYLES

logger = logging.getLogger(__name__)


def get_home_menu_markup(user_id: int) -> InlineKeyboardMarkup:
    """Build home menu keyboard with role-based buttons"""
    kb_rows = [
        [InlineKeyboardButton("❓ 𝐇ᴇʟᴘ", callback_data="menu_help"),
         InlineKeyboardButton("ℹ️ 𝐀ʙᴏᴜᴛ", callback_data="menu_about")],
        [InlineKeyboardButton("⚙️ 𝐒ᴇᴛᴛɪɴɢs", callback_data="menu_settings"),
         InlineKeyboardButton("👨‍💻 𝐃ᴇᴠᴇʟᴏᴘᴇʀ", callback_data="menu_developer")]
    ]
    if is_admin(user_id):
        kb_rows.append([InlineKeyboardButton("🛡️ 𝐀ᴅᴍɪɴ 𝐏ᴀɴᴇʟ", callback_data="admin_back")])
    return InlineKeyboardMarkup(kb_rows)


def get_home_menu_text() -> str:
    """Get home menu display text"""
    return (
        "<b>𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ 𝐈ɴsᴛᴀɴᴛ 𝐂ᴏᴠᴇʀ 𝐁ᴏᴛ</b>\n\n"
        "🎬 <b>𝐏ʀᴏꜰᴇssɪᴏɴᴀʟ 𝐕ɪᴅᴇᴏ 𝐂ᴏᴠᴇʀ 𝐓ᴏᴏʟ</b>\n\n"
        "⚡ <b>𝐐ᴜɪᴄᴋ 𝐒ᴛᴀʀᴛ:</b>\n\n"
        "📸 <b>𝐔ᴘʟᴏᴀᴅ 𝐏ʜᴏᴛᴏ</b>\n"
        "   𝐘ᴏᴜʀ ᴛʜᴜᴍʙɴᴀɪʟ sᴀᴠᴇs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ\n\n"
        "🎥 <b>𝐒ᴇɴᴅ 𝐕ɪᴅᴇᴏ</b>\n"
        "   𝐓ʜᴜᴍʙɴᴀɪʟ ᴀᴘᴘʟɪᴇs ɪɴsᴛᴀɴᴛʟʏ\n\n"
        "🌟 <b>𝐊ᴇʏ 𝐅ᴇᴀᴛᴜʀᴇs:</b>\n"
        "✅ 𝐎ɴᴇ-𝐂ʟɪᴄᴋ 𝐀ᴘᴘʟɪᴄᴀᴛɪᴏɴ\n"
        "✅ 𝐇ɪɢʜ-𝐐ᴜᴀʟɪᴛʏ 𝐂ᴏᴠᴇʀs\n"
        "✅ 𝟏𝟑+ 𝐂ᴀᴘᴛɪᴏɴ 𝐅ᴏɴᴛ 𝐒ᴛʏʟᴇs\n"
        "✅ 𝐀ᴜᴛᴏ-𝐒ᴇɴᴅ 𝐓ᴏ 𝐂ʜᴀɴɴᴇʟ\n\n"
        "💡 <b>𝐂ᴏᴍᴍᴀɴᴅs:</b>\n"
        "/help – 𝐂ᴏᴍᴘʟᴇᴛᴇ 𝐆ᴜɪᴅᴇ\n"
        "/settings – 𝐌ᴀɴᴀɢᴇ 𝐂ᴏɴᴛᴇɴᴛ\n"
        "/fonts – 𝐂ᴀᴘᴛɪᴏɴ 𝐅ᴏɴᴛs\n"
        "/channel – 𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ"
    )


def get_settings_menu(user_id: int):
    """Build settings menu text & keyboard"""
    thumb_status = "✅ 𝐒ᴀᴠᴇᴅ" if has_thumbnail(user_id) else "❌ 𝐍ᴏᴛ 𝐒ᴀᴠᴇᴅ"
    font_key = get_font_style(user_id)
    font_name = get_font_name(font_key)
    dest_chan = get_destination_channel(user_id)
    send_mode = get_send_mode(user_id)
    
    mode_str = "📤 𝐁ᴏᴛʜ (𝐂ʜᴀᴛ + 𝐂ʜᴀɴɴᴇʟ)" if send_mode == "both" else ("📢 𝐂ʜᴀɴɴᴇʟ 𝐎ɴʟʏ" if send_mode == "channel_only" else "👤 𝐂ʜᴀᴛ 𝐎ɴʟʏ")
    chan_str = f"✅ {dest_chan.get('channel_title', 'Channel')}" if dest_chan else "❌ 𝐍ᴏᴛ 𝐂ᴏɴꜰɪɢᴜʀᴇᴅ"

    text = (
        "⚙️ <b>𝐁ᴏᴛ 𝐒ᴇᴛᴛɪɴɢs & 𝐏ʀᴇꜰᴇʀᴇɴᴄᴇs</b>\n\n"
        f"👤 <b>𝐔sᴇʀ 𝐈𝐃:</b> <code>{user_id}</code>\n\n"
        f"🖼️ <b>𝐓ʜᴜᴍʙɴᴀɪʟ:</b> {thumb_status}\n"
        f"✍️ <b>𝐂ᴀᴘᴛɪᴏɴ 𝐅ᴏɴᴛ:</b> <code>{font_name}</code>\n"
        f"📢 <b>𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ:</b> {chan_str}\n"
        f"📤 <b>𝐃ᴇʟɪᴠᴇʀʏ 𝐌ᴏᴅᴇ:</b> <code>{mode_str}</code>\n\n"
        "𝐒ᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴꜰɪɢᴜʀᴇ:"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 𝐓ʜᴜᴍʙɴᴀɪʟ", callback_data="submenu_thumbnails"),
         InlineKeyboardButton("✍️ 𝐂ᴀᴘᴛɪᴏɴ 𝐅ᴏɴᴛ", callback_data="submenu_fonts")],
        [InlineKeyboardButton("📢 𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ", callback_data="submenu_channel")],
        [InlineKeyboardButton("⬅️ 𝐁ᴀᴄᴋ", callback_data="menu_back")]
    ])
    return text, kb


def get_fonts_menu(user_id: int):
    """Build fonts selection menu"""
    current_font = get_font_style(user_id)
    font_name = get_font_name(current_font)
    sample_preview = format_caption("Movie Name (2024) [1080p Web-DL]", current_font)
    
    text = (
        "✍️ <b>𝐂ᴀᴘᴛɪᴏɴ 𝐅ᴏɴᴛ 𝐒ᴛʏʟᴇ 𝐒ᴇᴛᴛɪɴɢs</b>\n\n"
        f"<b>𝐂ᴜʀʀᴇɴᴛ 𝐅ᴏɴᴛ:</b> <code>{font_name}</code>\n\n"
        f"<b>𝐋ɪᴠᴇ 𝐏ʀᴇᴠɪᴇᴡ:</b>\n"
        f"<blockquote>{sample_preview}</blockquote>\n\n"
        "<i>𝐂ʟɪᴄᴋ ᴀɴʏ ꜰᴏɴᴛ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀᴘᴘʟʏ ɪᴛ:</i>"
    )
    
    font_buttons = []
    row = []
    for s in FONT_STYLES:
        is_active = (s["key"] == current_font)
        btn_text = f"✅ {s['name']}" if is_active else s["name"]
        row.append(InlineKeyboardButton(btn_text, callback_data=f"set_font_{s['key']}"))
        if len(row) == 2:
            font_buttons.append(row)
            row = []
    if row:
        font_buttons.append(row)
    font_buttons.append([InlineKeyboardButton("⬅️ 𝐁ᴀᴄᴋ 𝐓ᴏ 𝐒ᴇᴛᴛɪɴɢs", callback_data="menu_settings")])
    
    return text, InlineKeyboardMarkup(font_buttons)


def get_channel_menu(user_id: int):
    """Build destination channel menu"""
    dest_chan = get_destination_channel(user_id)
    send_mode = get_send_mode(user_id)
    mode_label = "📤 𝐁ᴏᴛʜ (𝐂ʜᴀᴛ + 𝐂ʜᴀɴɴᴇʟ)" if send_mode == "both" else ("📢 𝐂ʜᴀɴɴᴇʟ 𝐎ɴʟʏ" if send_mode == "channel_only" else "👤 𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ 𝐎ɴʟʏ")
    
    if dest_chan:
        chan_id = dest_chan.get("channel_id", "Unknown")
        chan_title = dest_chan.get("channel_title", "Channel")
        chan_user = dest_chan.get("channel_username", "")
        user_disp = f" (@{chan_user})" if chan_user else ""
        
        text = (
            "📢 <b>𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ 𝐒ᴇᴛᴛɪɴɢs</b>\n\n"
            f"✅ <b>𝐒ᴛᴀᴛᴜs:</b> 𝐂ᴏɴɴᴇᴄᴛᴇᴅ & 𝐀ᴄᴛɪᴠᴇ\n"
            f"📢 <b>𝐂ʜᴀɴɴᴇʟ:</b> <b>{chan_title}</b>{user_disp}\n"
            f"🆔 <b>𝐂ʜᴀɴɴᴇʟ 𝐈𝐃:</b> <code>{chan_id}</code>\n"
            f"📤 <b>𝐃ᴇʟɪᴠᴇʀʏ 𝐌ᴏᴅᴇ:</b> <code>{mode_label}</code>\n\n"
            "💡 <i>𝐖ʜᴇɴ ʏᴏᴜ sᴇɴᴅ ᴀɴʏ ᴠɪᴅᴇᴏ, ɪᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴘᴘʟʏ ʏᴏᴜʀ ᴛʜᴜᴍʙɴᴀɪʟ & ꜰᴏɴᴛ ᴀɴᴅ sᴇɴᴅ ᴛᴏ ᴛʜɪs ᴄʜᴀɴɴᴇʟ!</i>"
        )
        chan_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🔄 𝐌ᴏᴅᴇ: {mode_label}", callback_data="chan_toggle_mode")],
            [InlineKeyboardButton("🧪 𝐓ᴇsᴛ 𝐂ᴏɴɴᴇᴄᴛɪᴏɴ", callback_data="chan_test"),
             InlineKeyboardButton("🔄 𝐂ʜᴀɴɢᴇ 𝐂ʜᴀɴɴᴇʟ", callback_data="chan_set_prompt")],
            [InlineKeyboardButton("🗑️ 𝐑ᴇᴍᴏᴠᴇ 𝐂ʜᴀɴɴᴇʟ", callback_data="chan_delete")],
            [InlineKeyboardButton("⬅️ 𝐁ᴀᴄᴋ 𝐓ᴏ 𝐒ᴇᴛᴛɪɴɢs", callback_data="menu_settings")]
        ])
    else:
        text = (
            "📢 <b>𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ 𝐒ᴇᴛᴛɪɴɢs</b>\n\n"
            "❌ <b>𝐒ᴛᴀᴛᴜs:</b> 𝐍ᴏᴛ 𝐂ᴏɴɴᴇᴄᴛᴇᴅ\n\n"
            "<b>🚀 𝐖ʜᴀᴛ 𝐈s 𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ?</b>\n"
            "𝐂ᴏɴɴᴇᴄᴛ ʏᴏᴜʀ 𝐓ᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ. 𝐖ʜᴇɴ ʏᴏᴜ sᴇɴᴅ ᴠɪᴅᴇᴏs ᴛᴏ ᴛʜɪs ʙᴏᴛ, ɪᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴘᴘʟɪᴇs ʏᴏᴜʀ ᴛʜᴜᴍʙɴᴀɪʟ ᴄᴏᴠᴇʀ, ᴄᴜsᴛᴏᴍ ꜰᴏɴᴛ ᴄᴀᴘᴛɪᴏɴ, ᴀɴᴅ ᴘᴏsᴛs ᴛʜᴇ ʀᴇᴀᴅʏ ᴠɪᴅᴇᴏ ᴅɪʀᴇᴄᴛʟʏ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ!\n\n"
            "<b>📋 𝐐ᴜɪᴄᴋ 𝐒ᴇᴛᴜᴘ:</b>\n"
            "1️⃣ 𝐀ᴅᴅ ᴛʜɪs ʙᴏᴛ ᴀs ᴀɴ <b>𝐀ᴅᴍɪɴ</b> ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜ <i>𝐏ᴏsᴛ 𝐌ᴇssᴀɢᴇs</i> ᴘᴇʀᴍɪssɪᴏɴ.\n"
            "2️⃣ 𝐂ʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ."
        )
        chan_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ 𝐂ᴏɴɴᴇᴄᴛ 𝐂ʜᴀɴɴᴇʟ", callback_data="chan_set_prompt")],
            [InlineKeyboardButton("⬅️ 𝐁ᴀᴄᴋ 𝐓ᴏ 𝐒ᴇᴛᴛɪɴɢs", callback_data="menu_settings")]
        ])
    return text, chan_kb
