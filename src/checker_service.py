import threading
import time

from src.settings import config, NetworkSettings
from src.currency_service import CurrencyService
from src.bot_base import Bot
class BalanceCheckerService(threading.Thread):

    def __init__(self, network_name: str, network_config: NetworkSettings):
        super().__init__()
        self.name = network_name
        self.config = network_config
        self.service = CurrencyService(network_name=self.name, network_config=self.config)
        self.bot = Bot(self.name, self.config)
        self.logger = self.service.logger

    def check_balance(self):
        balance = self.service.get_saved_balance()
        if int(balance) > config.WARNING_LEVELS[-1]:
            levels_count = len(config.WARNING_LEVELS)
            if self.service.get_current_warning_level() != levels_count:
                warning_level = levels_count
                self.service.set_current_warning_level(warning_level)
                try:
                    self.bot.send_alert(balance, warning_level, is_ok=True)
                except Exception as e:
                    self.logger.warning(e)

            return

        self.logger.warning(f'WARNING level reached! Current balance is {balance}')

        for i, warning_level in enumerate(config.WARNING_LEVELS):
            if (
                    self.service.get_saved_balance() < warning_level
                    and self.service.get_current_warning_level() > i
            ):
                self.service.set_current_warning_level(i)
                self.bot.send_alert(balance)
                return


    def run(self) -> None:
        while True:
            self.service.update_balance()
            self.check_balance()
            time.sleep(config.BALANCE_CHECKER_TIMEOUT)

