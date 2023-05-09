from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default


class Arbitrum(Default):
    """An Arbitrum node giving access to the underlying network."""
    HOST = 'https://arb-goerli.g.alchemy.com/v2'
    WS_HOST = 'wss://arb-goerli.g.alchemy.com/v2'

    def chain_id(self): return 421613

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().abitrumAPIKey())



