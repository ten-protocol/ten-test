from web3 import Web3
from ethsys.utils.properties import Properties
from ethsys.networks.default import Default


class Ropsten(Default):
    """A Ropsten node giving access to the underlying network."""
    HOST = 'https://ropsten.infura.io/v3'
    WS_HOST = 'wss://ropsten.infura.io/v3'

    @classmethod
    def chain_id(cls): return 3

    @classmethod
    def connection(cls, test, private_key, web_socket):
        provider = Web3.HTTPProvider if not web_socket else Web3.WebsocketProvider
        host = '%s/%s' % (cls.HOST if not web_socket else cls.WS_HOST, Properties().infuraProjectID())

        test.log.info('Connecting to network on %s' % host)
        web3 = Web3(provider(host))
        account = web3.eth.account.privateKeyToAccount(private_key)
        return web3, account


