import os
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from filelock import AsyncFileLock
from load_env import load_env

class PositionsBot:
    def __init__(self):
        load_env()
        self.bot_token = os.getenv("positions_token")

        self.app = Application.builder().token(self.bot_token).build()

        # Add command handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("positions", self.positions))

        # File path for storing positions
        self.positions_path = "./fetcher_positions.csv"
        self.lock = AsyncFileLock("./fetcher_positions.lock")

    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Hello! I am your trading bot. Type /help to see what I can do.")

    async def help(self, update: Update, context: CallbackContext):
        await update.message.reply_text("The timestamps are in UTC. Type /positions for a list of long positions.")

    async def positions(self, update: Update, context: CallbackContext):
        async with self.lock:
            try:
                if not os.path.exists(self.positions_path):
                    await update.message.reply_text("No positions found. The file doesn't exist.")
                    return
                
                data = pd.read_csv(self.positions_path)

                # No active positions response
                if data.empty:
                    await update.message.reply_text("No active positions at the moment.")
                    return

                # Format positions for response
                positions_text = data.to_string(index=False)
                await update.message.reply_text(f"Current Positions:\n{positions_text}")

            except Exception as e:
                await update.message.reply_text(f"Error reading positions: {str(e)}")

    def run(self):
        self.app.run_polling()

# Run the bot
if __name__ == "__main__":
    bot = PositionsBot()
    bot.run()
