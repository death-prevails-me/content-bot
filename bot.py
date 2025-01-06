from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Flask app setup
app = Flask(__name__)

# Load bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it as an environment variable in Vercel.")

# Telegram Application setup
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# List of authorized users
AUTHORIZED_USERS = [1139405017]

# Available chats for posting
available_chats = {}

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        await update.message.reply_text("Welcome! You are authorized to use this bot.")
    else:
        await update.message.reply_text("You are not authorized to use this bot.")

async def list_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    if not available_chats:
        await update.message.reply_text("No available groups or channels found.")
        return

    chat_list = "\n".join([f"{name} (ID: {chat_id})" for name, chat_id in available_chats.items()])
    await update.message.reply_text(f"Available chats:\n{chat_list}")

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a message with /post <chat_title> to post it.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /post <chat_title>")
        return

    chat_title = context.args[0]
    if chat_title not in available_chats:
        await update.message.reply_text(f"Chat '{chat_title}' not found. Use /list_chats to see available options.")
        return

    original_message = update.message.reply_to_message.text
    chat_id = available_chats[chat_title]

    try:
        await bot.send_message(chat_id=chat_id, text=original_message)
        await update.message.reply_text(f"Content posted to '{chat_title}' successfully.")
    except Exception as e:
        await update.message.reply_text(f"Failed to post content: {e}")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("list_chats", list_chats))
application.add_handler(CommandHandler("post", post))

@app.route("/", methods=["POST"])
def webhook():
    """Process Telegram updates."""
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return "OK"

@app.route("/", methods=["GET"])
def health_check():
    """Handle health check or browser visit."""
    return "Bot is running!"

if __name__ == "__main__":
    app.run(port=8000)
