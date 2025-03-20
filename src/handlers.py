import re
import logging
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from .utils import AdminCache

admin_cache = AdminCache()

# Regex to detect URLs (including non-http prefixes like www. or example.com)
LINK_REGEX = re.compile(
    r'(?:https?://)?'  # Optional http/https
    r'(?:www\.)?'      # Optional www.
    r'\w+\.\w+'        # Domain + TLD (e.g., example.com)
    r'(?:/\S*)?'       # Optional path (e.g., /page?id=1)
    r'(?=\s|$)'        # Ensure URL ends at whitespace or end of string
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message handler"""
    await update.message.reply_text("Hai!. Saya adalah bot untuk melakukan filter pesan chat dari member group diskusi Sasana Ngapak Purwokerto. Hal ini bertujuan untuk menjaga keamanan dan kenyamanan member group serta menghindari hal hal yang tidak diinginkan")

async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete non-admin links and notify users"""
    message = update.message
    if not message or message.chat.type not in ['group', 'supergroup']:
        return

    # Skip if sender is anonymous (e.g., channel posts)
    if not message.from_user:
        return

    text = message.text or message.caption
    if not text or not LINK_REGEX.search(text):
        return  # No link detected

    try:
        chat_id = message.chat_id
        user = message.from_user

        # Fetch admins (cached for 5 minutes)
        admin_ids = await admin_cache.get_admins(context.bot, chat_id)
        if not admin_ids:
            logging.warning(f"Failed to fetch admins for chat {chat_id}")
            return

        # Allow admins to post links
        if user.id in admin_ids:
            logging.info(f"Allowed link from admin {user.id} in chat {chat_id}")
            return
 
        # Send warning FIRST to avoid reply errors
        warning = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ {user.first_name}! demi keamanan dan kenyamanan, anda tidak diizinkan untuk mengirimkan link di dalam group diskusi ini. Terimakasih.",
        );

        # Delete the original message
        await message.delete()
        logging.info(f"Deleted link from user {user.id} in chat {chat_id}")

    except Exception as e:
        logging.error(f"Error handling message: {e}", exc_info=True)

        # Fallback error message
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ I need admin privileges to delete messages!"
        );