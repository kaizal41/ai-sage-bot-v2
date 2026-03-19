import os
import requests
import telebot
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Setup - API Key ရှိမှ လုပ်မယ်
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def get_crypto_price(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        res = requests.get(url, timeout=5).json()
        return res[coin_id]['usd']
    except: return None

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "forbidden", 403

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("BTC Price 💰", "LTC Price 🚀", "Trading Tips 💡")
    bot.send_message(message.chat.id, "ဟေ့လူ... နေကောင်းလား! Gemini Sage ပြန်လာပြီ။ ဘာမေးချင်လဲ?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id
    
    if not GEMINI_API_KEY:
        bot.send_message(chat_id, "Error: Vercel Settings မှာ GEMINI_API_KEY ထည့်ဖို့ မမေ့နဲ့ဦးဘရို။")
        return

    price_info = ""
    lower_text = user_text.lower()
    if "btc" in lower_text or "bitcoin" in lower_text:
        p = get_crypto_price("bitcoin")
        if p: price_info = f"Current Bitcoin Price: ${p:,} USDT."
    elif "ltc" in lower_text or "litecoin" in lower_text:
        p = get_crypto_price("litecoin")
        if p: price_info = f"Current Litecoin Price: ${p} USDT."

    system_prompt = (
        "You are 'The Crypto Sage', a chill Burmese friend. "
        "Talk naturally in Burmese. Keep terms like Bitcoin, USDT, Entry in English. "
        "Use the provided context to answer questions."
    )

    try:
        response = model.generate_content(f"{system_prompt}\n\nContext: {price_info}\nUser: {user_text}")
        bot.send_message(chat_id, response.text)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {str(e)}")

@app.route('/')
def index():
    return "Gemini is Online"
