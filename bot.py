#!/usr/bin/env python3
import logging
from html import escape
import pickledb
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOTNAME, TOKEN

# Define the help text
help_text = (
    "Welcomes everyone that enters a group chat that this bot is a "
    "part of. By default, only the person who invited the bot into "
    "the group is able to change settings.\nCommands:\n\n"
    "/welcome - Set welcome message\n"
    "/goodbye - Set goodbye message\n"
    "/disable\\_goodbye - Disable the goodbye message\n"
    "/lock - Only the person who invited the bot can change messages\n"
    "/unlock - Everyone can change messages\n"
    '/quiet - Disable "Sorry, only the person who..." '
    "& help messages\n"
    '/unquiet - Enable "Sorry, only the person who..." '
    "& help messages\n\n"
    "You can use _$username_ and _$title_ as placeholders when setting"
    " messages. [HTML formatting]"
    "(https://core.telegram.org/bots/api#formatting-options) "
    "is also supported.\n"
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the database
db = pickledb.load("bot.db", True)
if not db.get("chats"):
    db.set("chats", [])

# Async function to send messages
async def send_message(context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
    await context.bot.send_message(*args, **kwargs)

# Check admin privileges
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE, override_lock=None):
    chat_id = update.message.chat_id
    chat_str = str(chat_id)

    if chat_id > 0:
        await send_message(context, chat_id=chat_id, text="Please add me to a group first!")
        return False

    locked = override_lock if override_lock is not None else db.get(chat_str + "_lck")

    if locked and db.get(chat_str + "_adm") != update.message.from_user.id:
        if not db.get(chat_str + "_quiet"):
            await send_message(
                context,
                chat_id=chat_id,
                text="Sorry, only the person who invited me can do that.",
            )
        return False
    return True

# Command and message handlers
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        context,
        chat_id=update.message.chat_id,
        text=help_text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update, context):
        return

    chat_id = update.message.chat_id
    message = update.message.text.partition(" ")[2]

    if not message:
        await send_message(
            context,
            chat_id=chat_id,
            text="You need to send a message, too! For example:\n"
            "<code>/welcome Hello $username, welcome to "
            "$title!</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    db.set(str(chat_id), message)
    await send_message(context, chat_id=chat_id, text="Got it!")

# Goodbye message
async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    text = db.get(str(chat_id) + "_bye")

    if text is False:
        return

    if text is None:
        text = "Goodbye, $username!"

    text = text.replace("$username", update.message.left_chat_member.first_name)
    text = text.replace("$title", update.message.chat.title)
    await send_message(context, chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

# Introduce bot to chat
async def introduce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    invited = update.message.from_user.id

    db.set(str(chat_id) + "_adm", invited)
    db.set(str(chat_id) + "_lck", True)

    text = (
        f"Hello {update.message.chat.title}! "
        "I will now greet anyone who joins this chat with a nice message 😊 \n"
        "Check the /help command for more info!"
    )
    await send_message(context, chat_id=chat_id, text=text)

async def empty_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chats = db.get("chats")

    if update.message.chat.id not in chats:
        chats.append(update.message.chat.id)
        db.set("chats", chats)

    if update.message.new_chat_members:
        for new_member in update.message.new_chat_members:
            if new_member.username == BOTNAME:
                await introduce(update, context)
            else:
                await welcome(update, context, new_member)

    elif update.message.left_chat_member:
        await goodbye(update, context)

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    try:
        if isinstance(error, TelegramError):
            chats = db.get("chats")
            if update.message.chat_id in chats:
                chats.remove(update.message.chat_id)
                db.set("chats", chats)
                logger.info(f"Removed chat_id {update.message.chat_id} from chat list")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

# Main function
async def main():
    application = ApplicationBuilder().token("7764138812:AAHwS5_4HwY1yfu1BBKFP7rj1sRyx-uepz4").build()

    application.add_handler(CommandHandler("start", help))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("welcome", set_welcome))
    application.add_handler(MessageHandler(filters.StatusUpdate.ALL, empty_message))

    application.add_error_handler(error)

    await application.start()
    await application.updater.start_polling()
    await application.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
