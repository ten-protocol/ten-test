from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default


class Goerli(Default):
    """A Goerli node giving access to the underlying network."""
    HOST = 'https://goerli.infura.io'
    WS_HOST = 'wss://goerli.infura.io/ws'
    VERSION = 'v3'
    ID = Properties().infuraProjectID()

    def chain_id(self): return 5


