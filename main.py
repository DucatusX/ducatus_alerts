import time
import threading

from db import db
from poller import bot
from litecoin_rpc import DucatuscoreInterface
from settings_local import BALANCE_CHACKER_TIMEOUT



class Alert:
    warning_levels = [10_000, 50_000, 100_000]
    current_level = 3

    def check_balance(self, duc_balance):
        if duc_balance > self.warning_levels[-1]:
            if self.current_level != 3:
                self.current_level = 3
                self._send_alert(duc_balance, is_ok=True)
            return

        for i, warning_level in enumerate(self.warning_levels):
            if duc_balance < warning_level and self.current_level > i:
                self.current_level = i
                self._send_alert(duc_balance, warning_level=warning_level)
                return

    def _send_alert(self, duc_balance, warning_level=None, is_ok=False):
        for chat in db.chats.find({}, {'id': 1}):
            chat_id = chat['id']
            if is_ok:
                bot.send_message(chat_id, f'DUC balance is replenished: {duc_balance} DUC')
            else:
                bot.send_message(chat_id, f'WARNING: DUC balance is less than {warning_level}: {duc_balance} DUC')


def start_polling():
    while True:
        bot.polling()


if __name__ == '__main__':
    poller = threading.Thread(target=start_polling)
    poller.start()

    alert = Alert()
    while True:
        interface = DucatuscoreInterface()
        duc_balance = interface.rpc.getbalance('')

        alert.check_balance(duc_balance)

        time.sleep(BALANCE_CHACKER_TIMEOUT)
