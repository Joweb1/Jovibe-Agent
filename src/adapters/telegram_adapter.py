import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from src.adapters.base import BaseAdapter
from src.config.settings import TELEGRAM_TOKEN

class TelegramAdapter(BaseAdapter):
    async def run(self):
        if not TELEGRAM_TOKEN:
            print("Telegram token not set. Skipping Telegram adapter.")
            return

        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers
        msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self._on_message)
        application.add_handler(msg_handler)
        
        print("Telegram adapter starting...")
        async with application:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            # Keep running until cancelled
            while True:
                await asyncio.sleep(1)

    async def _on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        text = update.message.text
        self._current_update = update # Keep for context
        await self.handle_message("telegram", user_id, text)

    async def send_message(self, user_id, text):
        if hasattr(self, "_current_update") and str(self._current_update.effective_user.id) == user_id:
            await self._current_update.message.reply_text(text)
        else:
            # Fallback: would need bot instance and chat_id
            print(f"Would send Telegram to {user_id}: {text}")
