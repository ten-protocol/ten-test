from web3 import Web3
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default


class Ropsten(Default):
    """A Ropsten node giving access to the underlying network."""
    HOST = 'https://ropsten.infura.io/v3'
    WS_HOST = 'wss://ropsten.infura.io/ws/v3'

    @classmethod
    def chain_id(cls): return 3

    @classmethod
    def connection_url(cls, web_socket=False):
        return '%s/%s' % (cls.HOST if not web_socket else cls.WS_HOST, Properties().infuraProjectID())



