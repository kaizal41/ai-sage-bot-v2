import os
from flask import Flask, request
from groq import Groq
import telebot # python-telegram-bot အစား ပိုပေါ့ပါးတဲ့ telebot ပုံစံသုံးပါမယ်

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "ok", 200
    return "forbidden", 403

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Market Update 📈", "Trading Tips 💡")
    bot.send_message(message.chat.id, "ဟေ့လူ... နေကောင်းလား! ငါက The Crypto Sage ပါ။ ဘာမေးချင်လဲ?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id
    
    try:
        # Groq AI ခေါ်မယ် (Sync ပုံစံနဲ့ပဲ)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "မင်းက 'The Crypto Sage' သူငယ်ချင်းတစ်ယောက်ပါ။ မြန်မာလိုပြောပါ။ English terms (Bitcoin, USDT, Long, Short, Entry) တွေကို ဗမာလိုမပေါင်းပါနဲ့။"},
                {"role": "user", "content": user_text}
            ]
        )
        ai_response = completion.choices[0].message.content
        bot.send_message(chat_id, ai_response)
    except Exception as e:
        bot.send_message(chat_id, f"Error တက်သွားတယ်ဘရို: {str(e)}")

@app.route('/')
def index():
    return "Sage is Ready and Sync"
