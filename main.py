from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Store the list of groups where the bot is a member
group_ids = set()

# A dictionary to store button click counts
click_counts = {}

# Bot's admin ID (replace with the actual bot admin's user ID)
BOT_ADMIN_IDs = [6426448705, 2024249696]  # Replace with the admin user ID (numeric)

greeting_message = 'Assalomu aleykum. I am an official SP bot of Millat Umidi University.'

# Function to add a group to the list of groups
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ['group', 'supergroup']:
        group_ids.add(chat.id)
        await update.message.reply_text(greeting_message)


# Function to check if the user is the bot's admin
async def is_bot_admin(user_id: int) -> bool:
    return user_id in BOT_ADMIN_IDs


# Function to handle photos (with optional captions) sent to the bot
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_type = update.effective_chat.type

    # Only process messages from personal chat sent by the admin
    if chat_type == 'private' and await is_bot_admin(user_id):
        if group_ids:
            photo = update.message.photo[-1]  # Get the highest resolution photo
            caption = update.message.caption or ""  # Optional caption
            for group_id in group_ids:
                try:
                    # Create a unique callback data key for this photo
                    callback_key = f"photo_{group_id}_{update.message.message_id}"
                    click_counts[callback_key] = 0  # Initialize click count

                    # Create an inline keyboard button
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("\u2714", callback_data=callback_key)]
                    ])

                    # Send the photo with the button
                    sent_message = await context.bot.send_photo(chat_id=group_id, photo=photo.file_id, caption=caption,
                                                                reply_markup=keyboard)

                    # Pin the message after sending it
                    await context.bot.pin_chat_message(chat_id=group_id, message_id=sent_message.message_id)
                except Exception as e:
                    print(f"Failed to send and pin photo to group {group_id}: {e}")
        else:
            await update.message.reply_text("No groups have been registered yet.")
    else:
        await update.message.reply_text("You are not authorized to send messages.")


# Function to handle videos (with optional captions) sent to the bot
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_type = update.effective_chat.type

    # Only process messages from personal chat sent by the admin
    if chat_type == 'private' and await is_bot_admin(user_id):
        if group_ids:
            video = update.message.video  # Get the video file
            caption = update.message.caption or ""  # Optional caption
            for group_id in group_ids:
                try:
                    # Create a unique callback data key for this video
                    callback_key = f"video_{group_id}_{update.message.message_id}"
                    click_counts[callback_key] = 0  # Initialize click count

                    # Create an inline keyboard button
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("\u2714", callback_data=callback_key)]
                    ])

                    # Send the video with the button
                    sent_message = await context.bot.send_video(chat_id=group_id, video=video.file_id, caption=caption,
                                                                reply_markup=keyboard)

                    # Pin the message after sending it
                    await context.bot.pin_chat_message(chat_id=group_id, message_id=sent_message.message_id)
                except Exception as e:
                    print(f"Failed to send and pin video to group {group_id}: {e}")
        else:
            await update.message.reply_text("No groups have been registered yet.")
    else:
        await update.message.reply_text("You are not authorized to send messages.")


# Function to handle text messages sent to the bot
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_type = update.effective_chat.type

    # Only process messages from personal chat sent by the admin
    if chat_type == 'private' and await is_bot_admin(user_id):
        if group_ids:
            text = update.message.text
            for group_id in group_ids:
                try:
                    # Create a unique callback data key for this text
                    callback_key = f"text_{group_id}_{update.message.message_id}"
                    click_counts[callback_key] = 0  # Initialize click count

                    # Create an inline keyboard button
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("\u2714", callback_data=callback_key)]
                    ])

                    # Send the text with the button
                    sent_message = await context.bot.send_message(chat_id=group_id, text=text, reply_markup=keyboard)

                    # Pin the message after sending it
                    await context.bot.pin_chat_message(chat_id=group_id, message_id=sent_message.message_id)
                except Exception as e:
                    print(f"Failed to send and pin message to group {group_id}: {e}")
        else:
            await update.message.reply_text("No groups have been registered yet.")
    else:
        pass


# Global dictionaries to track clicks and users
global_click_counts = {}  # Tracks total click counts for each button
global_click_users = {}   # Tracks users who clicked each button globally

# Function to handle button clicks
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data

    await query.answer()  # Acknowledge the callback query

    # Initialize tracking for this button globally
    if callback_data not in global_click_users:
        global_click_users[callback_data] = set()  # Set of users who clicked
        global_click_counts[callback_data] = 0     # Total click count

    # Check if the user has already clicked this button globally
    if user_id in global_click_users[callback_data]:
        await query.answer("You can only click once across all groups!", show_alert=True)
        return 1

    # Add the user to the global set of users who clicked
    global_click_users[callback_data].add(user_id)

    # Increment the global click count
    global_click_counts[callback_data] += 1
    count = global_click_counts[callback_data]

    # Update the button text with the new count globally
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"\u2714 {count}", callback_data=callback_data)]
    ])
    try:
        await query.edit_message_reply_markup(reply_markup=keyboard)
    except Exception as e:
        print(f"Failed to update button: {e}")


# Function to display button press statistics to the bot's admin
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Check if the user is the bot's admin
    if await is_bot_admin(user_id):
        if global_click_counts:
            stats_message = "Button Press Statistics:\n\n"
            for callback_data, count in global_click_counts.items():
                stats_message += f"{callback_data}: {count} presses\n"
            await update.message.reply_text(stats_message)
        else:
            await update.message.reply_text("No button press data available yet.")
    else:
        await update.message.reply_text("You are not authorized to view statistics.")



# Start command for the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a photo, a video, or a text message, and I’ll forward it to the groups I’m in. Only the bot's admin can send messages."
    )


# Main function to start the bot
def main():
    TOKEN = "7757218255:AAGbCKc1W3NZuwy43iP_D0vNAaWh0NS7iWg"
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))  # Video handler
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # Photo handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))  # Text handler
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.StatusUpdate.NEW_CHAT_MEMBERS, add_group))
    app.add_handler(CallbackQueryHandler(button_click))  # Handle button clicks
    app.add_handler(CommandHandler("stats", show_stats))  # Add the stats command

    # Run the bot
    app.run_polling()


if __name__ == "__main__":
    main()

#699475942708
