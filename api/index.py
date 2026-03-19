import os
import asyncio
from flask import Flask, request
from groq import Groq
from telegram import Update, Bot

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        if update.message and update.message.text:
            chat_id = update.message.chat_id
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "မင်းက 'The Crypto Sage' ဖြစ်တယ်။ မြန်မာလို ရင်းရင်းနှီးနှီး ပြောပါ။"},
                    {"role": "user", "content": update.message.text}
                ]
            )
            await bot.send_message(chat_id=chat_id, text=completion.choices[0].message.content)
        return "ok", 200
    except Exception as e:
        print(e)
        return "error", 500

@app.route('/')
def index():
    return "Sage is Online"

# Vercel အတွက် အရေးကြီးဆုံးအပိုင်း
def handler(request):
    return app(request)
