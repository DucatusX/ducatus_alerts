import os

from src.checker_service import BalanceCheckerService
from src.settings import config

if __name__ == "__main__":
    for network_name, network_config in config.NETWORKS.items():
        checker = BalanceCheckerService(network_name, network_config)
        checker.start()
