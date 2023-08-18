from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default


class Goerli(Default):
    """A Goerli connection giving access to the underlying network."""

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().infuraProjectID())



