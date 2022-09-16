from web3 import Web3
from ethsys.utils.properties import Properties
from ethsys.networks.default import Default


class Ropsten(Default):
    """A Ropsten node giving access to the underlying network."""
    HOST = 'https://ropsten.infura.io/v3'
    WS_HOST = 'wss://ropsten.infura.io/ws/v3'

    @classmethod
    def chain_id(cls): return 3

    @classmethod
    def connection(cls, test, private_key, web_socket):
        host = '%s/%s' % (cls.HOST if not web_socket else cls.WS_HOST, Properties().infuraProjectID())

        test.log.info('Connecting to network on %s' % host)
        if not web_socket: web3 = Web3(Web3.HTTPProvider(host))
        else: web3 = Web3(Web3.WebsocketProvider(host, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        return web3, account


