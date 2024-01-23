from src.utils.litecoin_rpc import DucatuscoreInterface
from web3 import Web3, HTTPProvider
import logging
import logging.handlers
from src.settings import config, NetworkSettings
from src.utils.redis_utils import RedisClient

class CurrencyService:

    def __init__(self, network_name: str, network_config: NetworkSettings):
        self.name = network_name
        self.config = network_config
        self.logger = self.get_logger()

    @property
    def get_DUC_address(self):
        return DucatuscoreInterface().rpc.getaccountaddress('')

    @property
    def get_DUCX_address(self):
        return self.config.address

    def get_address(self):
        return getattr(self, f"get_{self.name}_address")

    def get_logger(self):
        logger = logging.getLogger(f'{self.name}_logger')
        custom_formatter = logging.Formatter(
            fmt='%(levelname)-10s | %(asctime)s | %(name)-18s | %(message)s'
        )
        logfile_name = f'logs/{self.name}_alerts.log'
        custom_handler = logging.handlers.TimedRotatingFileHandler(
            filename=logfile_name,
            when='D',
            interval=3)
        custom_handler.setFormatter(custom_formatter)
        logger.addHandler(custom_handler)
        logger.level = logging.INFO
        return logger

    def update_balance(self):
        balance = getattr(self, f"fetch_balance_{self.name}")()
        redis_ = RedisClient()
        redis_.connection.set(f"balance_{self.name}", balance)

    def fetch_balance_DUC(self):
        balance = str(DucatuscoreInterface().rpc.getbalance(''))
        return balance

    def fetch_balance_DUCX(self):
        w3 = Web3(HTTPProvider(self.config.endpoint))

        raw_balance = w3.eth.get_balance(w3.to_checksum_address(self.get_address()))
        balance = str(raw_balance / 10 ** self.config.decimals)
        return balance

    def get_saved_balance(self):
        redis_ = RedisClient()
        return redis_.connection.get(f"balance_{self.name}")

    def set_current_warning_level(self, warning_level: int):
        redis_ = RedisClient()
        redis_.connection.set(f"warning_level_{self.name}", str(warning_level))
        return warning_level

    def get_current_warning_level(self):
        redis_ = RedisClient()
        level = redis_.connection.set(f"warning_level_{self.name}")
        return int(level)


