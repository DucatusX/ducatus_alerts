from bitcoinrpc.authproxy import AuthServiceProxy
from settings import settings, NetworkSettings


class DucatuscoreInterfaceException(Exception):
    pass


class DucatuscoreInterface:
    def __init__(self):
        self.settings: NetworkSettings = [network for network in settings.NETWORKS if network.name == 'DUC'][0]
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

    def check_connection(self):
        block = self.rpc.getblockcount()
        if block and block > 0:
            return True
        else:
            raise DucatuscoreInterfaceException('Ducatus node not connected')
