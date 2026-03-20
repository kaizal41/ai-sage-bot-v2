import os
import requests
import telebot
from flask import Flask, request

app = Flask(__name__)

# Config - Vercel မှာ BOT_TOKEN နဲ့ DEEPSEEK_API_KEY ကို ထည့်ပေးပါ
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

def call_deepseek_api(prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are 'The Crypto Sage', a chill Burmese friend. Talk naturally in Burmese."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"DeepSeek Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "ဟေ့လူ... DeepSeek နဲ့ ပြန်လာပြီ! ဘာမေးချင်လဲ?")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    ai_response = call_deepseek_api(message.text)
    bot.send_message(message.chat.id, ai_response)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "ok", 200

@app.route('/')
def index():
    return "DeepSeek Bot is Live"
