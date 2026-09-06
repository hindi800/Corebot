import telebot

TOKEN = '8897981080:AAGuvfDYZhRBqeQ089uJsXJeFy-suQQKcuw'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 Welcome to Core Dream! Bot is successfully online and ready for action, bhai!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Bhai, tune bola: {message.text}")

print("Bot is running...")
bot.polling()
