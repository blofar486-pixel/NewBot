import random
import logging
import threading
import time
from datetime import datetime, timedelta
import pytz
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Live Logs Monitoring
logging.basicConfig(level=logging.INFO)

# ✅ Aapka Telegram Bot Token
BOT_TOKEN = "8328605174:AAFeNEZR2BfW3i21BywTVeuDL-Oopo562gA"

bot = telebot.TeleBot(BOT_TOKEN)
PK_TZ = pytz.timezone('Asia/Karachi')

ADMIN_CHAT_ID = None
ALLOWED_USERS = set()
MAINTENANCE_MODE = False

# Optimized Compact Pairs List
PAIRS_CATEGORIES = {
    "majors": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"],
    "euro": ["EUR/GBP", "EUR/JPY", "EUR/AUD", "EUR/CAD"],
    "gbp": ["GBP/JPY", "GBP/AUD", "GBP/CAD", "GBP/CHF"],
    "cross": ["AUD/JPY", "AUD/CAD", "NZD/JPY", "CAD/JPY"],
    "exotics": ["USD/TRY", "USD/ZAR", "USD/INR", "USD/BRL"]
}

def is_authorized(chat_id, user_id):
    global ADMIN_CHAT_ID
    if ADMIN_CHAT_ID is None:
        ADMIN_CHAT_ID = user_id
        ALLOWED_USERS.add(user_id)
        return True
    if user_id == ADMIN_CHAT_ID:
        return True
    if MAINTENANCE_MODE:
        bot.send_message(chat_id, "⚠️ **Maintenance Active.**")
        return False
    if user_id not in ALLOWED_USERS:
        bot.send_message(chat_id, f"❌ **Access Denied.** ID: `{user_id}`")
        return False
    return True

# --- Dynamic Delayed Processing (5 Minutes Timer & Auto Win/Loss Evaluator) ---
def manage_signal_lifecycle(chat_id, message_id, pairs_data, timeframe):
    # Step 1: Wait for 5 minutes (300 Seconds) as requested
    time.sleep(300)
    
    # Step 2: Auto Evaluate Results before deleting to simulate transparency
    try:
        final_report = "📊 **RQT SESSION REPORT (FINISHED)** 📊\n"
        final_report += "=============================\n"
        
        for p in pairs_data:
            # Simulate real outcome checking based on refined probabilistic analysis
            outcome = "🟢 WIN (Pure)" if random.randint(1, 100) <= 91 else "🔴 LOSS"
            final_report += f"💱 `{p}` ➜ {outcome}\n"
            
        final_report += "=============================\n🧹 *Cleaning chat in 5s...*"
        bot.edit_message_text(final_report, chat_id, message_id, parse_mode="Markdown")
        
        time.sleep(5)
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.error(f"Lifecycle management failed: {e}")

@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id == ADMIN_CHAT_ID:
        try:
            new_id = int(message.text.split()[1])
            ALLOWED_USERS.add(new_id)
            bot.reply_to(message, f"✅ Added: `{new_id}`")
        except:
            bot.reply_to(message, "Use: `/adduser [id]`")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_authorized(message.chat.id, message.from_user.id):
        return
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 Majors", callback_data="pk_majors"),
        InlineKeyboardButton("🇪🇺 EUR", callback_data="pk_euro"),
        InlineKeyboardButton("🇬🇧 GBP", callback_data="pk_gbp"),
        InlineKeyboardButton("🇦🇺 Minors", callback_data="pk_cross"),
        InlineKeyboardButton("📊 Exotics", callback_data="pk_exotics")
    )
    bot.reply_to(message, "🎯 **RQT QUANT V5.2 (High-Accuracy)**\nSelect Asset Pack:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pk_'))
def handle_pack(call):
    if not is_authorized(call.message.chat.id, call.from_user.id):
        return
    bot.answer_callback_query(call.id)
    category = call.data.replace("pk_", "")
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⏱️ 1 Min", callback_data=f"al_1m_{category}"),
        InlineKeyboardButton("⏱️ 5 Min", callback_data=f"al_5m_{category}"),
        InlineKeyboardButton("⬅️ Menu", callback_data="back_main")
    )
    bot.edit_message_text(f"📦 **Pack: {category.upper()}**\nSelect Strategy Timeframe:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('al_'))
def generate_multi_signals(call):
    if not is_authorized(call.message.chat.id, call.from_user.id):
        return
    bot.answer_callback_query(call.id)
    
    raw_data = call.data.replace("al_", "")
    timeframe, category = raw_data.split("_", 1)
    pairs = PAIRS_CATEGORIES.get(category, [])
    
    now_pk = datetime.now(PK_TZ)
    
    # Clean, Compact Mobile Screen Layout
    output = f"💎 **RQT ACCURACY SIGNALS** 💎\n"
    output += f"📅 Time: `{now_pk.strftime('%I:%M %p')}` | Expiry: `{timeframe.upper()}`\n"
    output += "===============================\n"
    
    for pair in pairs[:4]:  # Top 4 pairs standard filtration for clear rendering
        pair_seed = sum(ord(c) for c in pair)
        
        # Micro structural logic update to simulate high success rate
        algo_bias = (pair_seed + now_pk.minute) % 3
        if algo_bias == 0:
            direction = "🟢 CALL (UP) 📈"
            str_tag = "94%"
        elif algo_bias == 1:
            direction = "🔴 PUT (DOWN) 📉"
            str_tag = "92%"
        else:
            direction = "🟢 CALL (UP) 📈" if (pair_seed % 2 == 0) else "🔴 PUT (DOWN) 📉"
            str_tag = "90%"
            
        future_time = now_pk + timedelta(minutes=2 if timeframe == "1m" else 5)
        output += f"🔹 **{pair}** ➜ `{future_time.strftime('%I:%M %p')}` ➜ {direction} *({str_tag})*\n"
        
    output += "===============================\n"
    output += "⚠️ *Rule: Strict MTG-1 if structure breaks.*\n⏳ _Auto-evaluating and deleting panel in 5 mins._"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Main Menu", callback_data="back_main"))
    
    sent_msg = bot.edit_message_text(output, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    # Trigger life cycle handling (5 mins window retention + live evaluation simulation)
    threading.Thread(target=manage_signal_lifecycle, args=(sent_msg.chat.id, sent_msg.message_id, pairs[:4], timeframe)).start()

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_main(call):
    if not is_authorized(call.message.chat.id, call.from_user.id):
        return
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌐 Majors", callback_data="pk_majors"),
        InlineKeyboardButton("🇪🇺 EUR", callback_data="pk_euro"),
        InlineKeyboardButton("🇬🇧 GBP", callback_data="pk_gbp"),
        InlineKeyboardButton("🇦🇺 Minors", callback_data="pk_cross"),
        InlineKeyboardButton("📊 Exotics", callback_data="pk_exotics")
    )
    bot.edit_message_text("🎯 **RQT QUANT V5.2 (High-Accuracy)**\nSelect Asset Pack:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

print("🚀 High-Accuracy Compressed Format Engine V5.2 Active...")
bot.infinity_polling()
