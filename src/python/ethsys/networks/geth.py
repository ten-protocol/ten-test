from web3 import Web3
from web3.middleware import geth_poa_middleware
from ethsys.networks.default import Default


class Geth(Default):
    """A Geth node giving access to the underlying network."""

    @classmethod
    def chain_id(cls): return 1337

    @classmethod
    def connection(cls, test, private_key, web_socket):
        port = cls.PORT if not web_socket else cls.WS_PORT
        host = cls.HOST if not web_socket else cls.WS_HOST

        test.log.info('Connecting to %s on %s:%d' % (cls.__name__, host, port))
        if not web_socket: web3 = Web3(Web3.HTTPProvider('%s:%d' % (host, port)))
        else: web3 = Web3(Web3.WebsocketProvider('%s:%d' % (host, port), websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.privateKeyToAccount(private_key)
        return web3, account
