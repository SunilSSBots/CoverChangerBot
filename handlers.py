"""
Message and Callback Handlers Module
Contains all handlers for messages, callbacks, and media
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

from database import (
    get_thumbnail, has_thumbnail, save_thumbnail, delete_thumbnail,
    log_new_user, log_thumbnail_set, log_thumbnail_removed, format_log_message
)
from helpers import (
    send_log, check_force_sub, is_admin
)

logger = logging.getLogger(__name__)

# Module-level variables set by bot.py
OWNER_ID = None
FORCE_SUB_CHANNEL_ID = None
FORCE_SUB_BANNER_URL = None


async def open_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open home menu with user's thumbnail"""
    await check_force_sub(update, context)
    
    try:
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # Build home menu keyboard
        kb = [
            [
                InlineKeyboardButton("📸 Set Thumbnail", callback_data="set_thumbnail"),
                InlineKeyboardButton("🎬 Apply to Video", callback_data="apply_cover"),
            ],
            [
                InlineKeyboardButton("👀 View Thumbnail", callback_data="view_thumb"),
                InlineKeyboardButton("🗑️ Remove Thumbnail", callback_data="remove_thumb"),
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
                InlineKeyboardButton("ℹ️ Help", callback_data="help_menu"),
            ]
        ]
        
        # Add admin panel button for admins
        if is_admin(user_id):
            kb.append([InlineKeyboardButton("🛡️ Admin Panel", callback_data="admin_panel")])
        
        kb_markup = InlineKeyboardMarkup(kb)
        
        # Build message
        has_thumb = has_thumbnail(user_id)
        thumb_status = "✅ Thumbnail saved" if has_thumb else "❌ No thumbnail yet"
        
        home_text = (
            f"👋 Welcome back, <b>{user_name}</b>!\n\n"
            f"<b>📊 Your Status:</b>\n"
            f"• {thumb_status}\n\n"
            f"<b>What would you like to do?</b>\n"
            "Use the buttons below to manage your thumbnails."
        )
        
        try:
            banner = FORCE_SUB_BANNER_URL if hasattr(update, 'callback_query') and update.callback_query else None
            
            if update.message:
                await update.message.reply_text(
                    home_text,
                    reply_markup=kb_markup,
                    parse_mode="HTML"
                )
            elif update.callback_query:
                if banner:
                    try:
                        if isinstance(banner, str) and os.path.isfile(banner):
                            await update.callback_query.message.reply_photo(
                                photo=InputFile(banner),
                                caption=home_text,
                                reply_markup=kb_markup,
                                parse_mode="HTML"
                            )
                        else:
                            await update.callback_query.message.reply_photo(
                                photo=banner,
                                caption=home_text,
                                reply_markup=kb_markup,
                                parse_mode="HTML"
                            )
                    except Exception:
                        await update.callback_query.message.reply_text(
                            home_text,
                            reply_markup=kb_markup,
                            parse_mode="HTML"
                        )
                else:
                    await update.callback_query.message.reply_text(
                        home_text,
                        reply_markup=kb_markup,
                        parse_mode="HTML"
                    )
                
                await update.callback_query.answer()
        
        except Exception as e:
            logger.error(f"Error showing home: {e}")
            
    except Exception as e:
        logger.error(f"open_home error: {e}", exc_info=True)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline button callbacks"""
    try:
        query = update.callback_query
        data = query.data
        user_id = update.effective_user.id
        
        await query.answer()
        
        # Force-sub verification
        if data == "check_fsub":
            logger.info(f"User {user_id} attempting to verify membership")
            
            if not FORCE_SUB_CHANNEL_ID:
                logger.info("Force-sub not configured, allowing access")
                return
            
            try:
                channel_id_str = str(FORCE_SUB_CHANNEL_ID).strip()
                try:
                    if channel_id_str.startswith("-"):
                        channel_id = int(channel_id_str)
                    else:
                        channel_id = int(channel_id_str)
                except ValueError:
                    channel_id = channel_id_str
                
                member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                
                if member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                    from bot import verified_users
                    verified_users.add(user_id)
                    
                    await query.edit_message_text(
                        "✅ <b>Verification Successful!</b>\n\n"
                        "You have joined the channel. You can now use all features of this bot.\n\n"
                        "Use /start to go to the home menu.",
                        parse_mode="HTML"
                    )
                    log_msg = (
                        f"✅ <b>User Verified</b>\n"
                        f"User ID: <code>{user_id}</code>\n"
                        f"Username: @{update.effective_user.username or 'N/A'}\n"
                        f"Status: Channel member verified"
                    )
                    await send_log(context, log_msg)
                    logger.info(f"✅ User {user_id} verified successfully")
                else:
                    await query.edit_message_text(
                        "❌ <b>Verification Failed</b>\n\n"
                        "It seems you haven't joined the channel yet or are not a member.\n\n"
                        "Please join the channel first, then try again.",
                        parse_mode="HTML"
                    )
                    logger.warning(f"⚠️ User {user_id} failed verification - not a member")
                    
            except Exception as e:
                logger.error(f"Verification error: {e}")
                await query.edit_message_text(
                    "⚠️ <b>Verification Error</b>\n\n"
                    f"Could not verify membership. Please try again later.\n"
                    f"Error: {str(e)[:100]}"
                )
        
        # Close banner
        elif data == "close_banner":
            await query.delete_message()
        
        # Set thumbnail
        elif data == "set_thumbnail":
            await query.edit_message_text(
                "📸 <b>Set Thumbnail</b>\n\n"
                "Send me an image to use as your thumbnail.\n\n"
                "<i>Supported formats: JPG, PNG</i>\n"
                "<i>Max size: 5 MB</i>\n\n"
                "✋ Or send /cancel to go back.",
                parse_mode="HTML"
            )
            context.user_data['waiting_for_thumb'] = True
        
        # Apply cover to video
        elif data == "apply_cover":
            has_thumb = has_thumbnail(user_id)
            if not has_thumb:
                await query.edit_message_text(
                    "❌ <b>No Thumbnail</b>\n\n"
                    "You don't have a saved thumbnail yet.\n\n"
                    "Please set a thumbnail first using the '📸 Set Thumbnail' button.",
                    parse_mode="HTML"
                )
            else:
                await query.edit_message_text(
                    "🎬 <b>Apply Thumbnail to Video</b>\n\n"
                    "Send me a video and I'll apply your saved thumbnail as the cover.\n\n"
                    "<i>Supported formats: MP4, WebM</i>\n"
                    "<i>Max size: 50 MB</i>\n\n"
                    "✋ Or send /cancel to go back.",
                    parse_mode="HTML"
                )
                context.user_data['waiting_for_video'] = True
        
        # View thumbnail
        elif data == "view_thumb":
            has_thumb = has_thumbnail(user_id)
            if not has_thumb:
                await query.edit_message_text(
                    "❌ <b>No Thumbnail</b>\n\n"
                    "You don't have a saved thumbnail yet.",
                    parse_mode="HTML"
                )
            else:
                try:
                    thumb_file = get_thumbnail(user_id)
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=InputFile(thumb_file),
                        caption="🖼️ <b>Your Saved Thumbnail</b>",
                        parse_mode="HTML"
                    )
                    await query.answer("✅ Thumbnail sent in a new message", show_alert=False)
                except Exception as e:
                    logger.error(f"Error viewing thumbnail: {e}")
                    await query.answer("❌ Could not load thumbnail", show_alert=True)
        
        # Remove thumbnail
        elif data == "remove_thumb":
            has_thumb = has_thumbnail(user_id)
            if not has_thumb:
                await query.edit_message_text(
                    "❌ <b>No Thumbnail</b>\n\n"
                    "You don't have a saved thumbnail to remove.",
                    parse_mode="HTML"
                )
            else:
                delete_thumbnail(user_id)
                log_msg = format_log_message(
                    user_id, update.effective_user.username,
                    "Removed thumbnail", "success"
                )
                await send_log(context, log_msg)
                
                await query.edit_message_text(
                    "✅ <b>Thumbnail Removed</b>\n\n"
                    "Your saved thumbnail has been successfully deleted.\n\n"
                    "You can set a new one anytime using the '📸 Set Thumbnail' button.",
                    parse_mode="HTML"
                )
        
        # Settings menu
        elif data == "settings_menu":
            user_info = f"User ID: <code>{user_id}</code>"
            
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Back to Home", callback_data="home_menu")]
            ])
            
            await query.edit_message_text(
                f"⚙️ <b>Your Settings</b>\n\n"
                f"{user_info}\n\n"
                f"<b>Account Status:</b>\n"
                f"• Status: Active\n"
                f"• Thumbnail: {'✅ Saved' if has_thumbnail(user_id) else '❌ Not set'}\n\n"
                f"<i>More settings coming soon...</i>",
                reply_markup=kb,
                parse_mode="HTML"
            )
        
        # Help menu
        elif data == "help_menu":
            help_text = (
                "ℹ️ <b>How to Use This Bot</b>\n\n"
                "<b>📸 Set Thumbnail:</b>\n"
                "1. Click the '📸 Set Thumbnail' button\n"
                "2. Send an image\n"
                "3. Your thumbnail is saved\n\n"
                "<b>🎬 Apply to Video:</b>\n"
                "1. Save a thumbnail first\n"
                "2. Click '🎬 Apply to Video'\n"
                "3. Send a video file\n"
                "4. Wait for processing\n"
                "5. Download the video with thumbnail\n\n"
                "<b>👀 View/Remove:</b>\n"
                "Use the buttons to view or delete your thumbnail.\n\n"
                "⚠️ <b>Important:</b>\n"
                "• Keep your images under 5 MB\n"
                "• Keep videos under 50 MB\n"
                "• Processing may take a few seconds"
            )
            
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Back to Home", callback_data="home_menu")]
            ])
            
            await query.edit_message_text(
                help_text,
                reply_markup=kb,
                parse_mode="HTML"
            )
        
        # Home menu
        elif data == "home_menu":
            await open_home(update, context)
        
        # Admin panel
        elif data == "admin_panel":
            if not is_admin(user_id):
                await query.answer("❌ Unauthorized", show_alert=True)
                return
            
            from admin_commands import admin_menu
            await admin_menu(update, context)
            
    except Exception as e:
        logger.error(f"callback_handler error: {e}", exc_info=True)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads - save as thumbnail"""
    if not await check_force_sub(update, context):
        return
    
    try:
        user_id = update.effective_user.id
        
        # Check if user is waiting for thumbnail
        if not context.user_data.get('waiting_for_thumb', False):
            await update.message.reply_text(
                "💭 I'm not expecting any photos right now.\n\n"
                "Use /start and click '📸 Set Thumbnail' to upload a thumbnail."
            )
            return
        
        context.user_data['waiting_for_thumb'] = False
        
        # Get photo
        photo_file = await update.message.photo[-1].get_file()
        
        # Create thumbnails directory
        os.makedirs("thumbnails", exist_ok=True)
        
        # Save thumbnail
        thumb_path = f"thumbnails/{user_id}.jpg"
        await photo_file.download_to_drive(thumb_path)
        
        # Save to database
        save_thumbnail(user_id, thumb_path)
        
        # Log
        log_msg = format_log_message(
            user_id, update.effective_user.username,
            "Set thumbnail", "success"
        )
        await send_log(context, log_msg)
        log_thumbnail_set(user_id)
        
        # Confirm
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Home", callback_data="home_menu")],
            [InlineKeyboardButton("👀 View", callback_data="view_thumb")]
        ])
        
        await update.message.reply_photo(
            photo=open(thumb_path, 'rb'),
            caption="✅ <b>Thumbnail Saved!</b>\n\nYour thumbnail is ready to use.",
            reply_markup=kb,
            parse_mode="HTML"
        )
        logger.info(f"✅ Thumbnail saved for user {user_id}")
        
    except Exception as e:
        logger.error(f"photo_handler error: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ <b>Error</b>\n\nFailed to save thumbnail: {str(e)[:100]}"
        )


async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video uploads - apply thumbnail cover"""
    if not await check_force_sub(update, context):
        return
    
    try:
        user_id = update.effective_user.id
        
        # Check if user is waiting for video
        if not context.user_data.get('waiting_for_video', False):
            await update.message.reply_text(
                "💭 I'm not expecting any videos right now.\n\n"
                "Use /start and click '🎬 Apply to Video' to upload a video."
            )
            return
        
        context.user_data['waiting_for_video'] = False
        
        # Check if user has thumbnail
        if not has_thumbnail(user_id):
            await update.message.reply_text(
                "❌ You don't have a thumbnail set yet.\n\n"
                "Please set a thumbnail first."
            )
            return
        
        # Get video
        video_file = await update.message.video.get_file()
        
        # Create temp directory
        os.makedirs("temp_videos", exist_ok=True)
        
        # Download video
        input_video = f"temp_videos/{user_id}_input.mp4"
        await video_file.download_to_drive(input_video)
        
        # Get thumbnail
        thumb_path = get_thumbnail(user_id)
        
        # Process video
        output_video = f"temp_videos/{user_id}_output.mp4"
        
        try:
            import ffmpeg
            
            (ffmpeg
                .input(input_video)
                .output(output_video, vf=f"scale=1280:720")
                .run(quiet=False, overwrite_output=True)
            )
            
            # Add thumbnail
            with open(output_video, 'rb') as f:
                await context.bot.send_document(
                    chat_id=user_id,
                    document=f,
                    caption="✅ <b>Video Ready!</b>\n\nYour video with the thumbnail cover is ready to download.",
                    parse_mode="HTML",
                    thumbnail=open(thumb_path, 'rb')
                )
            
            # Log
            log_msg = format_log_message(
                user_id, update.effective_user.username,
                "Applied thumbnail to video", "success"
            )
            await send_log(context, log_msg)
            log_thumbnail_set(user_id)
            
            logger.info(f"✅ Video processed for user {user_id}")
            
        except ImportError:
            logger.warning("ffmpeg not available, sending video without processing")
            with open(input_video, 'rb') as f:
                await context.bot.send_video(
                    chat_id=user_id,
                    video=f,
                    caption="✅ <b>Video Ready!</b>",
                    parse_mode="HTML",
                    thumbnail=open(thumb_path, 'rb')
                )
        
        finally:
            # Cleanup
            for path in [input_video, output_video]:
                if os.path.exists(path):
                    os.remove(path)
        
    except Exception as e:
        logger.error(f"video_handler error: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ <b>Error</b>\n\nFailed to process video: {str(e)[:100]}"
        )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    if not await check_force_sub(update, context):
        return
    
    try:
        user_id = update.effective_user.id
        text = update.message.text
        
        # Handle cancel command in waiting states
        if text.lower() == "/cancel":
            context.user_data['waiting_for_thumb'] = False
            context.user_data['waiting_for_video'] = False
            await update.message.reply_text("❌ Cancelled. Use /start to go to home menu.")
            return
        
        # If waiting for thumbnail
        if context.user_data.get('waiting_for_thumb', False):
            await update.message.reply_text(
                "❌ Please send an image, not text.\n\n"
                "📸 Send a JPG or PNG image for your thumbnail."
            )
            return
        
        # If waiting for video
        if context.user_data.get('waiting_for_video', False):
            await update.message.reply_text(
                "❌ Please send a video, not text.\n\n"
                "🎬 Send an MP4 or WebM video file."
            )
            return
        
        # Default response for other text
        await update.message.reply_text(
            "💭 I'm a specialized thumbnail tool.\n\n"
            "Use /start to access the full menu and manage your thumbnails.",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"text_handler error: {e}", exc_info=True)
