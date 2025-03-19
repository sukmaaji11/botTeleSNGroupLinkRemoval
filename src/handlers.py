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

    # Check for links
    if not (text and re.search(r'https?://\S+', text)):
        return

    try:
        admin_ids = await admin_cache.get_admins(context.bot, message.chat_id)
        if not admin_ids:
            return

        # Allow admins
        if message.from_user.id in admin_ids:
            return

        # Delete message
        await message.delete()
        await message.reply_text(
            f"⚠️ {message.from_user.first_name}, only admins can post links!",
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        logging.error(f"Failed to handle message: {e}")
        await message.reply_text("❌ I need admin privileges to delete messages!")