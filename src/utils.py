import time
import logging
from typing import Dict, List, Optional
from telegram.ext import ContextTypes  # <-- Add this line


class AdminCache:
    def __init__(self, refresh_interval: int = 300):
        self.cache: Dict[int, dict] = {}
        self.refresh_interval = refresh_interval  # 5 minutes

    async def get_admins(self, bot, chat_id: int) -> Optional[List[int]]:
        """Get cached admins or fetch fresh list asynchronously"""
        cached = self.cache.get(chat_id)
        
        if cached and (time.time() - cached["timestamp"] < self.refresh_interval):
            return cached["admins"]
        
        try:
            admins = await bot.get_chat_administrators(chat_id)
            admin_ids = [admin.user.id for admin in admins]
            self.cache[chat_id] = {
                "admins": admin_ids,
                "timestamp": time.time()
            }
            return admin_ids
        except Exception as e:
            logging.error(f"Error fetching admins: {e}")
            return None

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors with async support"""
    logging.error("Exception while handling update:", exc_info=context.error)