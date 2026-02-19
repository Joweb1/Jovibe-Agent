import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.error import NetworkError, TelegramError, TimedOut, RetryAfter
from src.adapters.base import BaseAdapter
from src.config.settings import TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramAdapter(BaseAdapter):
    async def run(self):
        if not TELEGRAM_TOKEN:
            print("Telegram token not set. Skipping Telegram adapter.")
            return

        application = (
            ApplicationBuilder()
            .token(TELEGRAM_TOKEN)
            .connect_timeout(30)
            .read_timeout(30)
            .write_timeout(30)
            .build()
        )
        
        # Add handlers
        msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self._on_message)
        application.add_handler(msg_handler)
        
        # Add global error handler
        application.add_error_handler(self._on_error)
        
        print("Telegram adapter starting...")
        async with application:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            while True:
                await asyncio.sleep(1)

    async def _on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        text = update.message.text
        self._current_update = update # Keep for context
        await self.handle_message("telegram", user_id, text)

    async def _on_error(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler for the telegram application."""
        logger.error(f"Exception while handling an update: {context.error}")
        if isinstance(context.error, NetworkError):
            print(f"Network error in Telegram update: {context.error}. Waiting for reconnection...")

    async def send_message(self, user_id, text, retries=3):
        """Send a message with retry logic and error handling."""
        if not (hasattr(self, "_current_update") and str(self._current_update.effective_user.id) == user_id):
            print(f"No active session for user {user_id}. Cannot send: {text}")
            return

        for attempt in range(retries):
            try:
                await self._current_update.message.reply_text(text)
                return # Success
            except RetryAfter as e:
                print(f"Rate limited by Telegram. Waiting {e.retry_after}s...")
                await asyncio.sleep(e.retry_after)
            except (TimedOut, NetworkError) as e:
                wait_time = (attempt + 1) * 5
                if attempt < retries - 1:
                    print(f"Telegram network error ({e}). Retrying in {wait_time}s... (Attempt {attempt+1}/{retries})")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"Failed to send message to {user_id} after {retries} attempts.")
            except TelegramError as e:
                print(f"Critical Telegram error: {e}")
                break # Non-recoverable or API issue
            except Exception as e:
                print(f"Unexpected error in send_message: {e}")
                break
