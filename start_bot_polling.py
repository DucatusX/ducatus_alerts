import os

from src.bot_base import Bot
from src.settings import config

if __name__ == "__main__":
    for network_name, network_config in config.NETWORKS.items():
        print(f"Launch bot on {network_name}")
        bot = Bot(network_name, network_config)
        bot.start()
