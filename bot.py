TOKEN = ''

import pandas as pd
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext , Application
from datetime import datetime
import random  # for generating UPI payment links

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the menu CSV
menu = pd.read_csv('menu.csv')  # Assuming the CSV has columns 'item' and 'price'

# Bot states
START, MENU, ORDER = range(3)

# Dictionary for storing user orders
user_orders = {}

# Function to start the bot
async def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    await update.message.reply_text(f"Hi {user.first_name}, I am your bot. Please choose an option:\n"
                                   "1. Type /start to place an order.\n"
                                   "2. Type /menu to view the menu.")
    return START

# Function to show the menu
async def show_menu(update: Update, context: CallbackContext) -> int:
    menu_text = "Here is the menu:\n"
    for idx, row in menu.iterrows():
        menu_text += f"{row['item']} - ₹{row['price']}\n"
    await update.message.reply_text(menu_text)
    return MENU

# Function to handle user order
async def take_order(update: Update, context: CallbackContext) -> int:
    order_text = update.message.text
    # Simple keyword-based order parsing
    order_items = []
    for idx, row in menu.iterrows():
        if row['item'].lower() in order_text.lower():
            order_items.append(row['item'])
    
    if order_items:
        total_price = sum(menu[menu['item'] == item]['price'].values[0] for item in order_items)
        user_orders[update.message.from_user.id] = order_items
        
        # Generate payment link (dummy link in this case)
        payment_link = f"upi://pay?pa=yourupi@bank&pn=YourName&mc=0000&tid={random.randint(100000, 999999)}&am={total_price}&cu=INR"
        
        await update.message.reply_text(f"Your order: {', '.join(order_items)}\n"
                                       f"Total price: ₹{total_price}\n"
                                       f"To complete your order, please pay using UPI: {payment_link}")
        return ORDER
    else:
        await update.message.reply_text("Sorry, I couldn't understand your order. Please type it again.")
        return ORDER

# Function to confirm order
async def confirm_order(update: Update, context: CallbackContext) -> int:
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    await update.message.reply_text(f"Order placed successfully at {current_time}. Thank you!")
    return ConversationHandler.END

# Error handling function
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Main function to set up conversation handler
def main() -> None:
    # Set up the application (formerly Updater)
    application = Application.builder().token(TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('menu', show_menu)],
        states={
            START: [MessageHandler(filters.TEXT & ~filters.COMMAND, take_order)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_menu)],
            ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, error))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
