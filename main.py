import time
import telebot
import threading
import traceback
import sys
from web3 import Web3, HTTPProvider
from pymongo import MongoClient
from settings import BALANCE_CHECKER_TIMEOUT, NETWORKS, WARNING_LEVELS
from litecoin_rpc import DucatuscoreInterface


class AlertsBot(threading.Thread):
    def __init__(self, currency, bot_token):
        super().__init__()
        self.current_warning_level = 3
        self.currency = currency
        self.db = getattr(MongoClient('mongodb://localhost:27017/'), f'{currency}_alerts')
        self.bot = telebot.TeleBot(bot_token)
        self.balance = 0

        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            data = {'id': message.chat.id}
            self.db.chats.update(data, data, upsert=True)
            self.bot.reply_to(message, 'Hello!')

        @self.bot.message_handler(commands=['stop'])
        def stop_handle(message):
            self.db.chats.remove({'id': message.chat.id})
            self.bot.reply_to(message, 'Bye!')

        @self.bot.message_handler(commands=['balance'])
        def balance_handle(message):
            getattr(self, f'update_{self.currency}_balance')()
            self.bot.reply_to(message, f'{self.balance} {self.currency}')

        @self.bot.message_handler(commands=['address'])
        def address_handle(message):
            address = getattr(self, f'{self.currency}_address')
            self.bot.reply_to(message, address)

        @self.bot.message_handler(commands=['ping'])
        def stop_handle(message):
            self.bot.reply_to(message, 'Pong')

    def start_polling(self):
        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception:
                print('\n'.join(traceback.format_exception(*sys.exc_info())), flush=True)
                time.sleep(15)

    def send_alert(self, is_ok=False):
        for chat in self.db.chats.find({}, {'id': 1}):
            chat_id = chat['id']
            if is_ok:
                self.bot.send_message(chat_id, f'{self.currency} balance replenished: {self.balance} {self.currency}')
            else:
                self.bot.send_message(chat_id, f'WARNING! {self.currency} balance is less than '
                                               f'{WARNING_LEVELS[self.current_warning_level]}: '
                                               f'{self.balance} {self.currency}')

    @property
    def DUC_address(self):
        return DucatuscoreInterface().rpc.getaccountaddress('')

    @property
    def DUCX_address(self):
        return NETWORKS[self.currency]['address']

    def update_DUC_balance(self):
        self.balance = DucatuscoreInterface().rpc.getbalance('')

    def update_DUCX_balance(self):
        w3 = Web3(HTTPProvider(NETWORKS[self.currency]['endpoint']))
        address = getattr(self, f'{self.currency}_address')
        raw_balance = w3.eth.getBalance(w3.toChecksumAddress(address))
        self.balance = raw_balance / NETWORKS[self.currency]['decimals']

    def check_balance(self):
        if self.balance > WARNING_LEVELS[-1]:
            levels_count = len(WARNING_LEVELS)
            if self.current_warning_level != levels_count:
                self.current_warning_level = levels_count
                self.send_alert(is_ok=True)
            return

        for i, warning_level in enumerate(WARNING_LEVELS):
            if self.balance < warning_level and self.current_warning_level > i:
                self.current_warning_level = i
                self.send_alert()
                return

    def run(self):
        threading.Thread(target=self.start_polling).start()
        while True:
            getattr(self, f'update_{self.currency}_balance')()
            print(f'{self.currency} balance updated: {self.balance}', flush=True)
            self.check_balance()
            time.sleep(BALANCE_CHECKER_TIMEOUT)


if __name__ == '__main__':
    for currency, info in NETWORKS.items():
        AlertsBot(currency, info['bot_token']).start()
        print(f'{currency} alerts bot is on!', flush=True)
