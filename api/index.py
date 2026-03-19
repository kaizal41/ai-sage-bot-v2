import os
import asyncio
from flask import Flask, request
from groq import Groq
from telegram import Update, Bot, ReplyKeyboardMarkup, KeyboardButton

app = Flask(__name__)

# Config - Environment Variables ထဲမှာ ရှိပြီးသားဖြစ်ရမယ်
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=BOT_TOKEN)

async def handle_logic(update: Update):
    if not update.message:
        return

    chat_id = update.message.chat_id
    user_text = update.message.text

    # /start command အတွက် UI ခလုတ်များပြပေးခြင်း
    if user_text == "/start":
        keyboard = [
            [KeyboardButton("Market Update 📈"), KeyboardButton("Trading Tips 💡")],
            [KeyboardButton("Help ❓")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        welcome_msg = (
            "ဟေ့လူ... နေကောင်းလား! 👋\n\n"
            "ငါက **The Crypto Sage** ပါ။ မင်းရဲ့ Crypto သူငယ်ချင်းပေါ့။\n"
            "သိချင်တာရှိရင် အောက်က ခလုတ်လေးတွေနှိပ် ဒါမှမဟုတ် စာရိုက်ပြီး မေးလို့ရတယ်နော်။"
        )
        await bot.send_message(chat_id=chat_id, text=welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")
        return

    # AI စကားပြောပုံ ညွှန်ကြားချက် (System Prompt)
    system_instruction = (
        "မင်းက 'The Crypto Sage' ဆိုတဲ့ နာမည်နဲ့ လူငယ်တစ်ယောက်လို စကားပြောပေးရမယ့် သူငယ်ချင်းတစ်ယောက်ပါ။ "
        "အရမ်းကြီး ယဉ်ကျေးနေစရာမလိုဘူး၊ ရင်းရင်းနှီးနှီးနဲ့ ပွင့်ပွင့်လင်းလင်း ပြောပါ။ "
        "မြန်မာလိုပြောတဲ့အခါ သဘာဝကျပါစေ။ English စကားလုံးတွေကို ညှပ်သုံးပါ။ "
        "အရေးကြီးတာက Bitcoin, Ethereum, USDT, Entry, Long, Short, Futures, Wallet, RSI, Support, Resistance စတဲ့ "
        "Technical term တွေကို ဗမာစာနဲ့ (ဥပမာ- ဘစ်ကွိုင်) လို့ လုံးဝ မရေးပါနဲ့။ Original English အတိုင်းပဲ ထားပါ။ "
        "အဖြေတွေကိုလည်း ရှည်ရှည်ဝေးဝေးကြီးတွေ မဟုတ်ဘဲ နားလည်လွယ်အောင် Bullet points လေးတွေနဲ့ ဖြေပေးပါ။"
    )

    try:
        # Groq AI ခေါ်ယူခြင်း
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ]
        )
        ai_response = completion.choices[0].message.content
        await bot.send_message(chat_id=chat_id, text=ai_response)
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text="အဆင်မပြေဖြစ်သွားတယ်ဗျာ... ခဏနေမှ ပြန်စမ်းကြည့်နော်။")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        
        # Vercel Runtime အတွက် Async loop ကို ကိုင်တွယ်ခြင်း
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(handle_logic(update))
        loop.close()
        
        return "ok", 200
    return "forbidden", 403

@app.route('/')
def index():
    return "Sage is Live and Friendly!"
