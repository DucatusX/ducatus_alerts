import os
import logging.handlers
import time
import telebot
import threading

import requests
from web3 import Web3, HTTPProvider
from pymongo import MongoClient

from settings import settings, NetworkSettings
from litecoin_rpc import DucatuscoreInterface


class AlertsBot(threading.Thread):
    def __init__(self, currency, bot_token):
        super().__init__()
        self.current_warning_level = 4
        self.currency: NetworkSettings = currency
        self.logger = self.set_logger()
        db_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        db_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        self.db = getattr(MongoClient(f'mongodb://{db_user}:{db_password}@db:27017/'), f'{currency.name}_alerts')
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
            getattr(self, f'update_{self.currency.name}_balance')()
            self.bot.reply_to(message, f'{self.balance} {self.currency.name}')

        @self.bot.message_handler(commands=['address'])
        def address_handle(message):
            address = getattr(self, f'{self.currency.name}_address')
            self.bot.reply_to(message, address)

        @self.bot.message_handler(commands=['ping'])
        def stop_handle(message):
            self.bot.reply_to(message, 'Pong')

    def set_logger(self):
        logger = logging.getLogger(
            '{currency}_logger'.format(currency=self.currency.name)
        )
        custom_formatter = logging.Formatter(
            fmt='%(levelname)-10s | %(asctime)s | %(name)-18s | %(message)s'
        )
        logfile_name = 'logs/{currency}_alerts.log'.format(currency=self.currency.name)
        custom_handler = logging.handlers.TimedRotatingFileHandler(
            filename=logfile_name,
            when='D',
            interval=3)
        custom_handler.setFormatter(custom_formatter)
        logger.addHandler(custom_handler)
        logger.level = logging.INFO
        return logger

    def start_polling(self):
        while True:
            try:
                self.bot.infinity_polling()
            except Exception as exception:
                self.logger.exception(exception, exc_info=True)

    def send_alert(self, is_ok=False):
        self.logger.warning("Trying to send alerts")
        for chat in self.db.chats.find({}, {'id': 1}):
            chat_id = chat['id']
            message = 'WARNING! {currency} balance is less than {level}: {balance} {currency}'.format(
                currency=self.currency.name,
                balance=self.balance,
                level=settings.WARNING_LEVELS[self.current_warning_level]
            )
            if is_ok:
                message = f'{self.currency.name} balance replenished: {self.balance} {self.currency.name}'
            try:
                self.bot.send_message(chat_id, message)
            except telebot.apihelper.ApiTelegramException as exc:
                if "bot was blocked by the user" in str(exc):
                    self.db.chats.remove({'id': chat_id})
                    self.logger.info(f"Removed user {chat_id} because they blocked bot")
            except (
                    ConnectionAbortedError,
                    ConnectionResetError,
                    ConnectionRefusedError,
                    ConnectionError,
                    requests.exceptions.RequestException,
            ) as exception:
                self.logger.exception(exception, exc_info=True)


    @property
    def DUC_address(self):
        return DucatuscoreInterface().rpc.getaccountaddress('')

    @property
    def DUCX_address(self):
        return self.DUCX_settings.address
        
    
    @property
    def DUCX_settings(self):
        return [network for network in settings.NETWORKS if network.name == 'DUCX'][0]
    
    @property
    def DUC_settings(self):
        return [network for network in settings.NETWORKS if network.name == 'DUC'][0]

    def update_DUC_balance(self):
        self.balance = DucatuscoreInterface().rpc.getbalance('')

    def update_DUCX_balance(self):
        w3 = Web3(HTTPProvider(self.DUCX_settings.endpoint))
        
        raw_balance = w3.eth.get_balance(w3.to_checksum_address(self.DUCX_address))
        self.balance = raw_balance / 10 ** self.DUCX_settings.decimals 

    def check_balance(self):
        if self.balance > settings.WARNING_LEVELS[-1]:
            levels_count = len(settings.WARNING_LEVELS)
            if self.current_warning_level != levels_count:
                self.current_warning_level = levels_count
                try:
                    self.send_alert(is_ok=True)
                except Exception as e:
                    self.logger.warning(e)
                    
            return

        self.logger.warning(
            'WARNING level reached! Current balance is {balance}'.format(balance=self.balance)
        )

        for i, warning_level in enumerate(settings.WARNING_LEVELS):
            if self.balance < warning_level and self.current_warning_level > i:
                self.current_warning_level = i
                self.send_alert()
                return

    def run(self):
        threading.Thread(target=self.start_polling).start()
        while True:
            getattr(self, f'update_{self.currency.name}_balance')()
            self.logger.info(f'{self.currency.name} balance updated: {self.balance}')
            self.check_balance()
            time.sleep(settings.BALANCE_CHECKER_TIMEOUT)


if __name__ == '__main__':
    currencies = settings.NETWORKS
    for currency in currencies:
        AlertsBot(currency, currency.bot_token).start()
        print(f'{currency.name} alerts bot is on!', flush=True)
