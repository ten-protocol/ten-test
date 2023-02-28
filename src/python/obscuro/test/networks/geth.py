from web3 import Web3
from web3.middleware import geth_poa_middleware
from obscuro.test.networks.default import Default


class Geth(Default):
    """A Geth node giving access to the underlying network."""

    def chain_id(self): return 1337

    def connect(self, test, private_key, web_socket=False, check_funds=True):
        url = self.connection_url(web_socket)

        test.log.info('Connecting to %s on %s' % (self.__class__.__name__, url))
        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.privateKeyToAccount(private_key)
        return web3, account
