import os
import telebot

# Yahan apna Telegram Bot Token daalna hai
TOKEN = '8897981080:AAGuvfDYZhRBqeQ089uJsXJeFy-suQQKcuw'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def action_start(message):
    bot.reply_to(message, "🔥 Welcome to Core Dream! Bot is successfully online and ready for action, bhai!")

@bot.message_handler(func=lambda message: True)
def action_echo(message):
    bot.reply_to(message, f"Bhai, tune bola: {message.text}")

print("Bot is running...")
bot.polling()
