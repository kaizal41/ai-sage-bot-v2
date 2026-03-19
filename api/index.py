import os
import requests
import telebot
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def get_crypto_price(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        res = requests.get(url).json()
        return res[coin_id]['usd']
    except: return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("BTC Price 💰", "LTC Price 🚀", "Trading Tips 💡")
    bot.send_message(message.chat.id, "ဟေ့လူ... အခု Gemini နဲ့ဆိုတော့ ပိုလန်းသွားပြီ။ ဘာသိချင်လဲ ပြော!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text.lower()
    
    # ဈေးနှုန်းကြည့်တဲ့ Logic
    price_info = ""
    if "btc" in user_text or "bitcoin" in user_text:
        p = get_crypto_price("bitcoin")
        if p: price_info = f"Current Bitcoin Price: ${p:,} USDT."
    elif "ltc" in user_text or "litecoin" in user_text:
        p = get_crypto_price("litecoin")
        if p: price_info = f"Current Litecoin Price: ${p} USDT."

    system_prompt = (
        "မင်းက 'The Crypto Sage' ဆိုတဲ့ မြန်မာလူငယ် တစ်ယောက်ပါ။ "
        "သူငယ်ချင်း အချင်းချင်း ပြောသလိုပဲ အလွတ်သဘော ပြောပေးပါ။ "
        "မြန်မာစကားကို သဘာဝကျကျ သုံးပါ။ Technical term တွေကို English လိုပဲ ထားပါ။ "
        "အခုပေးထားတဲ့ Live price data ကို သုံးပြီး ဖြေပေးပါ။"
    )

    try:
        full_prompt = f"{system_prompt}\n\nContext: {price_info}\nUser: {message.text}"
        response = model.generate_content(full_prompt)
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        bot.send_message(message.chat.id, "အဆင်မပြေဖြစ်သွားတယ်... ခဏနေမှ ပြန်ပြောနော်။")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return "ok", 200
