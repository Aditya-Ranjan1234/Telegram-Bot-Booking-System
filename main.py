import logging
import csv
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

item_count = 0
token_number = 1  
menu_items = {}
item_basket = {} 
time_slots = []
selected_time_slot = None  

def load_menu():
    global menu_items
    with open('D:\\Projects\\Mingos\\menu.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            menu_items[row['item']] = int(row['price'])

def generate_time_slots():
    global time_slots
    now = datetime.now()
    time_slots = []
    for i in range(4): 
        slot_time = now + timedelta(minutes=i * 15)
        time_slots.append(slot_time.strftime("%I:%M %p"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome! Use /menu to see the available items.')

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for item, price in menu_items.items():
        keyboard.append([InlineKeyboardButton(f"{item} - ₹{price}", callback_data=item)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose an item:', reply_markup=reply_markup)

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    generate_time_slots()
    keyboard = [[InlineKeyboardButton(time, callback_data=time)] for time in time_slots]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select a time slot:', reply_markup=reply_markup)

async def counter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if item_basket:
        basket_message = "Items in your cart:\n"
        total_price = 0
        for item, quantity in item_basket.items():
            price = menu_items.get(item, 0)
            total_price += price * quantity
            basket_message += f"{item} - Quantity: {quantity} - ₹{price * quantity}\n"
        basket_message += f"\nTotal Price: ₹{total_price}"
        await update.message.reply_text(basket_message)
    else:
        await update.message.reply_text("Your cart is empty.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global item_basket, selected_time_slot
    query = update.callback_query
    await query.answer()

    if query.data in menu_items:
        if query.data in item_basket:
            item_basket[query.data] += 1
        else:
            item_basket[query.data] = 1
        await query.edit_message_text(text=f"{query.data} added to cart. Current count: {item_basket[query.data]}")
    elif query.data == 'checkout':
        await checkout(update, context)
    elif query.data in time_slots:
        selected_time_slot = query.data
        await query.edit_message_text(text=f"Time slot {query.data} selected.")
    else:
        await query.edit_message_text(text="Invalid option selected.")

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global item_basket, token_number, selected_time_slot
    if item_basket and selected_time_slot:
        basket_message = "Your order:\n"
        total_price = 0
        for item, quantity in item_basket.items():
            price = menu_items.get(item, 0)
            total_price += price * quantity
            basket_message += f"{item} - Quantity: {quantity} - ₹{price * quantity}\n"
        basket_message += f"\nTotal Price: ₹{total_price}\n"
        basket_message += f"Time Slot: {selected_time_slot}\n"
        basket_message += f"Token number: {token_number}\n"
        basket_message += "Please complete your payment here: [Google Pay Link]"

        await update.callback_query.edit_message_text(basket_message)
        
        token_number += 1
        item_basket.clear()
        selected_time_slot = None  
    else:
        await update.callback_query.edit_message_text("No items in cart or time slot not selected. Please add items and select a time slot before checking out.")

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global item_basket, selected_time_slot
    if item_basket:
        basket_message = "Your order details:\n"
        total_price = 0
        for item, quantity in item_basket.items():
            price = menu_items.get(item, 0)
            total_price += price * quantity
            basket_message += f"{item} - Quantity: {quantity} - ₹{price * quantity}\n"
        basket_message += f"\nTotal Price: ₹{total_price}\n"
        basket_message += f"Time Slot: {selected_time_slot if selected_time_slot else 'Not selected'}\n"
        await update.message.reply_text(basket_message)
    else:
        await update.message.reply_text("No items in cart. Please add items to your order.")

def main() -> None:
    load_menu()

    application = ApplicationBuilder().token("  ").build()
  
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", show_menu))
    application.add_handler(CommandHandler("time", time))
    application.add_handler(CommandHandler("counter", counter))
    application.add_handler(CommandHandler("order", order)) 
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()
