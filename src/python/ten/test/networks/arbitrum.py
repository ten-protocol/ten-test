from ten.test.utils.properties import Properties
from ten.test.networks.default import DefaultPreLondon


class ArbitrumSepolia(DefaultPreLondon):
    """An Arbitrum sepolia connection giving access to the underlying network."""
    ETH_LIMIT = 0.5
    ETH_ALLOC = 0.1
    ETH_ALLOC_EPHEMERAL = 0.001

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('arbitrum.sepolia')
        self.WS_HOST = props.host_ws('arbitrum.sepolia')
        self.PORT = props.port_http('arbitrum.sepolia')
        self.WS_PORT = props.port_ws('arbitrum.sepolia')
        self.CHAIN_ID = props.chain_id('arbitrum.sepolia')

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().arbitrumSepoliaAPIKey())