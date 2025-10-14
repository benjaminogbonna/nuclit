import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
environment = os.getenv("ENVIRONMENT")
if environment == 'prod':
    BACKEND_URL = "http://localhost:8000/ask"
else:
    BACKEND_URL = "http://localhost:8000/ask"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! I’m Nuclit, your AI assistant. Ask me anything!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    await update.message.reply_text("Thinking...")

    try:
        response = requests.post(BACKEND_URL, json={"question": user_message})
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "Sorry, I couldn't find an answer.")
        else:
            answer = "Server error. Please try again."
    except Exception as e:
        answer = f"Error: {str(e)}"

    await context.bot.send_message(chat_id=chat_id, text=answer)

def bot_main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

# if __name__ == "__main__":
#     bot_main()
