import os
import asyncio
from flask import Flask, request
from groq import Groq
from telegram import Update, Bot, ReplyKeyboardMarkup, KeyboardButton

app = Flask(__name__)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=BOT_TOKEN)

async def handle_logic(update: Update):
    if not update.message or not update.message.text:
        return

    chat_id = update.message.chat_id
    user_text = update.message.text

    if user_text == "/start":
        keyboard = [[KeyboardButton("Market Update 📈"), KeyboardButton("Trading Tips 💡")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await bot.send_message(chat_id=chat_id, text="ဟေ့လူ... နေကောင်းလား! ငါ့ကို ဘာမေးချင်လဲ?", reply_markup=reply_markup)
        return

    try:
        # AI Logic
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "မင်းက 'The Crypto Sage' သူငယ်ချင်းတစ်ယောက်ပါ။ မြန်မာလိုပြောပါ။ English term တွေကို ဗမာလိုမပေါင်းပါနဲ့။"},
                {"role": "user", "content": user_text}
            ]
        )
        ai_response = completion.choices[0].message.content
        await bot.send_message(chat_id=chat_id, text=ai_response)
    except Exception as e:
        # Error က ဘာလဲဆိုတာ Bot က ပြောပြလိမ့်မယ်
        await bot.send_message(chat_id=chat_id, text=f"Error တက်သွားတယ်ဘရို: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        
        # New Loop for Each Request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(handle_logic(update))
        finally:
            loop.close()
        return "ok", 200
    return "forbidden", 403

@app.route('/')
def index():
    return "Sage is Ready"
