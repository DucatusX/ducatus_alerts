import telebot

from db import db
from litecoin_rpc import DucatuscoreInterface
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


@bot.message_handler(commands=['balance'])
def balance_handle(message):
    interface = DucatuscoreInterface()
    duc_balance = interface.rpc.getbalance('')
    bot.reply_to(message, f'{duc_balance} DUC')


@bot.message_handler(commands=['address'])
def address_handle(message):
    interface = DucatuscoreInterface()
    duc_address = interface.rpc.getaccountaddress('')
    bot.reply_to(message, f'You can send DUC to this address {duc_address}')


@bot.message_handler(commands=['ping'])
def stop_handle(message):
    bot.reply_to(message, 'pong')
