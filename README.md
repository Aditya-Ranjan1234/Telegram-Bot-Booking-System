# Telegram-Bot-Booking-System

## Overview
The Mingos College Food Booking System is a Telegram bot that streamlines the food ordering process for students and staff. Users can browse the menu, select items, choose a preferred time slot, and complete their orders effortlessly. The backend is powered by PostgreSQL, ensuring data persistence and scalability.

---

## Features
1. **Interactive Menu Browsing**: Users can view the menu, add items to their basket, and adjust quantities using inline buttons.
2. **Time Slot Selection**: Book a preferred time slot to avoid queues.
3. **Order Summary and Checkout**: View a detailed order summary and proceed to payment.
4. **Persistent Storage**: All data, including menu items, orders, and time slots, is stored in a PostgreSQL database.
5. **Token Management**: Generate unique token numbers for each order to streamline the pickup process.
6. **Payment Integration**: Provides a link for completing payments via Google Pay.

---

## Installation

### Prerequisites
- Python 3.9 or higher
- PostgreSQL database
- Telegram Bot Token (from @BotFather)

### Setup Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Aditya-Ranjan1234/Telegram-Bot-Booking-System.git
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Database**:
   - Create a PostgreSQL database named `mingos_cafe`.
   - Execute the provided SQL script (`database_setup.sql`) to create the necessary tables.

   Example:
   ```sql
   CREATE TABLE menu (
       item VARCHAR(100) PRIMARY KEY,
       price INTEGER NOT NULL
   );

   CREATE TABLE orders (
       order_id SERIAL PRIMARY KEY,
       token_number INTEGER NOT NULL,
       items JSONB NOT NULL,
       total_price INTEGER NOT NULL,
       time_slot VARCHAR(20) NOT NULL,
       order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

4. **Configure Environment Variables**:
   Create a `.env` file with the following details:
   ```env
   TELEGRAM_TOKEN=your_bot_token
   DATABASE_URL=postgresql://username:password@localhost:5432/mingos_cafe
   ```

5. **Run the Bot**:
   ```bash
   python main.py
   ```

---

## Usage
1. Start the bot on Telegram by sending `/start`.
2. View the menu using `/menu`.
3. Select items and quantities using the interactive buttons.
4. Proceed to time slot selection.
5. Review your order using `/order`.
6. Complete the order and payment using `/checkout`.
7. View your basket details anytime with `/counter`.

---

## File Structure
```
mingos-cafe-bot/
|-- main.py                 # Main bot logic
|-- menu.csv                # Menu items and prices
|-- requirements.txt        # Python dependencies
|-- database_setup.sql      # SQL script for database initialization
|-- .env                    # Environment variables
|-- README.md               # Project documentation
```

---

## Licensing
This project is licensed under the [GNU General Public License (GPL)](https://www.gnu.org/licenses/gpl-3.0.en.html). You are free to modify and distribute the software under the terms of the GPL.

---

## Contributing
We welcome contributions to improve the Mingos College Cafe Food Booking System. To contribute:
1. Fork the repository.
2. Create a new branch for your feature/bug fix.
3. Submit a pull request with a detailed description.

---

## Acknowledgements
1.Diptanshu Kumar
2.Garv Agarwalla
3.Ahibhruth A


