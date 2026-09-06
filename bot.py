import telebot

TOKEN = '8996461719:AAEz83971eXwQ68wYjH-8T3x3r_n4u0e-8A' # Naya API token yahan set hai
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 Welcome to Core Dream! Bot is live and running 24/7, bhai!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Bhai, tune bola: {message.text}")

print("Core Dream bot is active...")
bot.polling()
