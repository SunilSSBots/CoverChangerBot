# Join Our Telegram Channel :- @SSBotsUpdates
# Subscribe YouTube Channel For More Bots Updates :- SunilWebTricks
# Ask Doubt Contact Me On telegram @Sunil_Sharma_2_0_Bot

"""
Message, Photo, Video, and Channel Linking Handlers for CoverChangerBot
"""

import os
import logging
from telegram import Update, InputMediaVideo, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from config import LOG_CHANNEL_ID, HOME_MENU_BANNER_URL
from database import (
    save_thumbnail, get_thumbnail, delete_thumbnail, has_thumbnail,
    save_destination_channel, get_destination_channel,
    get_font_style, get_send_mode,
    log_thumbnail_set, log_thumbnail_removed, format_log_message
)
from fonts import format_caption, get_font_name
from helpers.menus import (
    get_home_menu_text, get_home_menu_markup,
    get_settings_menu, get_fonts_menu, get_channel_menu
)

logger = logging.getLogger(__name__)


def bold_entities(text: str):
    """Generate bold entity for telegram caption"""
    from telegram import MessageEntity
    if not text:
        return []
    return [MessageEntity(type=MessageEntity.BOLD, offset=0, length=len(text))]


async def send_log(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Send log event to configured log channel"""
    if LOG_CHANNEL_ID:
        try:
            await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=message, parse_mode="HTML")
        except Exception as e:
            logger.debug(f"Log send error: {e}")


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /start handler"""
    user_id = update.effective_user.id
    text = get_home_menu_text()
    kb = get_home_menu_markup(user_id)
    banner = HOME_MENU_BANNER_URL

    if banner:
        try:
            photo = InputFile(banner) if isinstance(banner, str) and os.path.isfile(banner) else banner
            return await update.message.reply_photo(photo=photo, caption=text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
    await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /help handler"""
    text = (
        "📖 <b>𝐂ᴏᴍᴘʟᴇᴛᴇ 𝐆ᴜɪᴅᴇ & 𝐅ᴇᴀᴛᴜʀᴇs</b>\n\n"
        "<b>1️⃣ 𝐔ᴘʟᴏᴀᴅ 𝐘ᴏᴜʀ 𝐓ʜᴜᴍʙɴᴀɪʟ</b>\n"
        "   • 𝐒ᴇɴᴅ ᴀɴʏ ᴘʜᴏᴛᴏ ᴛᴏ sᴀᴠᴇ ɪᴛ ᴀs ʏᴏᴜʀ ᴠɪᴅᴇᴏ ᴄᴏᴠᴇʀ.\n\n"
        "<b>2️⃣ 𝐂ʜᴏᴏsᴇ 𝐘ᴏᴜʀ 𝐂ᴀᴘᴛɪᴏɴ 𝐅ᴏɴᴛ</b>\n"
        "   • 𝐆ᴏ ᴛᴏ /fonts ᴛᴏ sᴇʟᴇᴄᴛ ꜰʀᴏᴍ 𝟏𝟑+ sᴛʏʟɪsʜ ꜰᴏɴᴛs.\n\n"
        "<b>3️⃣ 𝐒ᴇᴛ 𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ (𝐎ᴘᴛɪᴏɴᴀʟ)</b>\n"
        "   • 𝐆ᴏ ᴛᴏ /channel ᴛᴏ ʟɪɴᴋ ʏᴏᴜʀ 𝐓ᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ.\n"
        "   • 𝐀ᴅᴅ ᴛʜɪs ʙᴏᴛ ᴀs ᴀɴ 𝐀ᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ.\n\n"
        "<b>4️⃣ 𝐒ᴇɴᴅ 𝐘ᴏᴜʀ 𝐕ɪᴅᴇᴏs</b>\n"
        "   • 𝐒ᴇɴᴅ ᴀɴʏ ᴠɪᴅᴇᴏ ꜰɪʟᴇ.\n"
        "   • 𝐓ʜᴜᴍʙɴᴀɪʟ ᴀɴᴅ ꜰᴏɴᴛ ᴀʀᴇ ᴀᴘᴘʟɪᴇᴅ ɪɴsᴛᴀɴᴛʟʏ ᴀɴᴅ ᴀᴜᴛᴏ-sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ!\n\n"
        "<b>💡 𝐂ᴏᴍᴍᴀɴᴅs:</b>\n"
        "/start – 𝐌ᴀɪɴ 𝐌ᴇɴᴜ\n"
        "/settings – 𝐂ᴏɴꜰɪɢᴜʀᴇ 𝐒ᴇᴛᴛɪɴɢs\n"
        "/fonts – 𝐂ᴀᴘᴛɪᴏɴ 𝐅ᴏɴᴛ 𝐒ᴛʏʟᴇ\n"
        "/channel – 𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ\n"
        "/remove – 𝐃ᴇʟᴇᴛᴇ 𝐒ᴀᴠᴇᴅ 𝐓ʜᴜᴍʙɴᴀɪʟ\n\n"
        "📢 <b>𝐔ᴘᴅᴀᴛᴇs 𝐂ʜᴀɴɴᴇʟ:</b> @SSBotsUpdates\n"
        "📺 <b>𝐘ᴏᴜ𝐓ᴜʙᴇ 𝐂ʜᴀɴɴᴇʟ:</b> SunilWebTricks\n"
        "💬 <b>𝐒ᴜᴘᴘᴏʀᴛ & 𝐃ᴏᴜʙᴛs:</b> @Sunil_Sharma_2_0_Bot"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/SSBotsUpdates"),
         InlineKeyboardButton("📺 𝐘ᴏᴜ𝐓ᴜʙᴇ", url="https://youtube.com/@SunilWebTricks")],
        [InlineKeyboardButton("💬 𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/Sunil_Sharma_2_0_Bot")]
    ])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /about handler"""
    text = (
        "🤖 <b>𝐀ʙᴏᴜᴛ 𝐓ʜɪs 𝐁ᴏᴛ</b>\n\n"
        "<b>𝐏ʀᴏꜰᴇssɪᴏɴᴀʟ 𝐕ɪᴅᴇᴏ 𝐂ᴏᴠᴇʀ & 𝐂ʜᴀɴɴᴇʟ 𝐀ᴜᴛᴏᴍᴀᴛɪᴏɴ 𝐓ᴏᴏʟ</b>\n\n"
        "✨ <b>𝐅ᴇᴀᴛᴜʀᴇs:</b>\n"
        "✅ 𝐈ɴsᴛᴀɴᴛ 𝐓ʜᴜᴍʙɴᴀɪʟ 𝐑ᴇᴘʟᴀᴄᴇᴍᴇɴᴛ\n"
        "✅ 𝟏𝟑+ 𝐂ᴀᴘᴛɪᴏɴ 𝐅ᴏɴᴛ 𝐒ᴛʏʟᴇs\n"
        "✅ 𝐀ᴜᴛᴏ-sᴇɴᴅ ᴛᴏ 𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ\n"
        "✅ 𝐇ɪɢʜ 𝐒ᴘᴇᴇᴅ 𝐂ʟᴏᴜᴅ 𝐏ʀᴏᴄᴇssɪɴɢ\n\n"
        "📢 <b>𝐎ꜰꜰɪᴄɪᴀʟ 𝐔ᴘᴅᴀᴛᴇs:</b> @SSBotsUpdates\n"
        "📺 <b>𝐘ᴏᴜ𝐓ᴜʙᴇ 𝐂ʜᴀɴɴᴇʟ:</b> SunilWebTricks\n"
        "💬 <b>𝐀sᴋ 𝐃ᴏᴜʙᴛ 𝐂ᴏɴᴛᴀᴄᴛ:</b> @Sunil_Sharma_2_0_Bot"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝐔ᴘᴅᴀᴛᴇs 𝐂ʜᴀɴɴᴇʟ", url="https://t.me/SSBotsUpdates"),
         InlineKeyboardButton("📺 𝐘ᴏᴜ𝐓ᴜʙᴇ", url="https://youtube.com/@SunilWebTricks")],
        [InlineKeyboardButton("💬 𝐂ᴏɴᴛᴀᴄᴛ & 𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/Sunil_Sharma_2_0_Bot")]
    ])
    await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /settings handler"""
    user_id = update.effective_user.id
    text, kb = get_settings_menu(user_id)
    await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def fonts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /fonts handler"""
    user_id = update.effective_user.id
    text, kb = get_fonts_menu(user_id)
    await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def channel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /channel handler"""
    user_id = update.effective_user.id
    text, kb = get_channel_menu(user_id)
    await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")


async def remove_thumbnail_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /remove to delete thumbnail"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    if delete_thumbnail(user_id):
        log_data = log_thumbnail_removed(user_id, username)
        log_msg = format_log_message(user_id, username, log_data["action"])
        await send_log(context, log_msg)
        return await update.message.reply_text("✅ <b>𝐓ʜᴜᴍʙɴᴀɪʟ 𝐃ᴇʟᴇᴛᴇᴅ 𝐒ᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n𝐒ᴇɴᴅ ᴀ ɴᴇᴡ ᴘʜᴏᴛᴏ ᴀɴʏᴛɪᴍᴇ.", parse_mode="HTML")
    await update.message.reply_text("⚠️ <b>𝐍ᴏ 𝐒ᴀᴠᴇᴅ 𝐓ʜᴜᴍʙɴᴀɪʟ 𝐅ᴏᴜɴᴅ.</b>", parse_mode="HTML")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save received photo as user thumbnail"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    photo_id = update.message.photo[-1].file_id
    
    is_replace = has_thumbnail(user_id)
    save_thumbnail(user_id, photo_id)
    
    log_data = log_thumbnail_set(user_id, username, is_replace=is_replace)
    log_msg = format_log_message(user_id, username, log_data["action"])
    await send_log(context, log_msg)
    
    action = "Updated" if is_replace else "Saved"
    await update.message.reply_text(f"✅ <b>𝐓ʜᴜᴍʙɴᴀɪʟ {action}!</b>\n\n𝐍ᴏᴡ sᴇɴᴅ ᴀɴʏ ᴠɪᴅᴇᴏ ᴛᴏ ᴀᴘᴘʟʏ ᴛʜɪs ᴄᴏᴠᴇʀ.", parse_mode="HTML")


async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process video file: attach thumbnail, styled font, and send to destinations"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "No Username"
    cover = get_thumbnail(user_id)
    
    if not cover:
        return await update.message.reply_text("❌ <b>𝐍ᴏ 𝐓ʜᴜᴍʙɴᴀɪʟ 𝐅ᴏᴜɴᴅ!</b>\n𝐏ʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ꜰɪʀsᴛ ᴛᴏ sᴀᴠᴇ ᴀs ʏᴏᴜʀ ᴄᴏᴠᴇʀ.", parse_mode="HTML")
    
    status_msg = await update.message.reply_text("⏳ <b>𝐏ʀᴏᴄᴇssɪɴɢ 𝐕ɪᴅᴇᴏ...</b>\n𝐏ʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ.", parse_mode="HTML")
    
    if update.message.video:
        video_id = update.message.video.file_id
    elif update.message.document:
        video_id = update.message.document.file_id
    else:
        return
    
    # 1. Apply Caption & Font Style
    font_style = get_font_style(user_id)
    original_caption = update.message.caption or ""
    new_caption = format_caption(original_caption, font_style) if original_caption else ""
    caption_entities = bold_entities(new_caption) if font_style == "bold" and new_caption else None
    
    dest_chan = get_destination_channel(user_id)
    send_mode = get_send_mode(user_id)
    
    media = InputMediaVideo(media=video_id, caption=new_caption, caption_entities=caption_entities, supports_streaming=True, cover=cover)
    
    try:
        sent_to_user = False
        if send_mode in ("both", "user_only") or not dest_chan:
            await context.bot.edit_message_media(chat_id=update.effective_chat.id, message_id=status_msg.message_id, media=media)
            sent_to_user = True
            
        dest_success = False
        if dest_chan and send_mode in ("both", "channel_only"):
            try:
                dest_chat_id = dest_chan["channel_id"]
                await context.bot.send_video(
                    chat_id=dest_chat_id,
                    video=video_id,
                    caption=new_caption,
                    caption_entities=caption_entities,
                    supports_streaming=True,
                    thumbnail=cover
                )
                dest_success = True
            except Exception as chan_err:
                logger.error(f"Error posting to channel: {chan_err}")
                await update.message.reply_text(
                    f"⚠️ <b>𝐂ʜᴀɴɴᴇʟ 𝐏ᴏsᴛɪɴɢ 𝐍ᴏᴛɪᴄᴇ:</b>\n<code>{str(chan_err)[:120]}</code>\n\nEnsure bot is Admin with 'Post Messages' rights in your channel.",
                    parse_mode="HTML"
                )
        
        if not sent_to_user and dest_success:
            chan_title = dest_chan.get("channel_title", "Channel")
            await status_msg.edit_text(f"✅ <b>𝐕ɪᴅᴇᴏ 𝐏ʀᴏᴄᴇssᴇᴅ!</b>\n\n𝐏ᴏsᴛᴇᴅ ᴅɪʀᴇᴄᴛʟʏ ᴛᴏ: <b>{chan_title}</b>", parse_mode="HTML")
        elif sent_to_user and dest_success:
            chan_title = dest_chan.get("channel_title", "Channel")
            await update.message.reply_text(f"📢 <i>𝐀ʟsᴏ ᴘᴏsᴛᴇᴅ ᴛᴏ: <b>{chan_title}</b></i>", parse_mode="HTML")
            
        if LOG_CHANNEL_ID:
            try:
                log_caption = (
                    f"🎥 <b>Video Processed</b>\n"
                    f"👤 User: <code>{user_id}</code> (@{username})\n"
                    f"✍️ Font: <code>{get_font_name(font_style)}</code>\n"
                    f"📝 Caption: {original_caption or 'No Caption'}"
                )
                await context.bot.send_video(chat_id=LOG_CHANNEL_ID, video=video_id, caption=log_caption, supports_streaming=True, thumbnail=cover, parse_mode="HTML")
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Video processing failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ <b>Processing Failed:</b> <code>{str(e)[:100]}</code>", parse_mode="HTML")


async def text_and_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle channel linkage via text ID/username or forwarded message"""
    user_id = update.effective_user.id
    waiting_for = context.user_data.get("waiting_for")
    fwd_chat = getattr(update.message, "forward_from_chat", None)
    
    if waiting_for == "destination_channel" or (fwd_chat and fwd_chat.type == "channel"):
        channel_input = None
        if fwd_chat and fwd_chat.type == "channel":
            channel_input = fwd_chat.id
        elif update.message.text:
            raw = update.message.text.strip()
            if raw.lower() in ("/cancel", "cancel"):
                context.user_data.pop("waiting_for", None)
                return await update.message.reply_text("❌ <b>𝐒ᴇᴛᴜᴘ 𝐂ᴀɴᴄᴇʟʟᴇᴅ.</b>", parse_mode="HTML")
            if "t.me/" in raw:
                channel_input = "@" + raw.rstrip("/").split("/")[-1]
            elif raw.startswith("-100") or raw.startswith("-"):
                try:
                    channel_input = int(raw)
                except ValueError:
                    channel_input = raw
            elif raw.startswith("@"):
                channel_input = raw
            else:
                try:
                    channel_input = int(raw)
                except ValueError:
                    channel_input = "@" + raw

        if not channel_input:
            return
            
        verify_msg = await update.message.reply_text("🔍 <b>𝐕ᴇʀɪꜰʏɪɴɢ ᴄʜᴀɴɴᴇʟ & ᴘᴇʀᴍɪssɪᴏɴs...</b>", parse_mode="HTML")
        try:
            chat = await context.bot.get_chat(channel_input)
            bot_member = await context.bot.get_chat_member(chat_id=chat.id, user_id=context.bot.id)
            if bot_member.status not in ("administrator", "creator"):
                return await verify_msg.edit_text(
                    f"⚠️ <b>𝐁ᴏᴛ ɪs ɴᴏᴛ ᴀɴ 𝐀ᴅᴍɪɴ ɪɴ '{chat.title}'</b>\n\n𝐏ʟᴇᴀsᴇ ᴀᴅᴅ ᴛʜɪs ʙᴏᴛ ᴀs ᴀɴ 𝐀ᴅᴍɪɴ ᴡɪᴛʜ <b>'Post Messages'</b> ᴘᴇʀᴍɪssɪᴏɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.",
                    parse_mode="HTML"
                )
            
            save_destination_channel(user_id=user_id, channel_id=chat.id, channel_title=chat.title or "Channel", channel_username=chat.username or "")
            context.user_data.pop("waiting_for", None)
            
            mode_label = "📤 𝐁ᴏᴛʜ (𝐂ʜᴀᴛ + 𝐂ʜᴀɴɴᴇʟ)" if get_send_mode(user_id) == "both" else ("📢 𝐂ʜᴀɴɴᴇʟ 𝐎ɴʟʏ" if get_send_mode(user_id) == "channel_only" else "👤 𝐂ʜᴀᴛ 𝐎ɴʟʏ")
            text = (
                f"✅ <b>𝐃ᴇsᴛɪɴᴀᴛɪᴏɴ 𝐂ʜᴀɴɴᴇʟ 𝐂ᴏɴɴᴇᴄᴛᴇᴅ!</b>\n\n"
                f"📢 <b>𝐂ʜᴀɴɴᴇʟ:</b> <b>{chat.title}</b>\n"
                f"🆔 <b>𝐈𝐃:</b> <code>{chat.id}</code>\n"
                f"📤 <b>𝐃ᴇʟɪᴠᴇʀʏ 𝐌ᴏᴅᴇ:</b> <code>{mode_label}</code>\n\n"
                "🚀 <i>𝐍ᴏᴡ sᴇɴᴅ ᴀɴʏ ᴠɪᴅᴇᴏ — ɪᴛ ᴡɪʟʟ ʙᴇ ᴅᴇʟɪᴠᴇʀᴇᴅ ᴅɪʀᴇᴄᴛʟʏ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ!</i>"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🧪 𝐓ᴇsᴛ 𝐏ᴏsᴛ", callback_data="chan_test"),
                 InlineKeyboardButton(f"🔄 𝐌ᴏᴅᴇ: {mode_label}", callback_data="chan_toggle_mode")],
                [InlineKeyboardButton("⚙️ 𝐆ᴏ 𝐓ᴏ 𝐒ᴇᴛᴛɪɴɢs", callback_data="menu_settings")]
            ])
            await verify_msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception as e:
            await verify_msg.edit_text(f"❌ <b>𝐂ᴏɴɴᴇᴄᴛɪᴏɴ 𝐅ᴀɪʟᴇᴅ:</b> <code>{str(e)[:120]}</code>\n\n𝐌ᴀᴋᴇ sᴜʀᴇ ʙᴏᴛ ɪs 𝐀ᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ.", parse_mode="HTML")
