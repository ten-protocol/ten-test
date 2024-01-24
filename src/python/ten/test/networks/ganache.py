from ten.test.networks.default import DefaultPreLondon
from ten.test.utils.properties import Properties


class Ganache(DefaultPreLondon):
    """A Ganache connection giving access to the underlying network."""
    ETH_LIMIT = 0.05
    ETH_ALLOC = 0.1
    ETH_ALLOC_EPHEMERAL = 0.01

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('ganache')
        self.WS_HOST = props.host_ws('ganache')
        self.PORT = props.port_http('ganache')
        self.WS_PORT = props.port_ws('ganache')
        self.CHAIN_ID = props.chain_id('ganache')
