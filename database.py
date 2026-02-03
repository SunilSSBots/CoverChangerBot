"""
MongoDB Database Module for Video Cover Bot
Handles all database operations for user thumbnails
"""

import os
import logging
from datetime import datetime
from pymongo import MongoClient

# Setup logging
logger = logging.getLogger(__name__)

# MongoDB Connection Setup
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "video_cover_bot")

try:
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = mongo_client[MONGODB_DATABASE]
    users_collection = db["users"]
    # Test connection
    mongo_client.server_info()
    logger.info("✅ MongoDB connected successfully")
    DB_AVAILABLE = True
except Exception as e:
    logger.warning(f"⚠️ MongoDB not available: {e}")
    logger.warning("⚠️ Bot will work with limited functionality (thumbnails won't persist)")
    DB_AVAILABLE = False
    users_collection = None


def save_thumbnail(user_id: int, photo_id: str) -> bool:
    """Save or update user's thumbnail to MongoDB"""
    if not DB_AVAILABLE:
        logger.debug(f"Database not available, skipping thumbnail save for user {user_id}")
        return False
    
    try:
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "photo_id": photo_id,
                    "updated_at": datetime.now()
                }
            },
            upsert=True
        )
        logger.info(f"✅ Thumbnail saved for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving thumbnail: {e}")
        return False


def get_thumbnail(user_id: int) -> str | None:
    """Retrieve user's thumbnail from MongoDB"""
    if not DB_AVAILABLE:
        logger.debug(f"Database not available, cannot get thumbnail for user {user_id}")
        return None
    
    try:
        user_record = users_collection.find_one({"user_id": user_id})
        if user_record and "photo_id" in user_record:
            logger.info(f"✅ Retrieved thumbnail for user {user_id}")
            return user_record["photo_id"]
        logger.info(f"⚠️ No thumbnail found for user {user_id}")
        return None
    except Exception as e:
        logger.error(f"❌ Error retrieving thumbnail: {e}")
        return None


def delete_thumbnail(user_id: int) -> bool:
    """Delete user's thumbnail from MongoDB"""
    if not DB_AVAILABLE:
        logger.debug(f"Database not available, skipping thumbnail delete for user {user_id}")
        return False
    
    try:
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$unset": {"photo_id": ""}}
        )
        if result.modified_count > 0:
            logger.info(f"✅ Thumbnail deleted for user {user_id}")
            return True
        logger.info(f"⚠️ No thumbnail to delete for user {user_id}")
        return False
    except Exception as e:
        logger.error(f"❌ Error deleting thumbnail: {e}")
        return False


def has_thumbnail(user_id: int) -> bool:
    """Check if user has a saved thumbnail"""
    if not DB_AVAILABLE:
        return False
    
    try:
        user_record = users_collection.find_one({"user_id": user_id})
        has_thumb = user_record is not None and "photo_id" in user_record
        logger.debug(f"Thumbnail check for user {user_id}: {has_thumb}")
        return has_thumb
    except Exception as e:
        logger.error(f"❌ Error checking thumbnail: {e}")
        return False


"""═══════════════════ ADMIN FUNCTIONS ═══════════════════"""


def ban_user(user_id: int, reason: str = "No reason") -> bool:
    """Ban a user from using the bot"""
    if not DB_AVAILABLE:
        logger.debug(f"Database not available, skipping ban for user {user_id}")
        return False
    
    try:
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "is_banned": True,
                    "ban_reason": reason,
                    "banned_at": datetime.now()
                }
            },
            upsert=True
        )
        logger.info(f"🚫 User {user_id} banned. Reason: {reason}")
        return True
    except Exception as e:
        logger.error(f"❌ Error banning user {user_id}: {e}")
        return False


def unban_user(user_id: int) -> bool:
    """Unban a user"""
    if not DB_AVAILABLE:
        logger.debug(f"Database not available, skipping unban for user {user_id}")
        return False
    
    try:
        result = users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "is_banned": False,
                    "unbanned_at": datetime.now()
                }
            }
        )
        if result.modified_count > 0:
            logger.info(f"✅ User {user_id} unbanned")
            return True
        logger.info(f"⚠️ User {user_id} not found")
        return False
    except Exception as e:
        logger.error(f"❌ Error unbanning user {user_id}: {e}")
        return False


def is_user_banned(user_id: int) -> bool:
    """Check if user is banned"""
    if not DB_AVAILABLE:
        return False
    
    try:
        user_record = users_collection.find_one({"user_id": user_id})
        if user_record and user_record.get("is_banned", False):
            logger.debug(f"User {user_id} is banned")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error checking ban status: {e}")
        return False


def get_total_users() -> int:
    """Get total number of users"""
    if not DB_AVAILABLE:
        return 0
    
    try:
        count = users_collection.count_documents({})
        logger.info(f"📊 Total users: {count}")
        return count
    except Exception as e:
        logger.error(f"❌ Error counting users: {e}")
        return 0


def get_banned_users_count() -> int:
    """Get total number of banned users"""
    if not DB_AVAILABLE:
        return 0
    
    try:
        count = users_collection.count_documents({"is_banned": True})
        logger.info(f"🚫 Total banned users: {count}")
        return count
    except Exception as e:
        logger.error(f"❌ Error counting banned users: {e}")
        return 0


def get_stats() -> dict:
    """Get bot statistics"""
    if not DB_AVAILABLE:
        return {
            "total_users": 0,
            "banned_users": 0,
            "users_with_thumbnail": 0
        }
    
    try:
        total = users_collection.count_documents({})
        banned = users_collection.count_documents({"is_banned": True})
        with_thumb = users_collection.count_documents({"photo_id": {"$exists": True}})
        
        stats = {
            "total_users": total,
            "banned_users": banned,
            "users_with_thumbnail": with_thumb
        }
        logger.info(f"📊 Stats: {stats}")
        return stats
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return {
            "total_users": 0,
            "banned_users": 0,
            "users_with_thumbnail": 0
        }


"""═══════════════════ LOGGING FUNCTIONS ═══════════════════"""


def create_log_entry(user_id: int, username: str, action: str, details: str = "") -> dict:
    """Create a formatted log entry"""
    from datetime import datetime
    
    log_entry = {
        "user_id": user_id,
        "username": f"@{username}" if username else "Unknown",
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    return log_entry


def format_log_message(user_id: int, username: str, action: str, details: str = "") -> str:
    """Format log message for Telegram channel"""
    from datetime import datetime
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username_str = f"@{username}" if username else "Unknown"
    
    log_msg = (
        f"📝 <b>{action}</b>\n\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"📌 Username: {username_str}\n"
        f"⏰ Time: {now}\n"
    )
    
    if details:
        log_msg += f"📋 Details: {details}\n"
    
    return log_msg


def log_new_user(user_id: int, username: str, first_name: str) -> dict:
    """Log new user startup"""
    action = "🆕 New User Started Bot"
    details = f"Name: {first_name}"
    logger.info(f"✅ {action} - {username} ({user_id})")
    return create_log_entry(user_id, username, action, details)


def log_user_banned(user_id: int, username: str, reason: str) -> dict:
    """Log user ban"""
    action = "🚫 User Banned"
    details = f"Reason: {reason}"
    logger.info(f"✅ {action} - {username} ({user_id}): {reason}")
    return create_log_entry(user_id, username, action, details)


def log_user_unbanned(user_id: int, username: str) -> dict:
    """Log user unban"""
    action = "✅ User Unbanned"
    logger.info(f"✅ {action} - {username} ({user_id})")
    return create_log_entry(user_id, username, action)


def log_thumbnail_set(user_id: int, username: str, is_replace: bool = False) -> dict:
    """Log thumbnail set/replace"""
    action = "🖼 Thumbnail Replaced" if is_replace else "🖼 Thumbnail Set"
    logger.info(f"✅ {action} - {username} ({user_id})")
    return create_log_entry(user_id, username, action)


def log_thumbnail_removed(user_id: int, username: str) -> dict:
    """Log thumbnail removal"""
    action = "🗑️ Thumbnail Removed"
    logger.info(f"✅ {action} - {username} ({user_id})")
    return create_log_entry(user_id, username, action)

