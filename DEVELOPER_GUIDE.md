# Module Structure Guide for Developers

## Quick Overview

The bot is now organized into 5 focused modules:

```
bot.py                  Main application setup
├── admin_commands.py   Admin-only features
├── user_commands.py    User commands
├── handlers.py         Message & callback handlers
├── helpers.py          Shared utilities
└── database.py         Database operations (existing)
```

## How to Add Features

### Adding a New User Command

1. **Create function in `user_commands.py`:**
```python
async def mycommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """My new command description"""
    if not await check_force_sub(update, context):
        return
    
    await update.message.reply_text("✅ Command executed!")
    log_msg = format_log_message(
        update.effective_user.id,
        update.effective_user.username,
        "Used mycommand",
        "success"
    )
    await send_log(context, log_msg)
```

2. **Register in `bot.py` main() function:**
```python
app.add_handler(CommandHandler("mycommand", mycommand))
```

3. **Import at the top of `bot.py`:**
```python
from user_commands import mycommand
```

### Adding a New Admin Command

1. **Create function in `admin_commands.py`:**
```python
async def myadmincommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only command"""
    if not await check_admin(update):
        return
    
    # Your admin logic here
    pass
```

2. **Register in `bot.py`:**
```python
from admin_commands import myadmincommand
app.add_handler(CommandHandler("myadmincommand", myadmincommand))
```

### Adding a New Button Callback

1. **Add button in the relevant handler:**
```python
# In user_commands.py or handlers.py
button = InlineKeyboardButton("🆕 New Feature", callback_data="new_feature")
```

2. **Handle callback in `handlers.py`:**
```python
elif data == "new_feature":
    await query.edit_message_text("Feature activated!")
    # Your logic here
```

### Adding a Helper Function

1. **Add to `helpers.py`:**
```python
async def my_helper_function(param1: str) -> str:
    """Helper function description"""
    return f"Processed: {param1}"
```

2. **Import in needed modules:**
```python
from helpers import my_helper_function
```

---

## Module Import Guidelines

### What Each Module Should Import

**bot.py:**
- All command functions
- All handler functions
- Configuration from config.py
- logging, asyncio, telegram modules

**admin_commands.py:**
- database functions
- helpers functions
- telegram modules
- logging

**user_commands.py:**
- database functions
- helpers functions
- telegram modules
- logging

**handlers.py:**
- database functions
- helpers functions (but not OWNER_ID, FORCE_SUB_CHANNEL_ID)
- telegram modules
- logging

**helpers.py:**
- telegram modules
- database functions (minimal)
- logging
- asyncio (for sleep in retry loops)

### Circular Import Prevention

- ✅ `bot.py` imports from other modules
- ✅ `admin_commands.py` imports from helpers and database
- ✅ `user_commands.py` imports from helpers and database
- ✅ `handlers.py` imports from helpers and database
- ❌ Don't import `bot.py` from other modules (only `verified_users` when needed)

**Special case:** `handlers.py` imports `verified_users` from `bot.py` in the callback:
```python
from bot import verified_users  # Only done inside functions, not at module level
```

---

## Module-Level Variables Setup

All modules receive configuration variables from `bot.py.main()`:

### helpers.py needs:
```python
helpers.OWNER_ID = OWNER_ID
helpers.FORCE_SUB_CHANNEL_ID = FORCE_SUB_CHANNEL_ID
helpers.FORCE_SUB_BANNER_URL = FORCE_SUB_BANNER_URL
helpers.LOG_CHANNEL_ID = LOG_CHANNEL_ID
```

### admin_commands.py needs:
```python
admin_commands.OWNER_ID = OWNER_ID
admin_commands.HOME_MENU_BANNER_URL = HOME_MENU_BANNER_URL
admin_commands.LOG_CHANNEL_ID = LOG_CHANNEL_ID
```

### user_commands.py needs:
```python
user_commands.OWNER_ID = OWNER_ID
user_commands.FORCE_SUB_CHANNEL_ID = FORCE_SUB_CHANNEL_ID
user_commands.HOME_MENU_BANNER_URL = HOME_MENU_BANNER_URL
user_commands.LOG_CHANNEL_ID = LOG_CHANNEL_ID
```

### handlers.py needs:
```python
handlers.OWNER_ID = OWNER_ID
handlers.FORCE_SUB_CHANNEL_ID = FORCE_SUB_CHANNEL_ID
handlers.FORCE_SUB_BANNER_URL = FORCE_SUB_BANNER_URL
```

---

## Common Patterns

### Pattern 1: User Command with Force-Sub Check
```python
async def mycommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command that requires force-subscribe verification"""
    # Check force subscribe
    if not await check_force_sub(update, context):
        return
    
    user_id = update.effective_user.id
    
    # Your logic here
    
    # Log the action
    log_msg = format_log_message(
        user_id,
        update.effective_user.username,
        "Did something",
        "success"
    )
    await send_log(context, log_msg)
```

### Pattern 2: Admin Command
```python
async def myadmincommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only command"""
    # Check admin
    if not await check_admin(update):
        return
    
    # Your logic here
    
    # Log the action
    log_msg = f"✅ <b>Action</b>\nUser {update.effective_user.id} did something"
    await send_log(context, log_msg)
```

### Pattern 3: Callback Handler
```python
elif data == "mybutton":
    # Check if admin only
    if is_admin(user_id):
        # Admin logic
        pass
    else:
        # User logic
        pass
    
    await query.edit_message_text("Updated message")
    await query.answer("Tooltip message", show_alert=False)
```

### Pattern 4: Photo/Video Handler
```python
async def myhandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo or video"""
    # Check force subscribe
    if not await check_force_sub(update, context):
        return
    
    user_id = update.effective_user.id
    
    # Check if user is in waiting state
    if not context.user_data.get('waiting_for_file', False):
        await update.message.reply_text("Send a file")
        return
    
    context.user_data['waiting_for_file'] = False
    
    # Get the file
    file_obj = await update.message.photo[-1].get_file()  # or .video
    
    # Process file
    # ...
    
    # Send result
    await update.message.reply_text("Done!")
    
    # Log
    log_msg = format_log_message(user_id, update.effective_user.username, "Processed file", "success")
    await send_log(context, log_msg)
```

---

## Debugging Tips

### Check Module Variables
If you get "NoneType" errors, the module variables weren't set properly:
```python
# In your function
print(f"DEBUG: OWNER_ID = {OWNER_ID}")
print(f"DEBUG: FORCE_SUB_CHANNEL_ID = {FORCE_SUB_CHANNEL_ID}")
```

### Check Imports
If a function is not found:
```python
# Make sure it's imported at the top of bot.py
from admin_commands import admin_menu
from helpers import check_force_sub

# Make sure it's exported from the module it's in
# (Python exports all functions by default)
```

### Check Handler Registration
If a command doesn't work:
1. Verify the function exists and is imported
2. Check it's registered in `app.add_handler()`
3. Check the command name matches (case-sensitive)

### Check Circular Imports
If you get import errors:
1. Check you're not importing `bot.py` from other modules
2. Only import `verified_users` inside functions if needed
3. Use `from module import function` not `import module.function`

---

## Performance Considerations

### Module Loading
- All modules are loaded when the bot starts
- No lazy loading (can be added if needed)
- Estimated load time: < 1 second

### Memory Usage
- Each handler function creates a coroutine when called
- No memory overhead from modularization
- Same memory footprint as monolithic approach

### Execution Speed
- No performance penalty for module organization
- Function calls have same overhead (none)
- Async/await behaves identically

---

## Testing Individual Modules

### Test a Single Module
```bash
# Check syntax
python -m py_compile module_name.py

# Run with Python
python -c "import module_name"
```

### Test Imports
```bash
python -c "from user_commands import start; print('✅ Import successful')"
```

### Manual Testing
1. Start the bot: `python bot.py`
2. Test each command individually
3. Check logs in LOG_CHANNEL_ID
4. Verify admin commands require admin status

---

## Adding Documentation

### Function Documentation
```python
async def mycommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Brief description of what this command does.
    
    Args:
        update: The Telegram update object
        context: The Telegram context object
    
    Returns:
        None (sends messages directly to user)
    
    Raises:
        Exception: Description of what exceptions might be raised
    
    Example:
        User types /mycommand and receives a response
    """
    pass
```

### Module Documentation
Add this at the top of each module:
```python
"""
Module Name
Short description of what this module contains.

Functions:
    - function_name: What it does
    - another_function: What it does

Dependencies:
    - database: For user data
    - helpers: For utility functions
"""
```

---

## Version Control

### File Changes
- `bot.py` - Refactored (main entry point)
- `admin_commands.py` - New file
- `user_commands.py` - New file
- `handlers.py` - New file
- `helpers.py` - New file
- `bot_old.py` - Backup of original bot.py

### Git History
```bash
git add admin_commands.py user_commands.py handlers.py helpers.py bot.py
git commit -m "Refactor: Modularize bot.py into focused modules"
```

### Rollback (if needed)
```bash
# If something goes wrong, restore the original
mv bot.py bot_new.py
mv bot_old.py bot.py
```

---

## Checklist for New Features

- [ ] Function is in the correct module
- [ ] Function is imported in bot.py
- [ ] Command/callback is registered in main()
- [ ] Force-sub check is done (if needed)
- [ ] Admin check is done (if needed)
- [ ] Logging is implemented
- [ ] Error handling is in place
- [ ] Function has docstring
- [ ] Related tests pass
- [ ] Code follows project style

---

## Support

If you have questions about the module structure:

1. Check the **REFACTORING_SUMMARY.md** for detailed module information
2. Look for similar functions in the same module
3. Check `bot_old.py` for the original implementation
4. Review the function docstrings and comments

---

*This guide is for developers working on the bot codebase.*
