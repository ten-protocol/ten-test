from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import DefaultPreLondon


class Arbitrum(DefaultPreLondon):
    """An Arbitrum connection giving access to the underlying network."""

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('arbitrum')
        self.WS_HOST = props.host_ws('arbitrum')
        self.PORT = props.port_http('arbitrum')
        self.WS_PORT = props.port_ws('arbitrum')
        self.CHAIN_ID = props.chain_id('arbitrum')

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().abitrumAPIKey())



