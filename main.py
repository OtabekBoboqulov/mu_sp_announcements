from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import logging

import os

# Replace with your bot token

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN environment variable found!")


# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# List of admin user IDs
ADMIN_IDS = [6426448705]  # Replace with the Telegram user ID(s) of the admin(s)

# List to store chat IDs of groups where the bot is a member
group_chats = set()

# Function to add group chat IDs when the bot joins a group
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        group_chats.add(chat.id)
        await update.message.reply_text("Hello! I've joined this group.")

# Command to display the current list of groups
async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        group_list = "\n".join([str(chat_id) for chat_id in group_chats])
        if group_list:
            await update.message.reply_text(f"I'm currently a member of these groups:\n{group_list}")
        else:
            await update.message.reply_text("I'm not a member of any groups.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

# Forward a message sent by the admin to all groups
async def forward_to_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        message = update.message.text or update.message.caption
        for chat_id in group_chats:
            await context.bot.send_message(chat_id=chat_id, text=message)
    else:
        await update.message.reply_text("You are not authorized to send messages to groups.")

# Main function to start the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, add_group))
    application.add_handler(CommandHandler("list_groups", list_groups))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, forward_to_groups))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
