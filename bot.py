import telebot

TOKEN = '8996461719:AAHPTXQs2cs_8PuCxtbBHTpSVBm_zPVTYGk'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 Welcome to Core Dream! Bot is live and running successfully, bhai!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Bhai, tune bola: {message.text}")

print("Core Dream bot is active and listening...")
bot.polling()
