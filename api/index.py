import os
import asyncio
from flask import Flask, request
from groq import Groq
from telegram import Update, Bot

app = Flask(__name__)

# Environment Variables ကနေ ယူမယ်
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=BOT_TOKEN)

async def handle_message(update):
    if update.message and update.message.text:
        chat_id = update.message.chat_id
        user_text = update.message.text
        
        # AI Response ယူမယ်
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "မင်းက 'The Crypto Sage' ဖြစ်တယ်။ မြန်မာလို ရင်းရင်းနှီးနှီး ပြောပါ။"},
                {"role": "user", "content": user_text}
            ]
        )
        ai_response = completion.choices[0].message.content
        await bot.send_message(chat_id=chat_id, text=ai_response)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        # Async function ကို Run တာပါ
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(handle_message(update))
        loop.close()
        return "ok", 200
    return "forbidden", 403

@app.route('/')
def index():
    return "The Crypto Sage is Online!"
