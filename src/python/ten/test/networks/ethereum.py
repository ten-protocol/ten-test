import requests, json
from web3 import Web3
from ten.test.utils.properties import Properties
from ten.test.networks.default import DefaultPostLondon


class Ethereum(DefaultPostLondon):
    """An Ethereum connection giving access to the underlying network."""
    ETH_LIMIT = 0.002
    ETH_ALLOC = 0.005

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('ethereum')
        self.WS_HOST = props.host_ws('ethereum')
        self.PORT = props.port_http('ethereum')
        self.WS_PORT = props.port_ws('ethereum')
        self.CHAIN_ID = props.chain_id('ethereum')

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.from_key(private_key)
        balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
        if verbose: self.log.info('Account %s connected to %s (%.9f ETH)', account.address, self.__class__.__name__, balance)
        if check_funds: self.log.warn('Automatic funding of accounts not currently supported on an Ethereum node')
        return web3, account