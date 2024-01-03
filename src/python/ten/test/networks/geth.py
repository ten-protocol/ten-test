from web3 import Web3
from web3.middleware import geth_poa_middleware
from ten.test.networks.default import DefaultPreLondon


class Geth(DefaultPreLondon):
    """A Geth connection giving access to the underlying network."""

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        url = self.connection_url(web_socket)

        if verbose: test.log.info('Connecting to %s', self.__class__.__name__)
        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.from_key(private_key)
        return web3, account
