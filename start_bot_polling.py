import os

from src.bot_base import Bot
from src.settings import config

if __name__ == "__main__":
    for network_name, network_config in config.NETWORKS.items():
        bot = Bot(network_name, network_config)
        bot.start()
