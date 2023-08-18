from obscuro.test.networks.default import Default
from obscuro.test.utils.properties import Properties


class Ganache(Default):
    """A Ganache connection giving access to the underlying network."""

    def __init__(self, test, name=None):
        super().__init__(test, name)
        props = Properties()
        self.HOST = props.host_http('ganache')
        self.WS_HOST = props.host_ws('ganache')
        self.PORT = props.port_http('ganache')
        self.WS_PORT = props.port_ws('ganache')
        self.CHAIN_ID = props.chain_id('ganache')
