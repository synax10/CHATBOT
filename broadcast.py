from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3

# Initialize the SQLite database
conn = sqlite3.connect('bot_stats.db')
cursor = conn.cursor()

# Create a table to store group information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY,
        name TEXT,
        members_count INTEGER
    )
''')
conn.commit()

# Function to handle the /broadcast command
def broadcast(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type == 'private':
        context.bot.send_message(update.message.chat_id, "Broadcast not available in private chats.")
    else:
        groups = cursor.execute('SELECT id FROM groups').fetchall()
        message = 'Broadcast message:\n\n' + ' '.join(context.args)

        for group_id in groups:
            context.bot.send_message(group_id[0], message)

# Function to handle new members in a group
def new_member(update: Update, context: CallbackContext) -> None:
    if update.message.new_chat_members:
        group_id = update.message.chat.id
        group_name = update.message.chat.title
        members_count = len(update.message.new_chat_members)

        # Update or insert group information
        cursor.execute('''
            INSERT OR REPLACE INTO groups (id, name, members_count)
            VALUES (?, ?, ?)
        ''', (group_id, group_name, members_count))
        conn.commit()

# Function to handle the /stats command
def stats(update: Update, context: CallbackContext) -> None:
    groups_count = cursor.execute('SELECT COUNT(id) FROM groups').fetchone()[0]
    context.bot.send_message(update.message.chat_id, f"Bot is connected to {groups_count} groups.")

# Set up the Telegram bot
updater = Updater("YOUR_BOT_TOKEN")
dp = updater.dispatcher

# Add command handlers
dp.add_handler(CommandHandler("broadcast", broadcast, pass_args=True))
dp.add_handler(CommandHandler("stats", stats))
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

# Start the bot
updater.start_polling()
updater.idle()
