from ten.test.utils.properties import Properties
from ten.test.networks.default import DefaultPostLondon


class Ethereum(DefaultPostLondon):
    """An Ethereum connection giving access to the underlying network."""
    ETH_LIMIT = 0.01
    ETH_ALLOC = 0.05

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('ethereum')
        self.WS_HOST = props.host_ws('ethereum')
        self.PORT = props.port_http('ethereum')
        self.WS_PORT = props.port_ws('ethereum')
        self.CHAIN_ID = props.chain_id('ethereum')
