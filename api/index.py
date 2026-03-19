import os
import requests
from flask import Flask, request
from groq import Groq
import telebot

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Live Price ဆွဲတဲ့ Function
def get_crypto_price(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url).json()
        return response[coin_id]['usd']
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("BTC Price 💰", "LTC Price 🚀", "Trading Tips 💡")
    bot.send_message(message.chat.id, "ဈေးနှုန်းတွေ သိချင်ရင် ခလုတ်နှိပ်လိုက်ပါ။ Live ဈေးပြောပြမယ်!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text.lower()
    chat_id = message.chat.id
    
    # ဈေးနှုန်းမေးရင် Live data အရင်ယူမယ်
    if "btc" in user_text or "bitcoin" in user_text:
        price = get_crypto_price("bitcoin")
        info = f"အခု Bitcoin (BTC) ဈေးက ${price:,} USDT ရှိတယ်ဘရို။" if price else ""
    elif "ltc" in user_text or "litecoin" in user_text:
        price = get_crypto_price("litecoin")
        info = f"အခု Litecoin (LTC) ဈေးက ${price} USDT ရှိတယ်ဘရို။" if price else ""
    else:
        info = ""

    try:
        # AI ကို Live price information ပါ ထည့်ပေးလိုက်မယ်
        prompt = f"User context: {info}\nUser question: {user_text}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are 'The Crypto Sage', a chill Burmese friend. If the user asks for price, use the provided live price in your answer. Keep terms like Bitcoin, Entry, Long in English."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_response = completion.choices[0].message.content
        bot.send_message(chat_id, ai_response)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "ok", 200
