import requests
import yfinance as yf
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, ChatMemberHandler, filters

# Replace with your actual API keys
TOKEN = "8082794130:AAH9_ZY1VU4kRy8nBzInpuabJ-o9d8ni2FU"
NEWS_API_KEY = "10FU5CHVTK1LXM5E"
STOCK_API_KEY = "1LIN238V5F4PCM9R"

GROUP_DESCRIPTION = """
WELCOME TO ARMAN EXCHANGE!
I'm glad you're here. I would like to update you with the latest stock news.
What can I help you with today?
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a greeting message on /start command."""
    await update.message.reply_text(
        f"Hello, {update.effective_user.first_name}! Welcome to the bot. Type /help for available commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provide help information on /help command."""
    await update.message.reply_text(
        "/start - Start the bot\n"
        "/help - Display help message\n"
        "/news - Get the latest news headlines\n"
        "/stock <symbol> - Get real-time stock price\n"
        "/insider <symbol> - Get insider transactions for a stock symbol\n"
    )

async def fetch_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and send latest news headlines using NewsAPI."""
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json().get("articles", [])[:5]  # Fetch top 5 articles
        news_message = "📰 *Latest News Headlines:*\n\n"
        for article in news_data:
            news_message += f"🔹 *{article['title']}*\n"
            news_message += f"_{article['description']}_\n"
            news_message += f"[Read more]({article['url']})\n\n"
        await update.message.reply_text(news_message, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await update.message.reply_text("Failed to fetch news. Please try again later.")

async def fetch_stock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and send real-time stock data for a given symbol using Yahoo Finance."""
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a stock symbol, e.g., /stock AAPL")
        return

    symbol = context.args[0].upper()
    try:
        stock = yf.Ticker(symbol)
        stock_info = stock.history(period="1d")
        if not stock_info.empty:
            price = stock_info['Close'][0]
            stock_message = f"💹 *{symbol} Stock Price:*\n\n"
            stock_message += f"Current Price: ${price:.2f}\n"
            await update.message.reply_text(stock_message, parse_mode="Markdown")
        else:
            await update.message.reply_text("Could not retrieve stock data. Please check the symbol and try again.")
    except Exception as e:
        await update.message.reply_text(f"Error fetching stock data: {e}")

async def fetch_insider_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch insider transactions for a stock symbol using Alpha Vantage API."""
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a stock symbol, e.g., /insider IBM")
        return

    symbol = context.args[0].upper()
    url = f'https://www.alphavantage.co/query?function=INSIDER_TRANSACTIONS&symbol={symbol}&apikey={STOCK_API_KEY}'
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        transactions = data.get('transactions', [])
        
        if not transactions:
            await update.message.reply_text("No insider transactions found.")
            return
        
        message = f"📈 *{symbol} Insider Transactions:*\n\n"
        for transaction in transactions[:5]:  # Show top 5 transactions
            message += f"Date: {transaction['transactionDate']}\n"
            message += f"Type: {transaction['transactionType']}\n"
            message += f"Shares: {transaction['shares']}\n"
            message += f"Price: {transaction['transactionPrice']}\n\n"
        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text("Failed to fetch insider transactions.")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome new members to the group."""
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"Welcome to Arman Exchange, {member.full_name}! \n{GROUP_DESCRIPTION}"
        )

async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Say goodbye when a member leaves the group."""
    if update.message.left_chat_member:
        await update.message.reply_text(f"Goodbye, {update.message.left_chat_member.full_name}! We'll miss you.")

def main():
    application = ApplicationBuilder().token("8082794130:AAH9_ZY1VU4kRy8nBzInpuabJ-o9d8ni2FU").build()

    # Register handlers for each command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", fetch_news))
    application.add_handler(CommandHandler("stock", fetch_stock))
    application.add_handler(CommandHandler("insider", fetch_insider_transactions))

    # Handlers for welcome and goodbye messages in groups
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye))

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
