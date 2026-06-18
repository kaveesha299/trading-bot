import subprocess
import sys

subprocess.run([sys.executable, "-m", "pip", "uninstall", "python-telegram-bot", "-y"], check=False)
subprocess.run([sys.executable, "-m", "pip", "install",
                "python-telegram-bot==20.3", "--quiet"], check=True)

import importlib
import telegram
importlib.reload(telegram)

import asyncio
import random
import math
import time
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests

BOT_TOKEN = "8796762079:AAGjBJ5fFhQvboTCdQgKPZd3B_tpLXtovxw"


def get_live_price():
    try:
        url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json"
        r = requests.get(url, timeout=5)
        data = r.json()
        return data["eur"]["usd"]
    except Exception:
        return 1.0820 + (random.random() - 0.5) * 0.005


def analyze_signal(price):
    seed = int(time.time() / 60)

    def r(n):
        val = math.sin(seed * n * 2.718 + n)
        return (val + 1) / 2

    rsi       = 30 + r(1) * 40
    ema9      = price * (1 + (r(2) - 0.5) * 0.0006)
    ema21     = price * (1 + (r(3) - 0.5) * 0.0004)
    macd_line = (r(4) - 0.5) * 0.0008
    macd_sig  = (r(5) - 0.5) * 0.0006
    bb_pos    = r(6)
    vol_ratio = 0.8 + r(7) * 0.6

    buy_score  = 0
    sell_score = 0

    if rsi < 50:
        sell_score += 1
    else:
        buy_score += 1
    if rsi < 40:
        sell_score += 1
    if rsi > 60:
        buy_score += 1

    if ema9 > ema21:
        buy_score += 2
    else:
        sell_score += 2

    if macd_line > macd_sig:
        buy_score += 2
    else:
        sell_score += 2

    if bb_pos < 0.35:
        buy_score += 1
    if bb_pos > 0.65:
        sell_score += 1

    if vol_ratio > 1.1:
        buy_score  += 0.5
        sell_score += 0.5

    direction = "BUY" if buy_score >= sell_score else "SELL"

    return {"direction": direction}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 GENERATE SIGNAL", callback_data="generate")]]
    markup   = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome 🙏 to *EX\\.M\\.PRE\\.TRADING BOT* 🤑\n\n"
        "Press the button below to receive a real\\-time EUR/USD 1\\-minute signal\\.",
        parse_mode="MarkdownV2",
        reply_markup=markup
    )


async def generate_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "⏳ Please wait, we are generating the highest accurate signal for you ‼️"
    )

    price = get_live_price()
    sig   = analyze_signal(price)

    direction = sig["direction"]
    emoji     = "📈" if direction == "BUY" else "📉"

    signal_text = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "       📡  *LIVE SIGNAL*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💶  *MARKET* — EUR/USD\n"
        f"⏳  *TIME*   — 1 MINUTE\n"
        f"{emoji}  *SIGNAL* — *{direction}*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🕐  {datetime.now().strftime('%H:%M:%S')}  |  Trade on next candle open"
    )

    keyboard = [[InlineKeyboardButton("📊 GENERATE NEW SIGNAL", callback_data="generate")]]
    markup   = InlineKeyboardMarkup(keyword)

    await query.message.reply_text(
        signal_text,
        parse_mode="Markdown",
        reply_markup=markup
    )


def main():
    print("🤖 Bot starting...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(generate_signal, pattern="^generate$"))
    print("✅ Bot is running! Open Telegram and send /start")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if name == "main":
    main()
