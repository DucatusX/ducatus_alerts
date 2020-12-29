import time
import threading

from db import db
from poller import bot
from settings_local import BALANCE_CHECKER_TIMEOUT, NETWORK_SETTINGS, DECIMALS

from web3 import Web3, HTTPProvider
w3 = Web3(HTTPProvider(NETWORK_SETTINGS['DUCX']['endpoint']))


class Alert ():
    warning_levels = [10_000 * DECIMALS, 50_000 * DECIMALS, 100_000 * DECIMALS]
    current_level = 3

    def check_balance(self, ducx_balance):
        if ducx_balance > self.warning_levels[-1]:
            if self.current_level != 3:
                self.current_level = 3
                self._send_alert(duc_balance, is_ok=True)
            return

        for i, warning_level in enumerate(self.warning_levels):
            if ducx_balance < warning_level and self.current_level > i:
                self.current_level = i
                self._send_alert(ducx_balance, warning_level=warning_level)
                return

    def _send_alert(self, ducxx_balance, warning_level=None, is_ok=False):
        for chat in db.chats.find({}, {'id': 1}):
            chat_id = chat['id']
            if is_ok:
                bot.send_message(chat_id, f'DUCX balance is replenished: {ducx_balance/DECIMALS} DUC')
            else:
                bot.send_message(chat_id, f'WARNING: DUCX balance is less than {warning_level/DECIMALS}: {ducx_balance/DECIMALS} DUC')


def start_polling():
    while True:
        bot.polling()


if __name__ == '__main__':
    poller = threading.Thread(target=start_polling)
    poller.start()

    alert = Alert()
    while True:
        ducx_balance = w3.eth.getBalance(NETWORK_SETTINGS['DUCX']['address'])
        alert.check_balance(ducx_balance)
        time.sleep(BALANCE_CHECKER_TIMEOUT)
