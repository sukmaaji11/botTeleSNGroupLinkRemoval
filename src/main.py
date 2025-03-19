import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .handlers import start, handle_links
from .utils import error_handler

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def main():
    # Create Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, handle_links))
    
    # Error handler
    application.add_error_handler(error_handler)

    # Start bot
    logging.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()