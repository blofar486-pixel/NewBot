import random
import logging
from datetime import datetime, timedelta
import pytz
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# AWS/Railway Live Logs Monitoring
logging.basicConfig(level=logging.INFO)

# ⚠️ YAHAN APNA ASAL TELEGRAM TOKEN DIRECT PASTE KAREIN
BOT_TOKEN = "YAHAN_APNA_TELEGRAM_TOKEN_PASTE_KAREIN" 

bot = telebot.TeleBot(BOT_TOKEN)
PK_TZ = pytz.timezone('Asia/Karachi')

PAIRS_CATEGORIES = {
    "majors": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF", "NZD/USD"],
    "euro": ["EUR/GBP", "EUR/JPY", "EUR/AUD", "EUR/CAD", "EUR/CHF", "EUR/NZD"],
    "gbp": ["GBP/JPY", "GBP/AUD", "GBP/CAD", "GBP/CHF", "GBP/NZD"],
    "cross": ["AUD/JPY", "AUD/CAD", "AUD/CHF", "NZD/JPY", "NZD/CAD", "CAD/JPY"],
    "exotics": ["USD/SGD", "USD/HKD", "USD/TRY", "USD/ZAR", "USD/MXN", "USD/INR", "USD/BRL", "USD/PKR"]
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"🟢 Start command received from Chat ID: {message.chat.id}") # Yeh log check karne ke liye hai
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 Forex Majors", callback_data="c_majors"),
        InlineKeyboardButton("🇪🇺 EUR Crosses", callback_data="c_euro"),
        InlineKeyboardButton("🇬🇧 GBP Crosses", callback_data="c_gbp"),
        InlineKeyboardButton("🇦🇺 Minor Crosses", callback_data="c_cross"),
        InlineKeyboardButton("📊 Exotics", callback_data="c_exotics")
    )
    bot.reply_to(message, "📊 **RQT Future Signal Generator V3.0**\n\nKisi aik category par click karke pairs load karein:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('c_'))
def handle_category(call):
    bot.answer_callback_query(call.id)
    cat = call.data.replace("c_", "")
    pairs = PAIRS_CATEGORIES.get(cat, [])
    
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(p, callback_data=f"p_{p}") for p in pairs]
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("⬅️ Main Menu", callback_data="back_main"))
    
    bot.edit_message_text(f"💱 **Select Asset Pair ({cat.upper()}):**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def handle_pair(call):
    bot.answer_callback_query(call.id)
    selected_pair = call.data.replace("p_", "")
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("⏱️ 1 Min Expiry", callback_data=f"t_1m_{selected_pair}"),
        InlineKeyboardButton("⏱️ 5 Min Expiry", callback_data=f"t_5m_{selected_pair}"),
        InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_main")
    )
    bot.edit_message_text(f"Asset Selected: **{selected_pair}**\n\nAb expiry timeframe select karein:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('t_'))
def generate_signals(call):
    bot.answer_callback_query(call.id)
    raw_data = call.data.replace("t_", "")
    timeframe, pair = raw_data.split("_", 1)
    
    now_pk = datetime.now(PK_TZ)
    output = f"🎯 **RQT FUTURE SIGNALS FOR {pair}** 🎯\n"
    output += f"⏰ Generated At: {now_pk.strftime('%I:%M:%S %p')} (PKT)\n"
    output += f"⏳ Expiry: {timeframe.upper()}\n\n"
    
    intervals = [2, 5, 8] if timeframe == "1m" else [5, 15, 25]
    for idx, gap in enumerate(intervals, 1):
        future_time = now_pk + timedelta(minutes=gap)
        calc_seed = sum(ord(c) for c in pair) + future_time.minute + idx
        direction = "🟢 CALL (UP) 📈" if (calc_seed % 2 == 0) else "🔴 PUT (DOWN) 📉"
        
        output += f"📶 **Signal #{idx}**\n"
        output += f"⏰ Time: `{future_time.strftime('%I:%M %p')}`\n"
        output += f"🎯 Direction: {direction}\n"
        output += "-------------------------\n"
        
    output += "\n⚠️ *Use MTG 1 if the first candle ends in OTM.*"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 New Analysis", callback_data="back_main"))
    
    bot.edit_message_text(output, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_main(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 Forex Majors", callback_data="c_majors"),
        InlineKeyboardButton("🇪🇺 EUR Crosses", callback_data="c_euro"),
        InlineKeyboardButton("🇬🇧 GBP Crosses", callback_data="c_gbp"),
        InlineKeyboardButton("🇦🇺 Minor Crosses", callback_data="c_cross"),
        InlineKeyboardButton("📊 Exotics", callback_data="c_exotics")
    )
    bot.edit_message_text("📊 **RQT Future Signal Generator V3.0**\n\nKisi aik category par click karke pairs load karein:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

print("🚀 Telebot Engine Main Loop Started...")
bot.infinity_polling()
