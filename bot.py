import telebot
import time

TOKEN = '8996461719:AAFMAw1xfmMFdu-uFmVA4fznrL8zUu_teSg'

# Purane connection clash ko hatane ke liye chota sa pause
time.sleep(2)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 Welcome to Core Dream! Bot is fully live and online, bhai!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Bhai, tune bola: {message.text}")

print("Core Dream bot is starting up cleanly...")
bot.infinity_polling(none_stop=True)
