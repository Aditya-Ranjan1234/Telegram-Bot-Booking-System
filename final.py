import logging
import csv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(_name_)

menu_items = {}
selected_items = {}
token_number = 1
time_slots = []
selected_time_slot = "Instant"

def load_menu():
    global menu_items
    with open('menu.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            menu_items[row['item']] = int(row['price'])


def generate_time_slots():
    global time_slots
    from datetime import datetime, timedelta
    now = datetime.now()
    time_slots = []
    for i in range(4):
        slot_time = now + timedelta(minutes=i * 15)
        time_slots.append(slot_time.strftime("%I:%M %p"))

async def show_commands(update: Update):
    commands = (
        "/menu - Show food menu\n"
        "/counter - Show items in basket\n"
        "/time - Book a time slot\n"
        "/checkout - Complete your order\n"
        "/clear - Reset all selections"
    )
    await update.message.reply_text(f"Available commands:\n{commands}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use the following commands:")
    await show_commands(update)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{item} - ₹{price}", callback_data=item)] 
        for item, price in menu_items.items()
    ]
    keyboard.append([InlineKeyboardButton("Next", callback_data="next")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select items to add to your basket:", reply_markup=reply_markup)

async def counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_time_slot

    # Determine the correct reply method
    reply_method = (
        update.message.reply_text if update.message 
        else update.callback_query.message.reply_text
    )
    
    if not selected_items:
        await reply_method("Your basket is empty.")
    else:
        total_price = sum(qty * menu_items[item] for item, qty in selected_items.items())
        items_list = "\n".join(
            f"{item}: {qty} x ₹{menu_items[item]}" for item, qty in selected_items.items()
        )
        
        # Show whether the time slot is booked or not
        if selected_time_slot:
            time_info = f"Time Slot: {selected_time_slot}"
        else:
            time_info = "Time Slot: Not booked. Use /time to book a slot."
        
        basket_details = f"Basket:\n{items_list}\n\nTotal: ₹{total_price}\n{time_info}\nProceed to /checkout."
        
        await reply_method(basket_details)



async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_time_slot
    generate_time_slots()
    
    # Keyboard with available time slots
    keyboard = [[InlineKeyboardButton(slot, callback_data=slot)] for slot in time_slots]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Determine the correct reply method
    reply_method = (
        update.message.reply_text if update.message 
        else update.callback_query.message.reply_text
    )
    
    await reply_method("Select a time slot:", reply_markup=reply_markup)


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global token_number
    if not selected_items:
        await update.message.reply_text("Your basket is empty. Add items before checking out.")
        return
    total_price = sum(qty * menu_items[item] for item, qty in selected_items.items())
    await update.message.reply_text(f"Your order has been placed!\nToken: {token_number}\nTotal: ₹{total_price}\nProceed to payment.")
    selected_items.clear()
    token_number += 1

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_items
    selected_items.clear()
    await update.message.reply_text("All selections have been reset.")
    await show_commands(update)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_time_slot
    query = update.callback_query
    await query.answer()

    # Check if the callback data is a valid time slot
    if query.data in time_slots:
        selected_time_slot = query.data
        await query.message.reply_text(f"Time slot {selected_time_slot} has been successfully booked!")
    elif query.data in menu_items:
        selected_items[query.data] = selected_items.get(query.data, 0) + 1
    elif query.data == "next":
        await counter(update, context)


def main():
    load_menu()
    app = ApplicationBuilder().token(" ").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", show_menu))
    app.add_handler(CommandHandler("counter", counter))
    app.add_handler(CommandHandler("time", time))
    app.add_handler(CommandHandler("checkout", checkout))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if _name_ == "_main_":
    main()
