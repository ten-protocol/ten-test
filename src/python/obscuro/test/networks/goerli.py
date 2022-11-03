from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default


class Goerli(Default):
    """A Goerli node giving access to the underlying network."""
    HOST = 'https://goerli.infura.io/v3'
    WS_HOST = 'wss://goerli.infura.io/ws/v3'

    @classmethod
    def chain_id(cls): return 3

    @classmethod
    def connection_url(cls, web_socket=False):
        return '%s/%s' % (cls.HOST if not web_socket else cls.WS_HOST, Properties().infuraProjectID())



