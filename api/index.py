import os
import requests
import telebot
from flask import Flask, request

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def get_crypto_price(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        res = requests.get(url, timeout=5).json()
        return res[coin_id]['usd']
    except: return None

def call_gemini_api(prompt):
    # Endpoint URL ကို v1 သုံးပြီး model name ကို prefix ပါအောင် ထည့်ထားပါတယ်
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # Error တက်ရင် ဘာကြောင့်လဲဆိုတာ အသေးစိတ် သိရအောင်
            return f"Gemini Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "ဟေ့လူ... Crypto Sage ပြန်လာပြီ! ဘာမေးချင်လဲ?")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id
    
    price_info = ""
    if "btc" in user_text.lower():
        p = get_crypto_price("bitcoin")
        if p: price_info = f"Current BTC Price: ${p:,} USDT."

    system_prompt = "You are 'The Crypto Sage', a chill Burmese friend. Talk naturally in Burmese."
    full_prompt = f"{system_prompt}\nContext: {price_info}\nUser: {user_text}"
    
    ai_response = call_gemini_api(full_prompt)
    bot.send_message(chat_id, ai_response)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "ok", 200

@app.route('/')
def index():
    return "Bot is Live"
