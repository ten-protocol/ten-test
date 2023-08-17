from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default


class Arbitrum(Default):
    """An Arbitrum node giving access to the underlying network."""
    HOST = 'https://arb-goerli.g.alchemy.com'
    WS_HOST = 'wss://arb-goerli.g.alchemy.com'
    VERSION = 'v2'
    ID = Properties().abitrumAPIKey()

    def chain_id(self): return 421613


