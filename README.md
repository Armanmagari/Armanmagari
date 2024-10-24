from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Define a command handler function for /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your bot. Type /welcome for a special greeting.')

# Define a command handler function for /welcome
def welcome(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to Arman Magari world! Enjoy your stay!')

# Define a command handler function for /ask
def ask(update: Update, context: CallbackContext) -> None:
    if context.args:
        question = ' '.join(context.args)
        answer = get_answer(question)
        update.message.reply_text(answer)
    else:
        update.message.reply_text('Please ask a question after the command. For example: /ask What is your name?')

# Function to provide answers based on questions
def get_answer(question: str) -> str:
    q_and_a = {
        "What is your name?": "I am a Telegram bot created by Arman Magari.",
        "How are you?": "I'm just a bot, but I'm here to help you!",
        "What can you do?": "I can answer your questions and greet you!",
    }
    return q_and_a.get(question, "I'm sorry, I don't have an answer for that question.")

# Main function to run the bot
def main() -> None:
    # Replace '7764138812:AAHwS5_4HwY1yfu1BBKFP7rj1sRyx-uepz4' with your actual bot token
    updater = Updater("7764138812:AAHwS5_4HwY1yfu1BBKFP7rj1sRyx-uepz4", use_context=True)

    dispatcher = updater.dispatcher

    # Register the command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("welcome", welcome))
    dispatcher.add_handler(CommandHandler("ask", ask))

    # Start the Bot
    updater.start_polling()
    print("Bot has started.")
    
    # Run the bot until you press Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
