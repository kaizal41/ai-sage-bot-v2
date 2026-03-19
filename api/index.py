import os
from flask import Flask, request
from groq import Groq
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        
        # AI Logic
        user_text = update.message.text
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "မင်းက 'The Crypto Sage' ဖြစ်တယ်။ မြန်မာလို ရင်းရင်းနှီးနှီး ပြောပါ။"},
                {"role": "user", "content": user_text}
            ]
        )
        await bot.send_message(chat_id=update.message.chat_id, text=completion.choices[0].message.content)
        return "ok"

@app.route('/')
def index():
    return "Sage is Online"

# Vercel အတွက် အရေးကြီးတယ်
def handler(request):
    return app(request)
