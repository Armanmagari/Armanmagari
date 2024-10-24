from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Define a command handler function for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! I am your bot. Type /welcome for a special greeting.')

# Define the main function to run the bot
async def main() -> None:
    # Create the application and specify your bot token
    application = Application.builder().token("7764138812:AAHwS5_4HwY1yfu1BBKFP7rj1sRyx-uepz4").build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Start polling for updates
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
