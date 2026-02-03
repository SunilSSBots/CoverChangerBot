"""
Helper Functions Module
Contains utility functions used throughout the bot
"""

import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.error import BadRequest, RetryAfter
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

logger = logging.getLogger(__name__)

OWNER_ID = None  # Will be set from bot.py
FORCE_SUB_CHANNEL_ID = None  # Will be set from bot.py
FORCE_SUB_BANNER_URL = None  # Will be set from bot.py
LOG_CHANNEL_ID = None  # Will be set from bot.py


def is_admin(user_id: int) -> bool:
    """Check if user is bot owner or admin"""
    admin_list = [OWNER_ID]
    return user_id in admin_list


async def check_admin(update: Update) -> bool:
    """Check if user is admin and send error if not"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return False
    return True


async def send_log(context: ContextTypes.DEFAULT_TYPE, log_message: str) -> bool:
    """Send log message to log channel"""
    if not LOG_CHANNEL_ID:
        logger.debug("LOG_CHANNEL_ID not configured")
        return False
    
    try:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=log_message,
            parse_mode="HTML"
        )
        logger.debug(f"✅ Log sent to channel {LOG_CHANNEL_ID}")
        return True
    except Exception as e:
        logger.error(f"❌ Error sending log to channel: {e}")
        return False


async def get_invite_link(bot, chat_id):
    """Create or return a chat invite link with rate-limit retry handling."""
    try:
        link_obj = await bot.create_chat_invite_link(chat_id=chat_id, member_limit=1)
        return getattr(link_obj, "invite_link", link_obj)
    except RetryAfter as e:
        secs = getattr(e, "retry_after", None) or 30
        logger.info(f"Rate limited while creating invite link: sleeping {secs}s")
        await asyncio.sleep(secs)
        return await get_invite_link(bot, chat_id)
    except Exception as e:
        logger.error(f"get_invite_link failed: {e}")
        return None


async def check_force_sub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user has verified through force-sub AND is still a member.
    Verifies membership for cached users to ensure they haven't left the channel.
    """
    from bot import verified_users
    
    user_id = update.effective_user.id

    # Owner bypass
    if user_id == OWNER_ID:
        return True

    # If no force-sub configured, allow access
    if not FORCE_SUB_CHANNEL_ID:
        return True

    # If user already verified through verify button, verify they're still a member
    if user_id in verified_users:
        logger.info(f"🔍 User {user_id} is cached - checking if still a member...")
        
        try:
            channel_id_str = str(FORCE_SUB_CHANNEL_ID).strip()
            
            try:
                if channel_id_str.startswith("-"):
                    channel_id = int(channel_id_str)
                else:
                    try:
                        channel_id = int(channel_id_str)
                    except ValueError:
                        channel_id = channel_id_str
            except Exception:
                channel_id = channel_id_str
            
            member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            
            if member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                logger.info(f"✅ User {user_id} is still a member - access granted")
                return True
            
            logger.warning(f"⚠️ User {user_id} left the channel - removing from cache")
            verified_users.discard(user_id)
            
        except Exception as e:
            logger.warning(f"Could not verify membership for cached user {user_id}: {e}")
            verified_users.discard(user_id)
    
    logger.info(f"🔒 User {user_id} not verified or left channel - showing join prompt")

    # User not verified - show join prompt
    try:
        channel_id_str = str(FORCE_SUB_CHANNEL_ID).strip()
        logger.info(f"📌 Channel config: {channel_id_str}")
        
        try:
            if channel_id_str.startswith("-"):
                channel_chat_id = int(channel_id_str)
            else:
                try:
                    channel_chat_id = int(channel_id_str)
                except ValueError:
                    channel_chat_id = channel_id_str
        except Exception as parse_err:
            logger.error(f"❌ Channel ID parse error: {parse_err}")
            channel_chat_id = channel_id_str

        # Get channel info
        try:
            logger.info(f"📍 Getting chat info for {channel_chat_id}")
            chat = await context.bot.get_chat(channel_chat_id)
            channel_name = chat.title or chat.username or "Channel"
            logger.info(f"✅ Got chat info: {channel_name}")
            
            invite_link = None
            if chat.username:
                invite_link = f"https://t.me/{chat.username}"
            elif hasattr(chat, 'invite_link') and chat.invite_link:
                invite_link = chat.invite_link
            
            if not invite_link:
                try:
                    link_obj = await context.bot.create_chat_invite_link(
                        chat_id=channel_chat_id, 
                        member_limit=1
                    )
                    invite_link = link_obj.invite_link
                except Exception as link_error:
                    logger.warning(f"Could not create invite link: {link_error}")
                    if str(channel_chat_id).startswith('-100'):
                        invite_link = f"https://t.me/c/{str(channel_chat_id)[4:]}"
                    else:
                        invite_link = f"https://t.me/{channel_chat_id}"
            
        except Exception as e:
            logger.error(f"Could not get chat info: {e}")
            return True

        # Build keyboard
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=invite_link)],
            [
                InlineKeyboardButton("✅ Verify", callback_data="check_fsub"),
                InlineKeyboardButton("✖️ Close", callback_data="close_banner")
            ]
        ])
        
        # Build prompt message
        prompt = (
            "🔐 <b>Channel Verification Required</b>\n\n"
            f"To access all features of this bot, you must join our community channel:\n\n"
            f"<b>📢 {channel_name}</b>\n\n"
            "We share exclusive updates, tips, and announcements there.\n\n"
            "👇 <b>Join the channel and verify to continue</b> 👇"
        )

        try:
            banner = FORCE_SUB_BANNER_URL
            
            if update.message:
                if banner:
                    try:
                        if isinstance(banner, str) and os.path.isfile(banner):
                            await update.message.reply_photo(
                                photo=InputFile(banner),
                                caption=prompt,
                                reply_markup=kb,
                                parse_mode="HTML"
                            )
                        else:
                            await update.message.reply_photo(
                                photo=banner,
                                caption=prompt,
                                reply_markup=kb,
                                parse_mode="HTML"
                            )
                    except Exception as banner_err:
                        logger.warning(f"Could not send banner, sending text instead: {banner_err}")
                        await update.message.reply_text(
                            prompt,
                            reply_markup=kb,
                            parse_mode="HTML"
                        )
                else:
                    await update.message.reply_text(
                        prompt,
                        reply_markup=kb,
                        parse_mode="HTML"
                    )
            elif update.callback_query:
                if banner:
                    try:
                        await update.callback_query.message.edit_caption(
                            caption=prompt,
                            reply_markup=kb,
                            parse_mode="HTML"
                        )
                    except Exception:
                        await update.callback_query.message.edit_text(
                            prompt,
                            reply_markup=kb,
                            parse_mode="HTML"
                        )
                else:
                    await update.callback_query.message.edit_text(
                        prompt,
                        reply_markup=kb,
                        parse_mode="HTML"
                    )
            logger.info(f"🔒 Force-sub prompt shown to user {user_id} with banner")
        except Exception as e:
            logger.error(f"Failed to show prompt: {e}")
            return True

        return False

    except Exception as e:
        logger.error(f"Force-Sub Error: {e}", exc_info=True)
        return True
