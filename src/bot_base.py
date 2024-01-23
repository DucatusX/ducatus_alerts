import os
import logging
import threading
from typing import Any, Optional

import redis
import telebot
# from django.apps import apps
from pymongo import MongoClient

from src.utils.redis_utils import RedisClient
from src.settings import config, NetworkSettings
from src.currency_service import CurrencyService


class Bot(threading.Thread):
    def __init__(self, network_name: str, network_config: NetworkSettings):
        super().__init__()
        self.config = network_config
        self.name = network_name
        self.currency_service = CurrencyService(self.name, self.config)
        self.logger = self.currency_service.logger

        db_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        db_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        self.db = getattr(MongoClient(f'mongodb://{db_user}:{db_password}@db:27017/'), f'{self.name}_alerts')
        self.bot = telebot.TeleBot(network_config.bot_token)

        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            self.add_chat(message.chat.id)
            self.bot.reply_to(message, 'Hello!')

        @self.bot.message_handler(commands=['stop'])
        def stop_handle(message):
            self.remove_chat(user_id=message.chat.id)
            self.bot.reply_to(message, 'Bye!')

        @self.bot.message_handler(commands=['balance'])
        def balance_handle(message):
            balance = self.currency_service.get_saved_balance()
            self.bot.reply_to(message, f'{balance} {self.name}')

        @self.bot.message_handler(commands=['address'])
        def address_handle(message):
            address = self.currency_service.get_address()
            self.bot.reply_to(message, address)

        @self.bot.message_handler(commands=['ping'])
        def ping_handle(message):
            self.bot.reply_to(message, 'Pong')

    def get_all_chats(self):
        redis_ = RedisClient()
        redis_keys = redis_.connection.keys(f'user_{self.name}_*')
        chats = []
        for rk in redis_keys:
            chat_id = rk.split('_')[-1]
            chats.append(chat_id)
        return chats

    def remove_chat(self, user_id):
        try:
            redis_ = RedisClient()
            redis_.connection.delete(f"user_{self.name}_{user_id}")
        except Exception as e:
            pass

    def add_chat(self, user_id):
        redis_ = RedisClient()
        redis_.connection.set(f"user_{self.name}_{user_id}", '1')


    def send_alert(self, balance: Any, warning_level: Optional[int] = None, is_ok=True):
        self.logger.warning("Trying to send alerts")
        chats = self.get_all_chats()
        for chat in chats:
        # for chat in self.db.chats.find({}, {'id': 1}):
            chat_id = chat
            message = 'WARNING! {currency} balance is less than {level}: {balance} {currency}'.format(
                currency=self.name,
                balance=balance,
                level=config.WARNING_LEVELS[warning_level]
            )
            if is_ok:
                message = f'{self.name} balance replenished: {balance} {self.name}'
            try:
                self.bot.send_message(chat_id, message)
            except telebot.apihelper.ApiTelegramException as exc:
                if "bot was blocked by the user" in str(exc):
                    self.remove_chat(chat_id)
                    self.logger.info(f"Removed user {chat_id} because they blocked bot")
            except Exception as e:
                self.logger.exception(e, exc_info=True)

    def run(self):
        self.bot.infinity_polling()

