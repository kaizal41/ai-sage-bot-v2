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
    if request.method == "POST":
        try:
            data = request.get_json(force=True)
            update = Update.de_json(data, bot)
            
            if update.message and update.message.text:
                chat_id = update.message.chat_id
                user_text = update.message.text
                
                # Groq AI ကို ခေါ်မယ်
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "မင်းက 'The Crypto Sage' ဖြစ်တယ်။ မြန်မာလို ရင်းရင်းနှီးနှီး ပြောပါ။"},
                        {"role": "user", "content": user_text}
                    ]
                )
                ai_response = completion.choices[0].message.content
                
                # စာပြန်ပို့မယ်
                await bot.send_message(chat_id=chat_id, text=ai_response)
                
            return "ok", 200
        except Exception as e:
            print(f"Error: {e}")
            return "error", 500
    return "forbidden", 403

@app.route('/')
def index():
    return "Sage is Online"
