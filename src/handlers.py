import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .utils import AdminCache

admin_cache = AdminCache()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔗 I'm a link-filter bot! Add me to groups as admin.")

async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.chat.type not in ['group', 'supergroup']:
        return

    message = update.message
    text = message.text or message.caption

    # Link REGEX 
    # Use this regex pattern in your code

    LINK_REGEX = re.compile(
        r'(?:https?://)?'  # Optional http/https
        r'(?:www\.)?'       # Optional www.
        r'\w+\.\w+'        # Domain and TLD (e.g., example.com)
        r'(?:/\S*)?'       # Optional path (e.g., /page?id=1)
    )

    if not text:
        return

    # Check for links using the new regex
    if LINK_REGEX.search(text):
        # Fetch admins and delete message (same as before)
        admin_ids = await admin_cache.get_admins(context.bot, message.chat_id)
        if not admin_ids:
            return

        if message.from_user.id in admin_ids:
            return

        try:
            await message.delete()
            await message.reply_text(
                f"⚠️ {message.from_user.first_name}, links are not allowed!",
                reply_to_message_id=message.message_id
            )
        except Exception as e:
            logging.error(f"Failed to delete message: {e}")
