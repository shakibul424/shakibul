import os
import re
import requests
import phonenumbers
from phonenumbers import geocoder
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ENV VAR
E_AUTH_V = os.getenv('E_AUTH_V')
E_AUTH = os.getenv('E_AUTH')
E_AUTH_C = os.getenv('E_AUTH_C')
E_AUTH_K = os.getenv('E_AUTH_K')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Welcome! Send a phone number (with country code). Example: +8801711111111")

def handle_phone(update: Update, context: CallbackContext):
    text = update.message.text.strip()

    # Validate phone number
    try:
        parsed_number = phonenumbers.parse(text, None)
        if not phonenumbers.is_valid_number(parsed_number):
            update.message.reply_text("❌ Invalid number! Use format: +88017...")
            return
    except Exception:
        update.message.reply_text("❌ Invalid number! Use format: +88017...")
        return

    country_name = geocoder.description_for_number(parsed_number, "en")
    phone_clean = re.sub(r'[^\d]', '', text)

    headers_name = {
        "User-Agent": "Mozilla/5.0",
        "accept": "application/json",
        "e-auth-v": E_AUTH_V,
        "e-auth": E_AUTH,
        "e-auth-c": E_AUTH_C,
        "e-auth-k": E_AUTH_K,
        "accept-charset": "UTF-8",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        "Host": "api.eyecon-app.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }

    url_name = f"https://api.eyecon-app.com/app/getnames.jsp?cli={phone_clean}&lang=en&is_callerid=true&is_ic=true&cv=vc_542_vn_4.0.542_a&requestApi=URLconnection&source=MenifaFragment"
    response_name = requests.get(url_name, headers=headers_name)

    if response_name.status_code == 200 and response_name.json():
        data = response_name.json()
        name = data[0].get('name', 'No name found') if data else 'No data found.'
    else:
        name = "No data found."

    # Optional: picture
    url_pic = "https://api.eyecon-app.com/app/pic"
    params = {
        'cli': phone_clean,
        'is_callerid': 'true',
        'size': 'big',
        'type': '0',
        'src': 'MenifaFragment',
        'cancelfresh': '0',
        'cv': 'vc_542_vn_4.0.542_a'
    }
    headers_pic = headers_name
    response_pic = requests.get(url_pic, params=params, headers=headers_pic)

    if response_pic.status_code == 200 and response_pic.history:
        image_url = response_pic.url
        fb_user_id = re.search(r'facebook\.com/(\d+)', response_pic.history[-1].url)
        fb_id = fb_user_id.group(1) if fb_user_id else "Not found"
    else:
        image_url = "Not found"
        fb_id = "Not found"

    msg = f"📱 Phone: {text}\n🌍 Country: {country_name}\n👤 Name: {name}\n🖼️ Image: {image_url}\n🔗 FB ID: {fb_id}"
    update.message.reply_text(msg)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_phone))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
