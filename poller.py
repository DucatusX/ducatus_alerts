import telebot

from db import db
from settings_local import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_handler(message):
    data = {'id': message.chat.id}
    db.chats.update(data, data, upsert=True)
    bot.reply_to(message, 'hello')


@bot.message_handler(commands=['stop'])
def stop_handle(message):
    db.chats.remove({'id': message.chat.id})
    bot.reply_to(message, 'buy')


@bot.message_handler(commands=['ping'])
def stop_handle(message):
    bot.reply_to(message, 'pong')
