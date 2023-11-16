from ten.test.utils.properties import Properties
from ten.test.networks.default import DefaultPostLondon


class Sepolia(DefaultPostLondon):
    """A Sepolia connection giving access to the underlying network."""

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('sepolia')
        self.WS_HOST = props.host_ws('sepolia')
        self.PORT = props.port_http('sepolia')
        self.WS_PORT = props.port_ws('sepolia')
        self.CHAIN_ID = props.chain_id('sepolia')

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().sepoliaAPIKey())



