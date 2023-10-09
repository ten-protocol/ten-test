from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import DefaultPostLondon


class Goerli(DefaultPostLondon):
    """A Goerli connection giving access to the underlying network."""

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('goerli')
        self.WS_HOST = props.host_ws('goerli')
        self.PORT = props.port_http('goerli')
        self.WS_PORT = props.port_ws('goerli')
        self.CHAIN_ID = props.chain_id('goerli')

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().infuraProjectID())



