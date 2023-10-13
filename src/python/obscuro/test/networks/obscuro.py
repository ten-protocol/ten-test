import requests, json
from web3 import Web3
from pysys.constants import BLOCKED
from obscuro.test.networks.default import DefaultPreLondon
from obscuro.test.networks.geth import Geth
from obscuro.test.networks.sepolia import Sepolia
from obscuro.test.utils.properties import Properties
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware
from obscuro.test.helpers.wallet_extension import WalletExtension


class ObscuroL1Sepolia(Sepolia):
    """The Obscuro L1 Sepolia implementation connection. """
    ETH_LIMIT = 0.01
    ETH_ALLOC = 0.002

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

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
        if verbose: test.log.info('Account %s connected to %s (%.6f ETH)', account.address, self.__class__.__name__, balance)

        if check_funds and balance < self.ETH_LIMIT:
            if verbose: test.log.info('Account balance is below threshold %s ... need to distribute funds', self.ETH_LIMIT)
            test.fund_native(self, account, self.ETH_ALLOC, Properties().l1_funded_account_pk(test.env), persist_nonce=False)
            if verbose:
                balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
                test.log.info('Account balance %.6f ETH', web3.fromWei(balance, 'ether'))
        return web3, account


class ObscuroL1Geth(Geth):
    """The Obscuro L1 Geth implementation connection. """
    ETH_LIMIT = 0.05
    ETH_ALLOC = 0.02

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.l1_host_http(test.env)
        self.WS_HOST = props.l1_host_ws(test.env)
        self.PORT = props.l1_port_http(test.env)
        self.WS_PORT = props.l1_port_ws(test.env)
        self.CHAIN_ID = props.chain_id(test.env)

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.privateKeyToAccount(private_key)
        balance_before = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
        if verbose: test.log.info('Account %s connected to %s (%.6f ETH)', account.address, self.__class__.__name__, balance_before)

        if check_funds and balance_before < self.ETH_LIMIT:
            if verbose: test.log.info('Account %s balance is below threshold %s ... need to distribute funds', account.address, self.ETH_LIMIT)
            test.fund_native(self, account, self.ETH_ALLOC, Properties().l1_funded_account_pk(test.env), persist_nonce=False)
            if verbose:
                balance_after = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
                test.log.info('Account %s balance is now %.6f ETH', account.address, web3.fromWei(balance_after, 'ether'))
        return web3, account


class Obscuro(DefaultPreLondon):
    """The L2 connection for Obscuro.

    An obscuro network instance requires a wallet extension (gateway) to connect to the network. A gateway can
    support multiple connections through it through joining as a particular user_id, under which multiple accounts
    can be registered. If a gateway instance is supplied in the constructor that instance will be used. If one is
    not supplied, if running against a local testnet an instance will be created; if running against a dev testnet,
    or testnet, then the hosted instance will be used. """
    ETH_LIMIT = 0.05
    ETH_ALLOC = 0.1
    CURRENCY = 'ETH'

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.CHAIN_ID = props.chain_id(test.env)

        if 'wallet' in kwargs:
            wallet = kwargs['wallet']
            self.name = wallet.name
            self.HOST = 'http://127.0.0.1'
            self.WS_HOST = 'ws://127.0.0.1'
            self.PORT = wallet.port
            self.WS_PORT = wallet.ws_port
        else:
            if test.is_local_obscuro():
                wallet = WalletExtension.start(test, name=name)
                self.name = name
                self.HOST = props.host_http(test.env)
                self.WS_HOST = props.host_ws(test.env)
                self.PORT = wallet.port
                self.WS_PORT = wallet.ws_port
            else:
                self.name = 'hosted'
                self.HOST = props.host_http(test.env)
                self.WS_HOST = props.host_ws(test.env)
                self.PORT = props.port_http(test.env)
                self.WS_PORT = props.port_ws(test.env)
                self.test.log.info('Using hosted wallet extension on port=%d, ws_port=%d', self.PORT, self.WS_PORT)

        self.ID = self.__join()
        if self.ID is None:
            test.addOutcome(BLOCKED, 'Error joining network for connection', abortOnError=True)

    def connection_url(self, web_socket=False):
        port = self.PORT if not web_socket else self.WS_PORT
        host = self.HOST if not web_socket else self.WS_HOST
        return '%s:%d/v1/?u=%s' % (host, port, self.ID)

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        self.__register(account)
        balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
        if verbose: test.log.info('Account %s connected to %s (%.6f ETH)', account.address, self.__class__.__name__, balance)

        if check_funds and balance < self.ETH_LIMIT:
            if verbose: test.log.info('Account balance is below threshold %s ... need to distribute funds', self.ETH_LIMIT)
            test.distribute_native(account, self.ETH_ALLOC)
            if verbose:
                balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
                test.log.info('Account balance %.6f ETH', web3.fromWei(balance, 'ether'))
        return web3, account

    def __join(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get('%s:%d/v1/join/' % (self.HOST, self.PORT),  headers=headers)
        if response.ok: return response.text.strip()
        return None

    def __register(self, account):
        text_to_sign = "Register " + self.ID + " for " + str(account.address).lower()
        eth_message = f"{text_to_sign}"
        encoded_message = encode_defunct(text=eth_message)
        signature = account.sign_message(encoded_message)

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"signature": signature['signature'].hex(), "message": text_to_sign}
        requests.post('%s:%d/v1/authenticate/?u=%s' % (self.HOST, self.PORT, self.ID),
                      data=json.dumps(data), headers=headers)



