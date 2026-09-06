import os
from flask import Flask, render_template_string
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = '8996461719:AAFMAw1xfmMFdu-uFmVA4fznrL8zUu_teSg'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Yahan tera Web App ka link aayega (Render ka URL ya GitHub Pages ka link)
WEB_APP_URL = "https://corebot-xyz.onrender.com"  # Isko baad me apne Render URL se update kar denge

@app.route('/')
index():
    # Ye tera GambleFi Mini App ka front-end (HTML/CSS) hai
    return render_template_string('''
    <html>
        <head>
            <title>Core Dream GambleFi</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { background-color: #0f172a; color: white; font-family: Arial, sans-serif; text-align: center; padding: 20px; }
                h1 { color: #facc15; }
                .card { background: #1e293b; padding: 20px; border-radius: 15px; margin-top: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
                button { background: #22c55e; color: white; border: none; padding: 12px 24px; font-size: 18px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 15px; }
                button:active { background: #16a34a; }
            </style>
        </head>
        <body>
            <h1>🔥 Core Dream 🔥</h1>
            <p>Welcome to the ultimate GambleFi experience, bhai!</p>
            <div class="card">
                <h3>Your Balance: 🪙 1,000 CORE</h3>
                <p>Tap below to roll and win big!</p>
                <button onclick="alert('Spinning feature coming soon, bhai!')">SPIN & WIN</button>
            </div>
        </body>
    </html>
    ''')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    # WebApp button jo direct game khol dega
    web_app = WebAppInfo(url=WEB_APP_URL)
    markup.add(InlineKeyboardButton("🚀 Open Core Dream Game", web_app=web_app))
    
    bot.reply_to(message, "🔥 Welcome to Core Dream! Click the button below to launch the game app:", reply_markup=markup)

# Render par Flask server ko chalane ke liye
if __name__ == "__main__":
    # Bot ko background me chalane ke liye threading bhi use kar sakte hain, 
    # filhal hum Flask app run karenge jo Render web service ke liye zaroori hai.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
