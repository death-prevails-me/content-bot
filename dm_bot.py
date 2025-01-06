from telegram import Update, Message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace with your bot token
BOT_TOKEN = '7647501362:AAEnUPclHfX72Xsn4ghaxtUCDAHLm5gVfwA'

# Replace with a list of authorized user IDs
AUTHORIZED_USERS = [1139405017]

# Dictionary to store groups and channels where the bot is admin
available_chats = {}

def start(update: Update, context: CallbackContext) -> None:
    """Start command to welcome the user."""
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        update.message.reply_text("Welcome! You are authorized to use this bot.")
    else:
        update.message.reply_text("You are not authorized to use this bot.")

def update_chat_list(context: CallbackContext) -> None:
    """Fetch and update the list of groups and channels."""
    bot = context.bot
    global available_chats
    available_chats = {}  # Reset the list

    # Use getUpdates to fetch recent chats and check admin rights
    updates = bot.get_updates()

    for update in updates:
        chat = update.message.chat if update.message else None
        if chat and chat.type in ["group", "supergroup", "channel"]:
            chat_member = bot.get_chat_member(chat.id, bot.id)
            if chat_member.status in ["administrator", "creator"]:
                available_chats[chat.title] = chat.id

def list_chats(update: Update, context: CallbackContext) -> None:
    """List available groups and channels where the bot can post."""
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("You are not authorized to use this bot.")
        return

    if not available_chats:
        update_chat_list(context)

    if available_chats:
        chat_list = "\n".join([f"{name} (ID: {chat_id})" for name, chat_id in available_chats.items()])
        update.message.reply_text(f"Available chats:\n{chat_list}")
    else:
        update.message.reply_text("No available groups or channels found.")

def post_reply(update: Update, context: CallbackContext) -> None:
    """Post content by replying to a message with /post <chat_title>."""
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
    bot = context.bot
    bot.send_message(chat_id=chat_id, text=original_message)
    update.message.reply_text(f"Content posted to '{chat_title}' successfully.")

def main():
    """Main function to set up the bot."""
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("list_chats", list_chats))
    dispatcher.add_handler(CommandHandler("post", post_reply))

    # Start the bot
    updater.start_polling()

    # Periodically update the chat list
    job_queue = updater.job_queue
    job_queue.run_repeating(update_chat_list, interval=600, first=0)

    updater.idle()

if __name__ == "__main__":
    main()
