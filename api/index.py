import os
import requests
import telebot
from flask import Flask, request

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def call_gemini_api(prompt):
    # Endpoint ကို v1 ပြောင်းပြီး model name ကို gemini-1.5-flash လို့ အသေရေးထားပါတယ်
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
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
            # Response ကနေ စာသားကို သေချာထုတ်ယူခြင်း
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Gemini Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Request Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "ဟေ့လူ... Crypto Sage အဆင်သင့်ပဲ! ဘာမေးချင်လဲ?")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id
    
    # System Instruction ကို ဒီမှာပဲ တည့်ထည့်လိုက်မယ်
    system_prompt = "You are 'The Crypto Sage', a chill Burmese friend. Talk naturally in Burmese language."
    full_prompt = f"{system_prompt}\nUser: {user_text}"
    
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
    return "Sage is Live"
