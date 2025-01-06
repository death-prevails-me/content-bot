from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# Flask app setup
app = Flask(__name__)

# Bot token from environment variable (best practice for security)
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it as an environment variable in Vercel.")

bot = Bot(token=BOT_TOKEN)

# Telegram Dispatcher (manages command handlers)
dispatcher = Dispatcher(bot, None, workers=0)

# List of authorized user IDs
AUTHORIZED_USERS = [123456789, 987654321]

# Dictionary to store available chats (groups/channels where the bot is admin)
available_chats = {}

@app.route("/", methods=["GET", "POST"])
def webhook():
    """Webhook handler to process Telegram updates."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return "OK"

# Command Handlers
def start(update: Update, context: CallbackContext) -> None:
    """Handle the /start command."""
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        update.message.reply_text("Welcome! You are authorized to use this bot.")
    else:
        update.message.reply_text("You are not authorized to use this bot.")

def list_chats(update: Update, context: CallbackContext) -> None:
    """List available chats where the bot is admin."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("You are not authorized to use this bot.")
        return

    if not available_chats:
        update.message.reply_text("No available groups or channels found.")
        return

    chat_list = "\n".join([f"{name} (ID: {chat_id})" for name, chat_id in available_chats.items()])
    update.message.reply_text(f"Available chats:\n{chat_list}")

def post_reply(update: Update, context: CallbackContext) -> None:
    """Post a message by replying to it with /post <chat_title>."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("You are not authorized to use this bot.")
        return

    if not update.message.reply_to_message:
        update.message.reply_text("Please reply to a message with /post <chat_title> to post it.")
        return

    if not context.args:
        update.message.reply_text("Usage: /post <chat_title>")
        return

    chat_title = context.args[0]
    if chat_title not in available_chats:
        update.message.reply_text(f"Chat '{chat_title}' not found. Use /list_chats to see available options.")
        return

    # Get the original message content
    original_message = update.message.reply_to_message.text
    chat_id = available_chats[chat_title]

    # Post the message to the chosen chat
    bot.send_message(chat_id=chat_id, text=original_message)
    update.message.reply_text(f"Content posted to '{chat_title}' successfully.")

# Adding Command Handlers to Dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("list_chats", list_chats))
dispatcher.add_handler(CommandHandler("post", post_reply))

# Main entry point for Vercel
if __name__ == "__main__":
    app.run(port=8000)
