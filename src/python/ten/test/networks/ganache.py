from ten.test.networks.default import DefaultPostLondon
from ten.test.utils.properties import Properties


class Ganache(DefaultPostLondon):
    """A Ganache connection giving access to the underlying network."""
    ETH_LIMIT = 0.005
    ETH_ALLOC = 0.01

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('ganache')
        self.WS_HOST = props.host_ws('ganache')
        self.PORT = props.port_http('ganache')
        self.WS_PORT = props.port_ws('ganache')
        self.CHAIN_ID = props.chain_id('ganache')
