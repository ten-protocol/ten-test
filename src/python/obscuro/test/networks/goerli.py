from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default


class Goerli(Default):
    """A Goerli connection giving access to the underlying network."""
    HOST = 'https://goerli.infura.io/v3'
    WS_HOST = 'wss://goerli.infura.io/ws/v3'

    def chain_id(self): return 5

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().infuraProjectID())



