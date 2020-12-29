import telebot

from db import db
from settings_local import NETWORK_SETTINGS, DECIMALS
from web3 import Web3, HTTPProvider
w3 = Web3(HTTPProvider(NETWORK_SETTINGS['DUCX']['endpoint']))

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
    ducx_balance = w3.eth.getBalance(NETWORK_SETTINGS['DUCX']['address'])
    #ducx_balance = ducx_balance/DECIMALS
    bot.reply_to(message, f'{ducx_balance/DECIMALS} DUCX')


@bot.message_handler(commands=['address'])
def address_handle(message):
    ducx_address = NETWORK_SETTINGS['DUCX']['address']
    bot.reply_to(message, f'You can send DUCX to this address {ducx_address}')


@bot.message_handler(commands=['ping'])
def stop_handle(message):
    bot.reply_to(message, 'pong')
