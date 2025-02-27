from web3 import Web3
from ten.test.utils.properties import Properties
from ten.test.networks.default import DefaultPreLondon
from ten.test.networks.sepolia import Sepolia


class ArbitrumL1Sepolia(Sepolia):
    """The Arbitrum L1 Sepolia implementation connection. """
    ETH_LIMIT = 0.02
    ETH_ALLOC = 0.05
    ETH_ALLOC_EPHEMERAL = 0.005

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.l1_host_http(test.env)
        self.WS_HOST = props.l1_host_ws(test.env)
        self.PORT = props.l1_port_http(test.env)
        self.WS_PORT = props.l1_port_ws(test.env)
        self.CHAIN_ID = props.chain_id(test.env)

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().sepoliaAPIKey())

    def connect(self, test, private_key, web_socket=False, check_funds=False, verbose=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.from_key(private_key)
        balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
        if verbose: self.log.info('Account %s connected to %s (%.9f ETH)', account.address, self.__class__.__name__, balance)
        return web3, account


class ArbitrumSepolia(DefaultPreLondon):
    """An Arbitrum sepolia connection giving access to the underlying network."""
    ETH_LIMIT = 0.02
    ETH_ALLOC = 0.05
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