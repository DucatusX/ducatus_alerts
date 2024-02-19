import logging
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from http.client import RemoteDisconnected
from socket import timeout

from src.settings import config, NetworkSettings

class DucatuscoreInterfaceException(Exception):
    pass

def retry_on_http_disconnection(req):
    def wrapper(*args, **kwargs):
        for attempt in range(10):
            logging.info(f"attempt:{attempt}")
            try:
                return req(*args, **kwargs)
            except RemoteDisconnected as e:
                logging.warning(e)
                rpc_response = False
            except (timeout, TimeoutError) as e:
                logging.warning(e)
                rpc_response = False
            if not isinstance(rpc_response, bool):
                logging.debug(rpc_response)
                break
        else:
            raise DucatuscoreInterfaceException("cannot get unspent with 10 attempts")

    return wrapper


class DucatuscoreInterface:
    def __init__(self):
        self.settings = config.NETWORKS.get("DUC")
        self.setup_endpoint()
        self.rpc = AuthServiceProxy(self.endpoint)
        self.check_connection()

    def setup_endpoint(self):
        self.endpoint = 'http://{user}:{pwd}@{host}:{port}'.format(
            user=self.settings.user,
            pwd=self.settings.password,
            host=self.settings.host,
            port=self.settings.port
        )
        return

    @retry_on_http_disconnection
    def check_connection(self):
        block = self.rpc.getblockcount()
        if block and block > 0:
            return True
        else:
            raise DucatuscoreInterfaceException('Ducatus node not connected')

    @retry_on_http_disconnection
    def get_wallet_balance(self) -> float:
        return self.rpc.getbalance('')
