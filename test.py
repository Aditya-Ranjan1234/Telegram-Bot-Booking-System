import logging
import csv
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

item_basket = {}
menu_items = {}
time_slots = []
selected_time_slot = None
token_number = 1  

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
    if update.message:
        reply_to = update.message
    else:
        reply_to = update.callback_query.message
    
    keyboard = []
    for item, price in menu_items.items():
        
        keyboard.append([
            InlineKeyboardButton(f"-", callback_data=f"decrease_{item}"),
            InlineKeyboardButton(f"{item} - ₹{price}", callback_data=f"view_{item}"),
            InlineKeyboardButton(f"+", callback_data=f"increase_{item}")
        ])

    keyboard.append([InlineKeyboardButton("Next", callback_data="next_step")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await reply_to.reply_text('Please select items and adjust quantities (click + or - to change):', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global item_basket, selected_time_slot
    query = update.callback_query
    await query.answer()

    if query.data.startswith("increase_"):
        item = query.data.split("_")[1]
        item_basket[item] = item_basket.get(item, 0) + 1
        await query.edit_message_text(text=f"{item} quantity increased to {item_basket[item]}.")
        await show_menu(update, context) 
    
    elif query.data.startswith("decrease_"):
        item = query.data.split("_")[1]
        if item_basket.get(item, 0) > 0:
            item_basket[item] -= 1
            await query.edit_message_text(text=f"{item} quantity decreased to {item_basket[item]}.")
        else:
            await query.edit_message_text(text=f"Cannot decrease {item} further.")
        await show_menu(update, context)  
    elif query.data == "next_step":
        if item_basket:
            await time(update, context) 
        else:
            await query.edit_message_text("You haven't added any items yet. Please select items first.")

    elif query.data in time_slots:
        selected_time_slot = query.data
        await query.edit_message_text(text=f"Time slot {query.data} selected.")
    
    else:
        await query.edit_message_text(text="Invalid option selected.")

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    generate_time_slots()
    keyboard = [[InlineKeyboardButton(time, callback_data=time) for time in time_slots]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text('Select a time slot:', reply_markup=reply_markup)

async def counter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    basket_details = "Your basket:\n"
    total_price = 0
    for item, qty in item_basket.items():
        price = menu_items[item]
        basket_details += f"{item} x{qty} - ₹{price * qty}\n"
        total_price += price * qty

    basket_details += f"\nTotal Price: ₹{total_price}"
    await update.message.reply_text(basket_details)

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global item_basket, token_number
    if item_basket:
        message = f"Your order: {len(item_basket)} items. Token number: {token_number}."
        await update.callback_query.edit_message_text(message)
    
        await update.callback_query.message.reply_text("Please complete your payment here: [Google Pay Link]")
        token_number += 1  
        item_basket = {}  
    else:
        await update.callback_query.edit_message_text("No items in cart. Please add items before checking out.")

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global item_basket, selected_time_slot
    order_details = "Your Order Details:\n"
    total_price = 0
    for item, qty in item_basket.items():
        price = menu_items[item]
        order_details += f"{item} x{qty} - ₹{price * qty}\n"
        total_price += price * qty

    order_details += f"\nTotal Price: ₹{total_price}"
    if selected_time_slot:
        order_details += f"\nTime slot: {selected_time_slot}"

    await update.message.reply_text(order_details)

def main() -> None:
    load_menu()

    application = ApplicationBuilder().token("  ").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", show_menu))
    application.add_handler(CommandHandler("time", time))
    application.add_handler(CommandHandler("counter", counter))
    application.add_handler(CommandHandler("checkout", checkout))
    application.add_handler(CommandHandler("order", order))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()
