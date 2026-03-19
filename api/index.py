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
    # Endpoint ကို v1beta ပြန်ပြောင်းပြီး model name ကို prefix အပြည့်အစုံနဲ့ သုံးထားပါတယ်
    # ဒါက 404 error ကို အထိရောက်ဆုံး ဖြေရှင်းနိုင်တဲ့ နည်းလမ်းပါ
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Gemini Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Request Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("BTC Price 💰", "LTC Price 🚀", "Trading Tips 💡")
    bot.send_message(message.chat.id, "ဟေ့လူ... အခုတစ်ခါတော့ တကယ်လာပြီ! ဘာမေးချင်လဲ?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id
    
    # Context gathering
    price_info = ""
    lower_text = user_text.lower()
    if "btc" in lower_text or "bitcoin" in lower_text:
        p = get_crypto_price("bitcoin")
        if p: price_info = f"Current Bitcoin Price: ${p:,} USDT."
    elif "ltc" in lower_text or "litecoin" in lower_text:
        p = get_crypto_price("litecoin")
        if p: price_info = f"Current Litecoin Price: ${p} USDT."

    system_prompt = (
        "You are 'The Crypto Sage', a chill Burmese friend who is an expert in crypto. "
        "Talk naturally in Burmese. Use English for technical terms (Long, Short, Entry). "
        "Answer concisely based on the context."
    )

    full_prompt = f"{system_prompt}\n\nContext: {price_info}\nUser: {user_text}"
    ai_response = call_gemini_api(full_prompt)
    bot.send_message(chat_id, ai_response)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "forbidden", 403

@app.route('/')
def index():
    return "Sage is Live and Fixed"
