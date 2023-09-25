import requests, json
from web3 import Web3
from pysys.constants import BLOCKED
from obscuro.test.networks.default import Default
from obscuro.test.networks.geth import Geth
from obscuro.test.utils.properties import Properties
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware
from obscuro.test.helpers.wallet_extension import WalletExtension


class ObscuroL1(Geth):
    """The Obscuro L1 connection. """
    ETH_LIMIT = 1
    ETH_ALLOC = 0.2

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.l1_host_http(test.env)
        self.WS_HOST = props.l1_host_ws(test.env)
        self.PORT = props.l1_port_http(test.env)
        self.WS_PORT = props.l1_port_ws(test.env)
        self.CHAIN_ID = props.chain_id(test.env)

    def connect(self, test, private_key, web_socket=False, check_funds=True, log=True, **kwargs):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.privateKeyToAccount(private_key)
        if log: test.log.info('Account %s connected to %s on %s', account.address, self.__class__.__name__, url)

        if check_funds:
            balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
            if balance < self.ETH_LIMIT:
                if log: test.log.info('Account balance %.6f ETH below threshold %s', balance, self.ETH_LIMIT)
                test.fund_native(self, account, self.ETH_ALLOC, Properties().l1_funded_account_pk(test.env), persist_nonce=False)
            if log: test.log.info('Account balance %.6f ETH', web3.fromWei(web3.eth.get_balance(account.address), 'ether'))
        return web3, account


class Obscuro(Default):
    """The L2 connection for Obscuro.

    An obscuro network instance requires a wallet extension (gateway) to connect to the network. A gateway can
    support multiple connections through it through joining as a particular user_id, under which multiple accounts
    can be registered. If a gateway instance is supplied in the constructor that instance will be used. If one is
    not supplied, if running against a local testnet an instance will be created; if running against a dev testnet,
    or testnet, then the hosted instance will be used. """
    OBX_LIMIT = 0.5
    OBX_ALLOC = 1
    CURRENCY = 'OBX'

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.CHAIN_ID = props.chain_id(test.env)

        if 'wallet' in kwargs:
            wallet = kwargs['wallet']
            self.name = wallet.name
            test.log.info('Using supplied wallet for connection %s', name)
            self.HOST = 'http://127.0.0.1'
            self.WS_HOST = 'ws://127.0.0.1'
            self.PORT = wallet.port
            self.WS_PORT = wallet.ws_port
        else:
            if test.is_local_obscuro():
                wallet = WalletExtension.start(test, name=name)
                self.name = name
                self.HOST = 'http://127.0.0.1'
                self.WS_HOST = 'ws://127.0.0.1'
                self.PORT = wallet.port
                self.WS_PORT = wallet.ws_port
            else:
                self.name = 'hosted'
                url = Properties().gateway_url(test.env)
                self.HOST = url
                self.WS_HOST = url.replace('http','wss')
                self.PORT = props.gateway_port_http(test.env)
                self.WS_PORT = props.gateway_port_ws(test.env)

        test.log.info('Gateway http url is %s', self.WS_HOST)
        test.log.info('Gateway wss url  is %s', self.WS_HOST)

        self.ID = self.__join()
        if self.ID is None:
            test.addOutcome(BLOCKED, 'Error joining network for connection', abortOnError=True)
        else:
            test.log.info('Wallet %s has user id %s', self.name, self.ID)

    def connection_url(self, web_socket=False):
        port = self.PORT if not web_socket else self.WS_PORT
        host = self.HOST if not web_socket else self.WS_HOST
        return '%s:%d/v1/?u=%s' % (host, port, self.ID)

    def connect(self, test, private_key, web_socket=False, check_funds=True, log=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        self.__register(account)
        if log: test.log.info('Account %s connected to %s on %s', account.address, self.__class__.__name__, url)

        if check_funds:
            balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
            if balance < self.OBX_LIMIT:
                if log: test.log.info('Account balance %.6f OBX below threshold %s', balance, self.OBX_LIMIT)
                test.distribute_native(account, self.OBX_ALLOC)
            if log: test.log.info('Account balance %.6f OBX', web3.fromWei(web3.eth.get_balance(account.address), 'ether'))
        return web3, account

    def __join(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get('%s/v1/join/' % (self.HOST),  headers=headers)
        if response.ok: return response.text.strip()
        return None

    def __register(self, account):
        text_to_sign = "Register " + self.ID + " for " + str(account.address).lower()
        eth_message = f"{text_to_sign}"
        encoded_message = encode_defunct(text=eth_message)
        signature = account.sign_message(encoded_message)

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"signature": signature['signature'].hex(), "message": text_to_sign}
        requests.post('%s/v1/authenticate/?u=%s' % (self.HOST, self.ID),
                      data=json.dumps(data), headers=headers)



