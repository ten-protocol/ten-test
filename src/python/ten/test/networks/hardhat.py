from ten.test.networks.default import DefaultPreLondon
from ten.test.utils.properties import Properties


class Hardhat(DefaultPreLondon):
    """A Ganache connection giving access to the underlying network."""
    ETH_LIMIT = 0.05
    ETH_ALLOC = 0.1
    ETH_ALLOC_EPHEMERAL = 0.01

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('hardhat')
        self.WS_HOST = props.host_ws('hardhat')
        self.PORT = props.port_http('hardhat')
        self.WS_PORT = props.port_ws('hardhat')
        self.CHAIN_ID = props.chain_id('hardhat')


