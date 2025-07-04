import os
import logging
import phonenumbers
import re
import requests
from phonenumbers import geocoder
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Logging
logging.basicConfig(level=logging.INFO)

# Environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
E_AUTH = os.getenv("E_AUTH")
E_AUTH_V = os.getenv("E_AUTH_V")
E_AUTH_C = os.getenv("E_AUTH_C")
E_AUTH_K = os.getenv("E_AUTH_K")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 নম্বর পাঠান (দেশ কোড সহ) যেমনঃ +88017xxxxxxx")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text.strip()

    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        country_name = geocoder.description_for_number(parsed_number, "en")
    except phonenumbers.phonenumberutil.NumberParseException:
        await update.message.reply_text("❌ সঠিক আন্তর্জাতিক নম্বর দিন (যেমন: +8801712345678)")
        return

    phone_number_clean = re.sub(r'[^\d]', '', phone_number)

    # First API call for name
    url_name = f"https://api.eyecon-app.com/app/getnames.jsp?cli={phone_number_clean}&lang=en&is_callerid=true&is_ic=true&cv=vc_542_vn_4.0.542_a"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "e-auth-v": E_AUTH_V,
        "e-auth": E_AUTH,
        "e-auth-c": E_AUTH_C,
        "e-auth-k": E_AUTH_K
    }

    response_name = requests.get(url_name, headers=headers)
    if response_name.status_code != 200:
        await update.message.reply_text("❌ নাম আনতে সমস্যা হয়েছে।")
        return

    data = response_name.json()
    name = data[0].get('name', '❓ নাম পাওয়া যায়নি') if data else '❓ নাম পাওয়া যায়নি'

    # Second API call for photo
    url_pic = "https://api.eyecon-app.com/app/pic"
    params = {
        'cli': phone_number_clean,
        'is_callerid': 'true',
        'size': 'big',
        'type': '0',
        'src': 'MenifaFragment',
        'cancelfresh': '0',
        'cv': 'vc_542_vn_4.0.542_a'
    }

    response_pic = requests.get(url_pic, headers=headers, params=params)
    image_url = response_pic.url if response_pic.status_code == 200 else None

    msg = f"📞 নম্বর: {phone_number}\n🌍 দেশ: {country_name}\n👤 নাম: {name}"

    if image_url:
        await update.message.reply_photo(photo=image_url, caption=msg)
    else:
        await update.message.reply_text(msg)

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
