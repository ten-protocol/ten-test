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

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        """Never check funds on a connection as hardhat has already has pre-funded. """
        return super().connect(test, private_key, web_socket, False, verbose)

    def connect_account1(self, test, web_socket=False, check_funds=True, verbose=True):
        """Override the account pk from all environment as we use the hardhat pks. """
        return self.connect(test, Properties().account1pk(key='hardhat'), web_socket, check_funds, verbose)

    def connect_account2(self, test, web_socket=False, check_funds=True, verbose=True):
        """Override the account pk from all environment as we use the hardhat pks. """
        return self.connect(test, Properties().account2pk(key='hardhat'), web_socket, check_funds, verbose)

    def connect_account3(self, test, web_socket=False, check_funds=True, verbose=True):
        """Override the account pk from all environment as we use the hardhat pks. """
        return self.connect(test, Properties().account3pk(key='hardhat'), web_socket, check_funds, verbose)

    def connect_account4(self, test, web_socket=False, check_funds=True, verbose=True):
        """Override the account pk from all environment as we use the hardhat pks. """
        return self.connect(test, Properties().account4pk(key='hardhat'), web_socket, check_funds, verbose)

