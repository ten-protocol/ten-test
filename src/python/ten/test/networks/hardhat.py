from web3 import Web3
from ten.test.networks.default import DefaultPreLondon
from web3.middleware import geth_poa_middleware
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
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.from_key(private_key)
        balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
        if verbose: self.log.info('Account %s connected to %s (%.9f ETH)', account.address, self.__class__.__name__, balance)

        if check_funds and balance < self.ETH_LIMIT:
            if verbose: self.log.info('Account %s balance is below threshold %s ... need to distribute funds', account.address, self.ETH_LIMIT)
            test.fund_native(self, account, self.ETH_ALLOC, Properties().l1_funded_account_pk(test.env), persist_nonce=False)
            if verbose:
                balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
                self.log.info('Account %s balance is now %.9f ETH', account.address, balance)
        return web3, account

